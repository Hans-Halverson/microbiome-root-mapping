rmdir /s /q build
rmdir /s /q dist

pyinstaller main.py ^
  --name="Microbiome Root Mapping" ^
  --onefile ^
  -w ^
  -i resources\icon.ico ^
  --add-data resources\Data_file_for_mapping.csv;resources ^
  --add-data resources\icon.png;resources