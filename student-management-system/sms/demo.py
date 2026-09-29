"""Sample data so the project can be demonstrated immediately."""
from datetime import date, timedelta

from .errors import DuplicateError
from .services import StudentManager

STUDENTS = [
    ("24BCE1001", "Aarav Sharma", "aarav@example.com", "9876500001", "CSE", 2),
    ("24BCE1002", "Diya Patel", "diya@example.com", "9876500002", "CSE", 2),
    ("24BEC1003", "Rohan Verma", "rohan@example.com", "9876500003", "ECE", 2),
    ("24BME1004", "Ananya Iyer", "ananya@example.com", "9876500004", "MECH", 2),
    ("24BCE1005", "Karthik Nair", "karthik@example.com", "9876500005", "CSE", 2),
]
COURSES = [("CSE1001", "Problem Solving with Python", 4), ("MAT1001", "Calculus", 4),
           ("PHY1001", "Engineering Physics", 3), ("ENG1001", "Technical English", 2)]
MARKS = {"24BCE1001": [92, 85, 78, 88], "24BCE1002": [95, 91, 89, 93],
         "24BEC1003": [66, 58, 72, 61], "24BME1004": [45, 52, 38, 70],
         "24BCE1005": [81, 74, 69, 77]}
# fraction of 20 classes attended per student
ATTEND = {"24BCE1001": 19, "24BCE1002": 20, "24BEC1003": 16, "24BME1004": 13, "24BCE1005": 17}


def seed(mgr: StudentManager) -> bool:
    """Insert sample data. Returns False if the database already has students."""
    if mgr.list_students():
        return False
    for s in STUDENTS:
        mgr.add_student(*s)
    for c in COURSES:
        try:
            mgr.add_course(*c)
        except DuplicateError:
            pass
    start = date(2026, 8, 3)
    for reg, marks in MARKS.items():
        for (code, _, _), m in zip(COURSES, marks):
            mgr.enroll(reg, code)
            mgr.record_marks(reg, code, m)
        for i in range(20):
            day = (start + timedelta(days=i)).isoformat()
            mgr.mark_attendance(reg, "CSE1001", day, i < ATTEND[reg])
    return True
