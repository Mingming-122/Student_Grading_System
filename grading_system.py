"""
========================================================
  STUDENT GRADING AND GPA SYSTEM
  Language 1: Python (Procedural Computation Engine)
========================================================
"""
import json
import os

# ----------------------------------------------------------
# CONSTANTS: Grading Scale and Thresholds
# ----------------------------------------------------------

GRADE_SCALE = [
    (97, 100, 1.00, "A+"),
    (93,  96, 1.25, "A" ),
    (89,  92, 1.50, "A-"),
    (85,  88, 1.75, "B+"),
    (81,  84, 2.00, "B" ),
    (77,  80, 2.25, "B-"),
    (73,  76, 2.50, "C+"),
    (69,  72, 2.75, "C" ),
    (65,  68, 3.00, "D" ),
    ( 0,  64, 5.00, "F" ),
]

DL_THRESHOLD  = 1.75   # GPA <= 1.75  → Deans List
PASSED_THRESHOLD  = 3.00   # GPA <= 3.00  → Passed
# GPA > 3.00 or any 5.00 → Failed


# ----------------------------------------------------------
# PROCEDURAL FUNCTIONS
# ----------------------------------------------------------

def get_gpa_and_letter(numeric_grade):
    """Map a 0-100 numeric grade to a GPA point and letter grade."""
    for low, high, gpa, letter in GRADE_SCALE:
        if low <= numeric_grade <= high:
            return gpa, letter
    return 5.00, "F"   # safety fallback


def compute_weighted_average(subjects):
    
    total_units        = 0.0
    total_quality_pts  = 0.0
    subject_results    = []
    has_failing_subject = False

    for subj in subjects:   # Loop through each subject to compute quality points and GPA
        name  = subj["name"].strip()
        units = float(subj["units"])
        grade = float(subj["grade"])

        # Clamp grade between 0 and 100
        grade = max(0.0, min(100.0, grade))

        gpa_pt, letter = get_gpa_and_letter(grade)
        quality_pts    = gpa_pt * units          # quality points for this subject

        total_units       += units
        total_quality_pts += quality_pts

        if gpa_pt == 5.00:
            has_failing_subject = True

        subject_results.append({
            "name"        : name,
            "units"       : units,
            "numeric_grade": round(grade, 2),
            "gpa_point"   : gpa_pt,
            "letter_grade": letter,
            "quality_pts" : round(quality_pts, 4),
        })

    # Overall weighted GPA
    if total_units == 0:
        overall_gpa = 5.00
    else:
        overall_gpa = round(total_quality_pts / total_units, 4)

    # Overall letter grade
    _, overall_letter = get_gpa_and_letter(gpa_to_numeric(overall_gpa))

    # Academic standing
    if has_failing_subject or overall_gpa > PASSED_THRESHOLD:
        standing = "FAILED"
    elif overall_gpa <= DL_THRESHOLD:
        standing = "DEANS LIST"
    else:
        standing = "PASSED"

    return {
        "subjects"       : subject_results,
        "total_units"    : total_units,
        "total_quality_pts": round(total_quality_pts, 4),
        "overall_gpa"    : overall_gpa,
        "overall_letter" : overall_letter,
        "standing"       : standing,
    }


def gpa_to_numeric(gpa):
    """
    Reverse-map a GPA point back to the midpoint of its numeric range.
    Used only for deriving the overall letter grade from overall GPA.
    """
    reverse_map = {
        1.00: 98.5, 1.25: 94.5, 1.50: 90.5, 1.75: 86.5,
        2.00: 82.5, 2.25: 78.5, 2.50: 74.5, 2.75: 70.5,
        3.00: 66.5, 5.00: 32.0,
    }
    # Find the nearest GPA bracket
    closest = min(reverse_map.keys(), key=lambda k: abs(k - gpa))
    return reverse_map[closest]


def get_student_input():
    """Interactively collect student name, school year, and subject list."""
    print("=" * 56)
    print("   STUDENT GRADING AND GPA SYSTEM  —  Python Engine")
    print("=" * 56)

    student_name = input("\nStudent Name   : ").strip()
    school_year  = input("School Year    : ").strip()
    semester     = input("Semester       : ").strip()

    subjects = []
    print("\nEnter subject details (press Enter with blank name to finish):\n")
    print(f"{'#':<4} {'Subject Name':<30} {'Units':<8} {'Grade (0-100)'}")
    print("-" * 56)

    idx = 1
    while True:
        name = input(f"{idx:<4} Subject name  : ").strip()
        if not name:
            if len(subjects) == 0:
                print("  [!] Please enter at least one subject.")
                continue
            break

        # Validate units
        while True:
            try:
                units = float(input(f"     Units/Credits: "))
                if units <= 0:
                    raise ValueError
                break
            except ValueError:
                print("  [!] Enter a positive number for units.")

        # Validate grade
        while True:
            try:
                grade = float(input(f"     Numeric Grade: "))
                if not (0 <= grade <= 100):
                    raise ValueError
                break
            except ValueError:
                print("  [!] Grade must be between 0 and 100.")

        subjects.append({"name": name, "units": units, "grade": grade})
        idx += 1

    return student_name, school_year, semester, subjects


def display_results(student_name, school_year, semester, results):
    """Print a plain-text report card to the console."""
    print("\n")
    print("=" * 56)
    print("              GRADE COMPUTATION REPORT")
    print("=" * 56)
    print(f"  Student  : {student_name}")
    print(f"  Year     : {school_year}    Semester: {semester}")
    print("-" * 56)
    print(f"  {'Subject':<26} {'Units':>5}  {'Grade':>5}  {'GPA':>5}  {'LG':>3}")
    print("-" * 56)

    for s in results["subjects"]:
        print(f"  {s['name']:<26} {s['units']:>5.1f}  {s['numeric_grade']:>5.1f}  {s['gpa_point']:>5.2f}  {s['letter_grade']:>3}")

    print("-" * 56)
    print(f"  {'TOTAL UNITS':<26} {results['total_units']:>5.1f}")
    print(f"  {'TOTAL QUALITY POINTS':<26} {results['total_quality_pts']:>5.2f}")
    print(f"  {'OVERALL GPA':<26} {results['overall_gpa']:>5.2f}")
    print(f"  {'LETTER GRADE':<26} {results['overall_letter']:>5}")
    print(f"  {'ACADEMIC STANDING':<26} {results['standing']:>5}")
    print("=" * 56)


def save_to_json(student_name, school_year, semester, results, filepath="report_data.json"):
    """Serialize all computed results to JSON for the JS dashboard."""
    payload = {
        "student_name": student_name,
        "school_year" : school_year,
        "semester"    : semester,
        "results"     : results,
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"\n  [OK] Report saved to: {output_path}")
    print("       Open 'report_card.html' in your browser to view the dashboard.\n")
    return output_path


# ----------------------------------------------------------
# MAIN ENTRY POINT
# ----------------------------------------------------------

def main():
    student_name, school_year, semester, subjects = get_student_input()
    results = compute_weighted_average(subjects)
    display_results(student_name, school_year, semester, results)
    save_to_json(student_name, school_year, semester, results)


if __name__ == "__main__":
    main()
