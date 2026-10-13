# Student Management System with QR Code ID Cards

**PBL-3 Micro Project** | Python for Data Science (BE05000231)
Aditi Abhijeet Ghadge | 240090107042 | Division A
C. K. Pithawala College of Engineering and Technology, Surat

A menu-driven Python program to manage student records, extended with a **beyond-syllabus** feature:
every student gets a **QR code ID card**, and any card can be **verified by scanning its QR code**.

![Sample ID card](id_cards/CE101.png)

## Features

| No. | Feature | Details |
|---|---|---|
| 1 | Add student | Roll No, Name, Branch, Semester, Email, Phone, CGPA, with input checks |
| 2 | View all students | Neatly aligned table |
| 3 | Search student | By Roll No or part of the name |
| 4 | Update student | Press Enter to keep an old value |
| 5 | Delete student | Also removes that student's ID card |
| 6 | **Generate QR ID card** | One student or all; saved as PNG in `id_cards/` |
| 7 | **Verify ID card** | Reads the QR code from a card image and checks it against the records |
| 8 | Exit | |

Records are stored in `students.csv`, so they are kept after the program closes.

## Beyond syllabus: QR codes

A QR (Quick Response) code is a 2-D barcode that stores text. The program stores each student's
roll number, name, branch and semester in the QR code as JSON text using the `qrcode` library, and
draws a complete ID card with `Pillow`. For verification, `OpenCV`'s `QRCodeDetector` reads the QR
code back from the image and the program checks that the student still exists in the records.

## Input checks

- Roll No must be unique
- Name must contain only letters
- Semester must be 1 to 8
- Email must contain `@` and a domain
- Phone must be exactly 10 digits
- CGPA must be between 0 and 10

Wrong input shows a clear error message instead of crashing the program.

## How to run

```
pip install qrcode pillow opencv-python
python student_management.py
```

## Files

| File | Purpose |
|---|---|
| `student_management.py` | The complete program |
| `students.csv` | Sample student records |
| `id_cards/` | Generated ID cards |
| `requirements.txt` | Libraries needed |
