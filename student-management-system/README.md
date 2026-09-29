# 🎓 Student Management System

A menu-driven **Python + SQLite** application to manage students, courses, enrollments, marks and attendance. It calculates grades and **CGPA** (10-point VIT-style scale), flags **attendance shortage** (< 75 %), and produces rank lists and CSV exports.

> **VITyarthi Project** · Name: `[Himanshi khajuriya]` · Reg. No: `[26MIM10132]` · Course: `[Problem solving and programming]`

---

## ✨ Features

| Area | What you can do |
|---|---|
| **Students** | Add, view, update, delete, list by department, search by name / reg no / email |
| **Courses** | Add and list courses with credits |
| **Enrollment** | Enroll students in courses (duplicates blocked) |
| **Marks & Grades** | Enter marks (0–100) → automatic grade (S/A/B/C/D/E/F) and grade points |
| **CGPA** | Credit-weighted CGPA per student, transcript view |
| **Attendance** | Mark daily attendance per course, percentage, **shortage warning below 75 %** |
| **Reports** | Rank list (top CGPA), department statistics, CSV export |
| **Data safety** | Input validation, unique constraints, foreign keys with cascade delete, delete confirmation |

## 🛠 Tech Stack

Python 3.8+ (standard library only) · SQLite (`sqlite3`) · `unittest` · Git/GitHub. **No installation of extra packages is required.**

## 📁 Project Structure

```
student-management-system/
├── main.py                 # entry point (menu / demo)
├── sms/
│   ├── __init__.py
│   ├── database.py         # SQLite connection + schema
│   ├── services.py         # business logic (StudentManager)
│   ├── validators.py       # input validation
│   ├── grading.py          # marks -> grade -> CGPA
│   ├── errors.py           # custom exceptions
│   ├── cli.py              # menu-driven interface
│   └── demo.py             # sample data
├── tests/test_sms.py       # 15 unit tests
├── exports/                # CSV exports go here
├── PROJECT_REPORT.md
├── PROJECT_DESCRIPTION.md
├── requirements.txt
├── LICENSE
└── README.md
```

## 🚀 Getting Started

```bash
git clone https://github.com/<your-username>/student-management-system.git
cd student-management-system

python main.py --demo          # load sample data and open the menu
python main.py                 # start with your own (empty) database
python main.py --demo-report   # print a sample report and exit
```

The database is stored in `sms.db` in the project folder (use `--db other.db` to change it).

### Run the tests

```bash
python -m unittest discover -s tests -v
```

## 📋 Menu

```
 1. Add student            8. Enroll student in course
 2. View student           9. Enter marks
 3. Update student        10. Mark attendance
 4. Delete student        11. Transcript (grades + CGPA)
 5. List / search         12. Attendance report
 6. Add course            13. Rank list (top CGPA)
 7. List courses          14. Export students to CSV
 0. Exit
```

## 📊 Sample Output (`python main.py --demo-report`)

```
  Diya Patel (24BCE1002) - CSE, Year 2
  CODE    | TITLE                       | CREDITS | MARKS | GRADE | POINTS
  --------+-----------------------------+---------+-------+-------+-------
  CSE1001 | Problem Solving with Python | 4       | 95.0  | S     | 10
  ENG1001 | Technical English           | 2       | 93.0  | S     | 10
  MAT1001 | Calculus                    | 4       | 91.0  | S     | 10
  PHY1001 | Engineering Physics         | 3       | 89.0  | A     | 9

  CGPA: 9.77    Credits earned: 13

  Rank list:
  RANK | REG_NO    | NAME         | DEPARTMENT | CGPA
  -----+-----------+--------------+------------+-----
  1    | 24BCE1002 | Diya Patel   | CSE        | 9.77
  2    | 24BCE1001 | Aarav Sharma | CSE        | 9.08
  3    | 24BCE1005 | Karthik Nair | CSE        | 8.08
```

## 🎯 Grading Scale

| Marks | Grade | Points |
|---|---|---|
| 90–100 | S | 10 |
| 80–89 | A | 9 |
| 70–79 | B | 8 |
| 60–69 | C | 7 |
| 50–59 | D | 6 |
| 40–49 | E | 5 |
| < 40 | F | 0 |

`CGPA = Σ(credits × points) ÷ Σ(credits)` over courses that have marks. Change the scale in `sms/grading.py`.

## 🗄 Database Design

`students` (1) ── (M) `enrollments` (M) ── (1) `courses`
`attendance` links a student and a course per date. Deleting a student removes their enrollments and attendance automatically.

## 🔮 Future Work

Login with roles (admin / faculty / student), GUI or web front-end (Tkinter / Flask), semester-wise GPA, PDF report cards, e-mail alerts for attendance shortage.

## 📄 License

MIT: see [LICENSE](LICENSE).
