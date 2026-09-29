"""Menu-driven command line interface."""
from datetime import date

from .errors import SMSError
from .services import StudentManager

MENU = """
========== STUDENT MANAGEMENT SYSTEM ==========
 1. Add student            8. Enroll student in course
 2. View student           9. Enter marks
 3. Update student        10. Mark attendance
 4. Delete student        11. Transcript (grades + CGPA)
 5. List / search         12. Attendance report
 6. Add course            13. Rank list (top CGPA)
 7. List courses          14. Export students to CSV
 0. Exit
"""


def ask(label: str) -> str:
    return input(f"  {label}: ").strip()


def table(rows, cols):
    if not rows:
        print("  (no records)")
        return
    widths = [max(len(c), *(len(str(r[c])) for r in rows)) for c in cols]
    line = "  " + " | ".join(c.upper().ljust(w) for c, w in zip(cols, widths))
    print(line)
    print("  " + "-+-".join("-" * w for w in widths))
    for r in rows:
        print("  " + " | ".join(str(r[c]).ljust(w) for c, w in zip(cols, widths)))


def show_transcript(t):
    s = t["student"]
    print(f"\n  {s['name']} ({s['reg_no']}) - {s['department']}, Year {s['year']}")
    rows = [{**c, "points": "-" if c["points"] is None else c["points"],
             "marks": "-" if c["marks"] is None else c["marks"]} for c in t["courses"]]
    table(rows, ["code", "title", "credits", "marks", "grade", "points"])
    print(f"\n  CGPA: {t['cgpa']:.2f}    Credits earned: {t['credits_earned']}")


def show_attendance(rows):
    out = [{**r, "percent": "-" if r["percent"] is None else f"{r['percent']}%",
            "status": "SHORTAGE" if r["shortage"] else "OK"} for r in rows]
    table(out, ["code", "title", "present", "total", "percent", "status"])


def run(mgr: StudentManager) -> None:
    actions = {
        "1": lambda: print("  Added", mgr.add_student(
            ask("Reg no (e.g. 24BCE1234)"), ask("Name"), ask("Email"),
            ask("Phone (10 digits)"), ask("Department"), ask("Year (1-4)"))),
        "2": lambda: print("  ", mgr.get_student(ask("Reg no"))),
        "3": lambda: update(mgr),
        "4": lambda: delete(mgr),
        "5": lambda: table(mgr.search_students(ask("Search term (blank = all)")),
                           ["reg_no", "name", "department", "year", "email"]),
        "6": lambda: print("  Added", mgr.add_course(
            ask("Course code (e.g. CSE1001)"), ask("Title"), ask("Credits"))),
        "7": lambda: table(mgr.list_courses(), ["code", "title", "credits"]),
        "8": lambda: (mgr.enroll(ask("Reg no"), ask("Course code")), print("  Enrolled.")),
        "9": lambda: (mgr.record_marks(ask("Reg no"), ask("Course code"), ask("Marks (0-100)")),
                      print("  Marks saved.")),
        "10": lambda: attendance(mgr),
        "11": lambda: show_transcript(mgr.transcript(ask("Reg no"))),
        "12": lambda: show_attendance(mgr.attendance_summary(ask("Reg no"))),
        "13": lambda: table([{**r, "rank": i + 1} for i, r in enumerate(mgr.rank_list())],
                            ["rank", "reg_no", "name", "department", "cgpa"]),
        "14": lambda: print("  Exported", mgr.export_students_csv(
            ask("File path [exports/students.csv]") or "exports/students.csv"), "students."),
    }
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            return
        action = actions.get(choice)
        if not action:
            print("  Invalid option.")
            continue
        try:
            action()
        except SMSError as e:
            print(f"  ! {e}")
        except (KeyboardInterrupt, EOFError):
            print("\n  Cancelled.")
            return


def update(mgr):
    reg = ask("Reg no")
    print("  Leave a field blank to keep it unchanged.")
    fields = {k: ask(k.capitalize()) for k in ("name", "email", "phone", "department", "year")}
    fields = {k: val for k, val in fields.items() if val}
    mgr.update_student(reg, **fields)
    print("  Updated.")


def delete(mgr):
    reg = ask("Reg no")
    if ask(f"Type YES to permanently delete {reg}").upper() == "YES":
        mgr.delete_student(reg)
        print("  Deleted (with their enrollments and attendance).")
    else:
        print("  Cancelled.")


def attendance(mgr):
    reg, code = ask("Reg no"), ask("Course code")
    day = ask(f"Date YYYY-MM-DD [{date.today()}]") or date.today().isoformat()
    present = ask("Present? (y/n)").lower().startswith("y")
    mgr.mark_attendance(reg, code, day, present)
    print("  Attendance saved.")
