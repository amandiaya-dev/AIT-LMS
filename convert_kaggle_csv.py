"""
AIT LMS - Kaggle Dataset Converter
====================================
Run this script to convert a downloaded Kaggle student dataset
into the format required by the AIT LMS student registry.

Usage:
    python convert_kaggle_csv.py your_kaggle_file.csv

The output file 'ait_student_registry.csv' will be ready to upload
directly to the LMS at /accounts/import-students/
"""

import csv
import sys
import os
import random


def detect_columns(headers):
    """
    Automatically detects which column in the CSV file corresponds
    to which field we need, regardless of what the column is called.
    Works with any Kaggle student dataset.
    """
    headers_lower = [h.lower().strip() for h in headers]

    def find(options):
        for opt in options:
            for i, h in enumerate(headers_lower):
                if opt in h:
                    return i
        return None

    return {
        "id":         find(["studentid", "student_id", "id", "rollno", "roll_no", "regno", "reg_no"]),
        "name":       find(["name", "fullname", "full_name", "studentname"]),
        "first_name": find(["firstname", "first_name", "fname"]),
        "last_name":  find(["lastname", "last_name", "lname", "surname"]),
        "department": find(["department", "dept", "faculty", "major", "program", "course"]),
        "semester":   find(["semester", "sem", "year", "level", "grade", "class"]),
        "gender":     find(["gender", "sex"]),
    }


DEPARTMENTS = [
    "Computer Science",
    "Engineering",
    "Business Administration",
    "Information Technology",
    "Mathematics",
    "Physics",
    "Education",
    "Health Sciences",
]


def get_semester(row, col_map, headers):
    """Extract or estimate semester from the row."""
    if col_map["semester"] is not None:
        raw = row[col_map["semester"]].strip()
        # Try to extract a number 1-8 from whatever is in that column
        digits = ''.join(filter(str.isdigit, raw))
        if digits:
            sem = int(digits[0])  # take the first digit
            return max(1, min(8, sem))  # clamp between 1 and 8
    # If no semester column, assign randomly
    return random.randint(1, 8)


def get_department(row, col_map):
    """Extract or assign department."""
    if col_map["department"] is not None:
        dept = row[col_map["department"]].strip()
        if dept:
            return dept
    return random.choice(DEPARTMENTS)


def get_name_parts(row, col_map):
    """Extract first and last name from the row."""
    first = ""
    last = ""

    if col_map["first_name"] is not None:
        first = row[col_map["first_name"]].strip()
    if col_map["last_name"] is not None:
        last = row[col_map["last_name"]].strip()

    # If no separate columns but there's a full name column
    if not first and col_map["name"] is not None:
        full = row[col_map["name"]].strip()
        parts = full.split()
        if len(parts) >= 2:
            first = parts[0]
            last = " ".join(parts[1:])
        elif len(parts) == 1:
            first = parts[0]
            last = "Student"

    if not first:
        first = "Student"
    if not last:
        last = "Unknown"

    return first, last


def convert(input_file):
    output_file = "ait_student_registry.csv"

    print(f"\n Reading: {input_file}")

    with open(input_file, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    print(f" Found {len(rows)} rows")
    print(f" Columns detected: {headers}")

    col_map = detect_columns(headers)
    print(f"\n Column mapping:")
    for key, idx in col_map.items():
        print(f"   {key:12} → {headers[idx] if idx is not None else '(not found — will be generated)'}")

    converted = []
    skipped = 0

    for i, row in enumerate(rows, start=1):
        if not any(cell.strip() for cell in row):
            skipped += 1
            continue

        # Generate student ID in AIT format if no ID column found
        if col_map["id"] is not None:
            raw_id = row[col_map["id"]].strip()
            # Clean it up and format as AIT ID
            digits = ''.join(filter(str.isdigit, raw_id))
            if not digits:
                skipped += 1
                continue
            student_id = f"AIT/2024/{digits.zfill(4)}"
        else:
            student_id = f"AIT/2024/{str(i).zfill(4)}"

        first_name, last_name = get_name_parts(row, col_map)
        department = get_department(row, col_map)
        semester = get_semester(row, col_map, headers)

        converted.append({
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "department": department,
            "semester": semester,
            "status": "active",
        })

    with open(output_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "student_id", "first_name", "last_name", "department", "semester", "status"
        ])
        writer.writeheader()
        writer.writerows(converted)

    print(f"\n Done!")
    print(f"   {len(converted)} students converted")
    print(f"   {skipped} rows skipped (empty/invalid)")
    print(f"\n Output file: {output_file}")
    print(f" Upload this file at: http://127.0.0.1:8000/accounts/import-students/\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python convert_kaggle_csv.py your_kaggle_file.csv\n")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"\nFile not found: {input_file}\n")
        sys.exit(1)

    convert(input_file)
