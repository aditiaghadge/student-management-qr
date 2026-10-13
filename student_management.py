"""
Student Management System with QR Code ID Cards
-----------------------------------------------
PBL-3 Micro Project | Python for Data Science (BE05000231)
Author : Aditi Abhijeet Ghadge (240090107042), Division A

Features
    1. Add student            5. Delete student
    2. View all students      6. Generate QR code ID card(s)   <- beyond syllabus
    3. Search student         7. Verify an ID card by scanning its QR code   <- beyond syllabus
    4. Update student         8. Exit

Data is stored in students.csv. ID cards are saved as PNG images in the id_cards folder.
"""

import csv
import json
import os

import qrcode                                   # beyond syllabus: QR code generation
from PIL import Image, ImageDraw, ImageFont     # used to draw the ID card

DATA_FILE = "students.csv"
CARD_FOLDER = "id_cards"
FIELDS = ["Roll No", "Name", "Branch", "Semester", "Email", "Phone", "CGPA"]
COLLEGE = "C. K. Pithawala College of Engineering & Technology"


# ------------------------------------------------------------------
# File handling
# ------------------------------------------------------------------
def load_students():
    """Read all students from the CSV file into a list of dictionaries."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_students(students):
    """Write the full list of students back to the CSV file."""
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(students)


def find_student(students, roll_no):
    for s in students:
        if s["Roll No"].lower() == roll_no.strip().lower():
            return s
    return None


# ------------------------------------------------------------------
# Input validation
# ------------------------------------------------------------------
def validate(student, students, editing=False):
    """Raise ValueError with a clear message if any field is wrong."""
    if not student["Roll No"].strip():
        raise ValueError("Roll No cannot be empty")
    if not editing and find_student(students, student["Roll No"]):
        raise ValueError(f"Roll No {student['Roll No']} already exists")
    if not student["Name"].replace(" ", "").isalpha():
        raise ValueError("Name should contain only letters")
    if not student["Semester"].isdigit() or not 1 <= int(student["Semester"]) <= 8:
        raise ValueError("Semester must be a number from 1 to 8")
    if "@" not in student["Email"] or "." not in student["Email"].split("@")[-1]:
        raise ValueError("Email is not valid")
    if not (student["Phone"].isdigit() and len(student["Phone"]) == 10):
        raise ValueError("Phone must have exactly 10 digits")
    cgpa = float(student["CGPA"])          # raises ValueError if not a number
    if not 0 <= cgpa <= 10:
        raise ValueError("CGPA must be between 0 and 10")


# ------------------------------------------------------------------
# CRUD operations
# ------------------------------------------------------------------
def add_student(students, student):
    validate(student, students)
    students.append(student)
    save_students(students)
    return student


def update_student(students, roll_no, changes):
    student = find_student(students, roll_no)
    if student is None:
        raise KeyError(f"No student with Roll No {roll_no}")
    updated = dict(student, **{k: v for k, v in changes.items() if v != ""})
    validate(updated, students, editing=True)
    student.update(updated)
    save_students(students)
    return student


def delete_student(students, roll_no):
    student = find_student(students, roll_no)
    if student is None:
        raise KeyError(f"No student with Roll No {roll_no}")
    students.remove(student)
    save_students(students)
    card = os.path.join(CARD_FOLDER, f"{student['Roll No']}.png")
    if os.path.exists(card):
        os.remove(card)
    return student


def search_students(students, text):
    text = text.strip().lower()
    return [s for s in students if text in s["Roll No"].lower() or text in s["Name"].lower()]


def print_table(rows):
    if not rows:
        print("No students found.")
        return
    widths = {f: max(len(f), *(len(str(r[f])) for r in rows)) for f in FIELDS}
    line = " | ".join(f.ljust(widths[f]) for f in FIELDS)
    print(line)
    print("-" * len(line))
    for r in rows:
        print(" | ".join(str(r[f]).ljust(widths[f]) for f in FIELDS))


# ------------------------------------------------------------------
# Beyond syllabus: QR code ID cards
# ------------------------------------------------------------------
def _font(size, bold=False):
    names = ["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_qr(student):
    """Create a QR code image that stores the student's key details as JSON text."""
    data = json.dumps({"roll": student["Roll No"], "name": student["Name"],
                       "branch": student["Branch"], "sem": student["Semester"]})
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def generate_id_card(student):
    """Draw an ID card (PNG) with the student's details and QR code."""
    os.makedirs(CARD_FOLDER, exist_ok=True)
    card = Image.new("RGB", (700, 420), "white")
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, 700, 80], fill="#1b4332")
    d.text((24, 16), COLLEGE, font=_font(20, True), fill="white")
    d.text((24, 48), "STUDENT IDENTITY CARD", font=_font(16), fill="#c7e9d5")

    # photo placeholder with initials
    d.rounded_rectangle([24, 105, 164, 265], 10, fill="#e8f0ea", outline="#1b4332", width=2)
    initials = "".join(w[0] for w in student["Name"].split()[:2]).upper()
    d.text((94, 185), initials, font=_font(44, True), fill="#1b4332", anchor="mm")

    y = 110
    for label in ["Name", "Roll No", "Branch", "Semester", "Email", "Phone"]:
        d.text((185, y), f"{label}:", font=_font(16, True), fill="#333333")
        d.text((285, y), str(student[label]), font=_font(16), fill="#111111")
        y += 30

    qr = make_qr(student).resize((170, 170))
    card.paste(qr, (505, 100))
    d.text((590, 280), "Scan to verify", font=_font(13), fill="#555555", anchor="mm")
    d.rectangle([0, 395, 700, 420], fill="#1b4332")
    d.text((350, 407), "Academic Year 2026-27", font=_font(13), fill="white", anchor="mm")

    path = os.path.join(CARD_FOLDER, f"{student['Roll No']}.png")
    card.save(path)
    return path


def verify_id_card(image_path, students):
    """Read the QR code from a card image and check it against the records."""
    try:
        import cv2                           # OpenCV is only needed for scanning
    except ImportError:
        raise RuntimeError("Scanning needs OpenCV: run  pip install opencv-python")
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(image_path))
    if not text:
        return "INVALID: no QR code could be read from this image"
    info = json.loads(text)
    student = find_student(students, info["roll"])
    if student and student["Name"] == info["name"]:
        return f"VALID: {student['Name']} ({student['Roll No']}), {student['Branch']}, Semester {student['Semester']}"
    return "INVALID: this card does not match any current student"


# ------------------------------------------------------------------
# Menu
# ------------------------------------------------------------------
def ask_student():
    return {f: input(f"{f}: ").strip() for f in FIELDS}


def main():
    students = load_students()
    while True:
        print("\n====== STUDENT MANAGEMENT SYSTEM ======")
        print("1. Add student          5. Delete student")
        print("2. View all students    6. Generate QR ID card(s)")
        print("3. Search student       7. Verify ID card (scan QR)")
        print("4. Update student       8. Exit")
        choice = input("Enter your choice (1-8): ").strip()
        try:
            if choice == "1":
                s = add_student(students, ask_student())
                print(f"Student {s['Name']} added successfully.")
            elif choice == "2":
                print_table(students)
            elif choice == "3":
                print_table(search_students(students, input("Enter Roll No or name: ")))
            elif choice == "4":
                roll = input("Roll No to update: ")
                print("Press Enter to keep the old value.")
                changes = {f: input(f"New {f}: ").strip() for f in FIELDS if f != "Roll No"}
                s = update_student(students, roll, changes)
                print(f"Student {s['Roll No']} updated.")
            elif choice == "5":
                s = delete_student(students, input("Roll No to delete: "))
                print(f"Student {s['Name']} deleted.")
            elif choice == "6":
                roll = input("Roll No (or 'all'): ").strip()
                targets = students if roll.lower() == "all" else [find_student(students, roll)]
                if None in targets:
                    raise KeyError(f"No student with Roll No {roll}")
                for s in targets:
                    print("ID card saved:", generate_id_card(s))
            elif choice == "7":
                print(verify_id_card(input("Path of ID card image: ").strip(), students))
            elif choice == "8":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 8.")
        except (ValueError, KeyError, FileNotFoundError, RuntimeError) as e:
            print("Error:", str(e).strip("'\""))


if __name__ == "__main__":
    main()
