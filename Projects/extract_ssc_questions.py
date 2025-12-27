import os
import csv
import re
from PyPDF2 import PdfReader

# =============================
# CONFIGURATION
# =============================
FOLDER_PATH = r"D:\YoutubePoster\input\ssc_papers"
OUTPUT_CSV = "Extracted_Questions.csv"
PROBLEM_LOG = "problematic_pdfs.txt"

SECTION_MAP = {
    "1": "General Intelligence and Reasoning",
    "2": "General Awareness",
    "3": "Quantitative Aptitude",
    "4": "English Comprehension"
}

# =============================
# USER INPUT
# =============================
print("\nSelect Section to Extract:")
print("1: General Intelligence and Reasoning")
print("2: General Awareness (Default)")
print("3: Quantitative Aptitude")
print("4: English Comprehension")

choice = input("Enter your choice (1/2/3/4): ").strip()
SECTION_NAME = SECTION_MAP.get(choice, "General Awareness")

print(f"\n✅ Extracting Section: {SECTION_NAME}\n")

# =============================
# UTILITY FUNCTIONS
# =============================
def clean(text: str) -> str:
    if not text:
        return ""
    return (
        text.replace("✓", "")
            .replace("✔", "")
            .replace("\n", " ")
            .replace("\r", " ")
            .strip()
    )

def get_answer(options, index):
    try:
        return options[index - 1]
    except:
        return ""

# =============================
# CSV INITIALIZATION
# =============================
csv_exists = os.path.exists(OUTPUT_CSV)

with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)

    if not csv_exists:
        writer.writerow([
            "Paper Name",
            "Section",
            "Question",
            "Option A",
            "Option B",
            "Option C",
            "Option D",
            "Correct Answer"
        ])

    # =============================
    # PROCESS PDFs
    # =============================
    for file_name in os.listdir(FOLDER_PATH):
        if not file_name.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(FOLDER_PATH, file_name)
        print(f"📄 Processing: {file_name}")

        try:
            reader = PdfReader(pdf_path)
            full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            print(f"❌ Failed to read {file_name}: {e}")
            with open(PROBLEM_LOG, "a", encoding="utf-8") as log:
                log.write(file_name + " (read error)\n")
            continue

        if not full_text.strip():
            print(f"⚠️ No extractable text: {file_name}")
            with open(PROBLEM_LOG, "a", encoding="utf-8") as log:
                log.write(file_name + " (empty text)\n")
            continue

        # =============================
        # FIND SECTION BLOCK
        # =============================
        section_blocks = re.split(r"Section\s*:\s*", full_text, flags=re.IGNORECASE)
        section_text = ""

        for block in section_blocks:
            if block.strip().lower().startswith(SECTION_NAME.lower()):
                section_text = block
                break

        if not section_text:
            print(f"❌ Section not found in {file_name}")
            continue

        # =============================
        # EXTRACT QUESTIONS
        # =============================
        question_blocks = re.split(r"\bQ\.\s*\d+\b", section_text)
        question_blocks = [q.strip() for q in question_blocks if q.strip()]

        answer_keys = re.findall(r"Chosen Option\s*:\s*(\d)", section_text)

        for i, block in enumerate(question_blocks):
            question_text = ""
            options = ["", "", "", ""]

            lines = block.splitlines()
            for line in lines:
                opt_match = re.match(r"\s*(\d)\.\s*(.+)", line)
                if opt_match:
                    idx = int(opt_match.group(1))
                    if 1 <= idx <= 4:
                        options[idx - 1] = clean(opt_match.group(2))
                elif "Chosen Option" not in line and "Ans" not in line:
                    question_text += " " + line.strip()

            correct_index = int(answer_keys[i]) if i < len(answer_keys) else 0
            correct_answer = get_answer(options, correct_index)

            writer.writerow([
                file_name,
                SECTION_NAME,
                clean(question_text),
                *options,
                clean(correct_answer)
            ])

print("\n✅ DONE!")
print(f"📁 Output CSV: {OUTPUT_CSV}")
print(f"⚠️ Problematic PDFs logged in: {PROBLEM_LOG}")
