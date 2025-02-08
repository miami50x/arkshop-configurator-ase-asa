#!/usr/bin/env python3
import os
import json
import requests
from urllib.parse import urlparse

def download_image(image_url, local_path):
    """
    Download an image from image_url and save it to local_path.
    """
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {local_path}")
        else:
            print(f"Failed to download {image_url} (status code {response.status_code})")
    except Exception as e:
        print(f"Error downloading {image_url}: {e}")

def main():
    # File and folder names
    input_json = "ark_data.json"
    output_json = "ark_ase_asa_blueprints.json"
    image_folder = "ark_assets_img"

    # Ensure the image folder exists
    os.makedirs(image_folder, exist_ok=True)

    # Load the original JSON data.
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process each record.
    processed_data = []
    for record in data:
        # Each record is a dict with a single key.
        for key, value in record.items():
            image_url = value.get("image", "")
            if image_url:
                # Extract the filename from the URL.
                parsed = urlparse(image_url)
                filename = os.path.basename(parsed.path)
                local_image_path = os.path.join(image_folder, filename)
                
                # Download the image if it does not already exist.
                if not os.path.exists(local_image_path):
                    download_image(image_url, local_image_path)
                else:
                    print(f"Image already exists: {local_image_path}")

                # Update the image field to point to the local file.
                value["image"] = os.path.join(image_folder, filename)

            # Remove the 'url' field from the record.
            if "url" in value:
                del value["url"]

            processed_data.append({key: value})

    # Sort the records alphabetically by the key.
    processed_data.sort(key=lambda rec: list(rec.keys())[0].lower())

    # Write out the processed JSON to a new file.
    with open(output_json, 'w', encoding='utf-8') as out_f:
        json.dump(processed_data, out_f, indent=4)
    
    print(f"Processed data saved to {output_json}")

if __name__ == '__main__':
    main()
