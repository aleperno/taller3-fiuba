#!/bin/bash


ZIP_URL="$1"
FOLDER_PATH="$2"

# Check if the number of arguments is correct
if [ "$#" -ne 2 ]; then
    echo "Error: The number of arguments should be 2."
    exit 1
fi

#echo "La url del zip es $ZIP_URL"

cd "$FOLDER_PATH"

curl -O "$ZIP_URL" > /dev/null 2>&1

# Step 1: Look for a .zip file in the current directory
zip_file=$(find . -maxdepth 1 -type f -name '*.zip')

# Check if there's exactly one .zip file
if [ $(echo "$zip_file" | wc -l) -ne 1 ]; then
    #echo "Error: There should be exactly one '.zip' file in the current directory."
    exit 1
fi

# Unzip the .zip file
unzip "$zip_file" 2>&1 > /dev/null

# Step 2: Look for a directory in the current directory
directory=$(find . -maxdepth 1 -type d ! -name '.')

# Check if there's exactly one directory
if [ $(echo "$directory" | wc -l) -ne 1 ]; then
    echo "Error: There should be exactly one directory in the current directory."
    exit 1
fi

# Change directory to the found directory
cd "$directory"

# Step 3: Look for a .tex file in the current directory
tex_file=$(find . -maxdepth 1 -type f -name '*.tex')

# Check if there's exactly one .tex file
if [ $(echo "$tex_file" | wc -l) -ne 1 ]; then
    echo "Error: There should be exactly one '.tex' file in the current directory."
    exit 1
fi

# Run pdflatex with the .tex file
pdflatex -interaction=nonstopmode "$tex_file" > /dev/null 2>&1

pdf_file=$(find . -maxdepth 1 -type f -name '*.pdf')


echo "$FOLDER_PATH/${directory#./}/${pdf_file#./}"
