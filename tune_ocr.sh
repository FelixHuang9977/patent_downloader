.venv/bin/python3 img_ocr.py > sbios_text.txt
cat sbios_text.txt | sed -e '/NVIDIA CONFIDENTIAL/{N;N;d}' -e '/DG-11194-001_1.0/d' -e '/^[ ]*$/d' -e 's/[^[:print:]\t]//g' > sbios_text_tune.txt

echo "RUN AI prompt:"
exit 0
Read through the entire file and identify all lines that start with 'SBIOS-'

For each matching line, extract and format two specific fields:

First field: The SBIOS ID (e.g., 'SBIOS-CORE-010', 'SBIOS-SEC-001')
Second field: The description that follows the ID
Format the output so that:

Each SBIOS entry is on a new line
The ID and description are on the same line, separated by a colon
The format should be: 'SBIOS-ID: Description'
Maintain the exact text of both the ID and description as they appear in the original file
