import os
import csv
import re
from PyPDF2 import PdfReader

folder_path = r"D:\YoutubePoster\input\ssc_papers"
output_csv = "Extracted_Questions.csv"
problem_log = "problematic_pdfs.txt"

section_map = {
    "1": "General Intelligence and Reasoning",
    "2": "General Awareness",
    "3": "Quantitative Aptitude",
    "4": "English Comprehension"
}

# ==== Ask User ====
print("Select Section to Extract:")
print("1: General Intelligence and Reasoning")
print("2: General Awareness (Default)")
print("3: Quantitative Aptitude")
print("4: English Comprehension")
choice = input("Enter your choice (1/2/3/4): ").strip()
section = section_map.get(choice, "General Awareness")
print(f"\n✅ Extracting section: {section}\n")

# ==== Utility Functions ====
def clean(text):
    return text.replace("✓", "").replace("✔", "").replace("\n", " ").strip()

def get_answer_from_index(options, chosen_index):
    try:
        return clean(options[chosen_index - 1])
    except:
        return ""

# ==== CSV Initialization ====
file_exists = os.path.exists(output_csv)
with open(output_csv, "a", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["Paper Name", "Section", "Question", "Option 1", "Option 2", "Option 3", "Option 4", "Answer"])

    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".pdf"):
            continue

        file_path = os.path.join(folder_path, file_name)
        try:
            reader = PdfReader(file_path)
            full_text = "\n".join([page.extract_text() or "" for page in reader.pages])
        except Exception as e:
            print(f"❌ Skipping '{file_name}' due to read error: {e}")
            with open(problem_log, "a", encoding="utf-8") as log_file:
                log_file.write(file_name + "\n")
            continue

        if not full_text.strip():
            print(f"⚠️ No text extracted from '{file_name}' (possibly scanned images). Skipping.")
            with open(problem_log, "a", encoding="utf-8") as log_file:
                log_file.write(file_name + " (empty text)\n")
            continue

        # Split by section
        section_blocks = re.split(r"Section\s*:\s*", full_text)
        for block in section_blocks:
            if block.startswith(section):
                section_text = block
                break
        else:
            print(f"❌ Section '{section}' not found in {file_name}")
            continue

        # Extract Questions
        q_blocks = re.split(r"Q\.\d+", section_text)
        questions = [q.strip() for q in q_blocks if q.strip()]
        answer_blocks = re.findall(r"Chosen Option\s*:\s*(\d+)", section_text)

        i = 0
        for question in questions:
            lines = question.splitlines()
            q_text = ""
            options = ["", "", "", ""]
            for line in lines:
                match = re.match(r"\s*(\d)\.\s*(.*)", line)
                if match:
                    idx, opt = int(match.group(1)), match.group(2)
                    if 1 <= idx <= 4:
                        options[idx - 1] = clean(opt)
                        continue
                if "Ans" not in line:
                    q_text += " " + line.strip()

            chosen = int(answer_blocks[i]) if i < len(answer_blocks) else 0
            correct_ans = get_answer_from_index(options, chosen)

            writer.writerow([file_name, section, clean(q_text), *options, correct_ans])
            i += 1

print(f"\n✅ DONE: Questions with correct answers extracted to '{output_csv}'")
print(f"⚠️ Problematic files (if any) logged in '{problem_log}'")
