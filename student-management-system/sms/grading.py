"""Marks -> grade -> grade points, and CGPA calculation."""

# (minimum marks, grade, points) - highest first
SCALE = [(90, "S", 10), (80, "A", 9), (70, "B", 8),
         (60, "C", 7), (50, "D", 6), (40, "E", 5), (0, "F", 0)]

ATTENDANCE_MIN = 75.0   # percent


def grade_for(marks: float):
    """Return (grade, points) for the given marks."""
    for low, grade, points in SCALE:
        if marks >= low:
            return grade, points
    return "F", 0


def cgpa(courses):
    """courses: iterable of (credits, points). Returns CGPA rounded to 2 dp."""
    total_credits = sum(c for c, _ in courses)
    if total_credits == 0:
        return 0.0
    return round(sum(c * p for c, p in courses) / total_credits, 2)
