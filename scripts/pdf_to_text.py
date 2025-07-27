import fitz  # PyMuPDF

def pdf_to_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()

    doc.close()
    return text

# Example usage
pdf_path = "sample.pdf"  # Replace with your PDF file
output_text = pdf_to_text(pdf_path)

# Save to text file (optional)
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(output_text)

print("✅ Text extraction completed.")
