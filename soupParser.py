#!/usr/bin/env python3
import os
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def extract_slug(url):
    """Extract the last part of the URL path (page slug)."""
    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')
    return parts[-1] if parts else url

def get_availability_flags(soup):
    """
    Scan the page's images for green tick indicators and check their alt text.
    Return a tuple: (ase, asa) where each is True if a green tick is found 
    for that platform.
    """
    ase = False
    asa = False
    for img in soup.find_all('img', alt=True, src=True):
        src = img['src'].lower()
        alt = img['alt'].lower()
        if 'clip-green-tick-mark' in src:
            if 'ase' in alt:
                ase = True
            if 'asa' in alt:
                asa = True
    return ase, asa

def parse_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    # Get the canonical URL if available; otherwise, use the file path.
    canonical_tag = soup.find('link', rel='canonical')
    url = canonical_tag['href'] if canonical_tag and canonical_tag.has_attr('href') else file_path

    # Get the page title from an <h1> with class "withsep"
    title_tag = soup.find('h1', class_='withsep')
    title = title_tag.get_text(strip=True) if title_tag else ''

    # Grab the first image from a figure with class "wp-block-image"
    image_src = ''
    figure = soup.find('figure', class_='wp-block-image')
    if figure:
        img = figure.find('img')
        if img and img.has_attr('src'):
            image_src = img['src']

    # Determine availability flags using our helper function.
    ase, asa = get_availability_flags(soup)

    # Helper to extract a cheat code command from a section.
    # Looks for an element with the given anchor id, then the next container that includes a <copier> tag.
    def extract_command(anchor_id):
        anchor = soup.find(id=anchor_id)
        if anchor:
            # Look for the next container with a class that includes "container-section"
            container = anchor.find_next(lambda tag: tag.name == "div" and "container-section" in tag.get("class", []))
            if container:
                copier = container.find("copier")
                if copier:
                    return " ".join(copier.stripped_strings)
        return ""

    # Extract the various cheat code commands from their sections.
    shortest_gfi   = extract_command("anchorshortgfi")
    full_gfi       = extract_command("anchorlonggfi")
    giveitem       = extract_command("anchorgiveitem")
    unlock_engram  = extract_command("anchorunlockengram")
    blueprint_path = extract_command("anchorblueprint")
    item_id        = extract_command("anchoritemid")
    item_id_number = extract_command("anchoritemidnumber")

    return {
        "url": url,
        "title": title,
        "image": image_src,
        "ase": ase,
        "asa": asa,
        # "shortest_gfi": shortest_gfi,
        "gfi": full_gfi,
        # "giveitem": giveitem,
        # "unlock_engram": unlock_engram,
        "blueprint_path": blueprint_path,
        "item_id": item_id,
        "item_id_number": item_id_number
    }

def main():
    scraped_dir = "scraped/"
    all_data = {}
    
    # Loop through all .html files in the scraped directory.
    for filename in os.listdir(scraped_dir):
        if filename.endswith(".html"):
            file_path = os.path.join(scraped_dir, filename)
            data = parse_file(file_path)
            # Skip this file if both 'asa' and 'ase' are false.
            if not data.get("asa") and not data.get("ase"):
                continue
            # Extract the slug from the URL to use as the key.
            key = extract_slug(data.get("url", filename))
            all_data[key] = data
            print(f"Processed: {key}")
    
    output_file = "ark_data.json"
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("[\n")
        first = True
        for key, data in all_data.items():
            record = { key: data }
            if not first:
                out.write(",\n")
            out.write(json.dumps(record, separators=(',', ':')))
            first = False
        out.write("\n]")

    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
