import os
from PyPDF2 import PdfMerger

# 📂 Input Folder Path
folder_path = r"D:\YoutubePoster\input\msth_question"  # <-- Change this to your folder

# 📄 Output File Path
output_pdf = r"Merged_Output.pdf"

# 📦 Initialize Merger
merger = PdfMerger()

# 📑 List and Merge PDFs
pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
pdf_files.sort()  # Optional: Sort alphabetically

for pdf_file in pdf_files:
    file_path = os.path.join(folder_path, pdf_file)
    print(f"Adding: {pdf_file}")
    merger.append(file_path)

# 💾 Save Merged PDF
merger.write(output_pdf)
merger.close()

print(f"\n✅ All PDFs merged successfully into: {output_pdf}")
