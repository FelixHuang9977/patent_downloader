.venv/bin/python3 img_ocr.py > sbios_text.txt
cat sbios_text.txt | sed -e '/NVIDIA CONFIDENTIAL/{N;N;d}' -e '/DG-11194-001_1.0/d' -e '/^[ ]*$/d' -e 's/[^[:print:]\t]//g' > sbios_text_tune.txt