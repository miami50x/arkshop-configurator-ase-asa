#!/bin/bash
# Usage: ./codeblock_cat.sh file1 [file2 file3 ...]

# Check if at least one file is provided.
if [ "$#" -eq 0 ]; then
  echo "Usage: $0 file1 [file2 ...]"
  exit 1
fi

# Loop through each file passed as an argument.
for file in "$@"; do
  if [[ -f "$file" ]]; then
    # Print a header with the filename
    echo "### $file"
    # Start a Markdown code block with escaped backticks
    echo -e "\`\`\`"
    # Output the file content
    # echo -n -e "\n"
    cat "$file"
    echo -n -e "\n"
    # End the Markdown code block with escaped backticks
    echo -e "\`\`\`"
    # Print an empty line for readability
    echo ""
  else
    echo "Error: File '$file' not found."
  fi
done
