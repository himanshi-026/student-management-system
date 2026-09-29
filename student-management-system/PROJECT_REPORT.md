# Project Report: Student Management System

**Student:** [Your Name]  **Reg. No:** [Your Reg No]  **Course:** [Course Name]  **Date:** [Month Year]

---

## 1. Abstract
This project is a Student Management System built with Python and SQLite. It manages student records, courses, enrollments, marks and attendance, and automatically computes grades, CGPA, attendance percentage, shortage alerts and rank lists. The code is modular, input is validated, and the logic is covered by 15 automated tests.

## 2. Introduction
Academic data such as personal details, marks and attendance is often kept manually, which is slow and error-prone. A small database application removes repeated work and gives instant, consistent reports.

## 3. Problem Statement and Objectives
**Problem:** Manual record keeping causes duplicates, calculation errors and delayed identification of at-risk students.
**Objectives:**
1. Store student, course, marks and attendance data reliably.
2. Validate every input to keep data clean.
3. Automate grade, CGPA and attendance calculations.
4. Provide search, reports and export.
5. Keep the design modular and tested.

## 4. Requirements
**Functional:** add/view/update/delete students; manage courses; enroll students; record marks; mark attendance; view transcript, attendance report and rank list; export to CSV.
**Non-functional:** works offline, no external dependencies, clear error messages, data consistency, easy to extend.
**Software:** Python 3.8+, SQLite (bundled with Python), any terminal.

## 5. System Design

### 5.1 Architecture
```
   cli.py (menu)  ──►  services.py (StudentManager)  ──►  database.py (SQLite)
                              │
                     validators.py · grading.py · errors.py
```
The interface never touches SQL directly, so it can be swapped for a GUI or web layer.

### 5.2 Database Schema
| Table | Key columns |
|---|---|
| `students` | id (PK), reg_no (unique), name, email (unique), phone, department, year (1–4) |
| `courses` | code (PK), title, credits (1–10) |
| `enrollments` | student_id (FK), course_code (FK), marks (0–100 or NULL); unique per student and course |
| `attendance` | student_id (FK), course_code (FK), day, present (0/1); unique per student, course and day |

Foreign keys use `ON DELETE CASCADE`; `CHECK` constraints back up the application-level validation.

### 5.3 Validation Rules
Registration number `24BCE1234` pattern; valid email; 10-digit phone starting 6–9; year 1–4; course code like `CSE1001`; marks 0–100; date `YYYY-MM-DD`.

### 5.4 Grading and CGPA
Marks map to grades S–F (10–0 points) as shown in the README. `CGPA = Σ(credits × points) ÷ Σ(credits)`, using only courses that have marks. Attendance below 75 % is flagged as shortage.

## 6. Implementation
- `services.py` holds all operations and translates database errors into friendly exceptions (`ValidationError`, `NotFoundError`, `DuplicateError`).
- Queries are parameterised (`?` placeholders) to prevent SQL injection.
- Attendance uses an upsert so a wrong entry can be corrected by marking the same date again.
- The rank list sorts by CGPA (descending), then registration number.
- Deleting a student requires typing `YES` in the menu.

## 7. Testing
15 unit tests (`python -m unittest discover -s tests -v`), all passing. They cover: normalisation on insert, duplicate reg no / email, invalid inputs, update rules, delete with cascade, search, enrollment rules, marks range, grade boundaries (90, 89.9, 40, 39.9), CGPA calculation, ungraded courses, rank ordering, attendance percentage and shortage, attendance correction, invalid dates and CSV export. The interactive menu was also exercised manually with valid and invalid input.

## 8. Results
With the built-in sample data (5 students, 4 courses):

| Rank | Student | CGPA |
|---|---|---|
| 1 | Diya Patel | 9.77 |
| 2 | Aarav Sharma | 9.08 |
| 3 | Karthik Nair | 8.08 |
| 4 | Rohan Verma | 6.92 |
| 5 | Ananya Iyer | 4.62 |

Ananya Iyer's attendance in CSE1001 is 13 of 20 classes (65 %), so the system flags a shortage. Grades, CGPA and attendance percentages are produced instantly instead of by manual calculation.

## 9. Limitations
- Single-user, command-line interface with no login or roles.
- One grading scale (configurable only in code).
- CGPA is cumulative; there is no semester-wise GPA.
- The sample data is fictional.

## 10. Future Scope
Role-based login, Tkinter or Flask front-end, semester-wise GPA, PDF report cards, automatic e-mail alerts for attendance shortage, cloud database.

## 11. Conclusion
The system replaces error-prone manual record keeping with a validated, consistent and tested application. Its layered design makes it a solid base for a GUI or web version.

## 12. How to Run
```bash
python main.py --demo
python -m unittest discover -s tests -v
```

## 13. References
1. Python documentation: `sqlite3`, `unittest`, `argparse` (docs.python.org).
2. SQLite documentation: foreign keys and constraints (sqlite.org).
3. Institution grading and attendance regulations (used as the basis for the 10-point scale and 75 % rule; adjust to your institute's official rules).
