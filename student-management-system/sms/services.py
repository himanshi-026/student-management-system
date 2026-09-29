"""Business logic for the Student Management System."""
import csv
import os
import sqlite3
from typing import Dict, List, Optional

from . import database, grading, validators as v
from .errors import DuplicateError, NotFoundError, ValidationError

_UPDATABLE = {"name": v.name, "email": v.email, "phone": v.phone,
              "department": v.department, "year": v.year}


class StudentManager:
    def __init__(self, db_path: str = "sms.db"):
        self.conn = database.connect(db_path)

    def close(self) -> None:
        self.conn.close()

    # ------------------------------------------------------------ students
    def add_student(self, reg_no, name, email, phone, department, year) -> str:
        data = (v.reg_no(reg_no), v.name(name), v.email(email),
                v.phone(phone), v.department(department), v.year(year))
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO students (reg_no, name, email, phone, department, year)"
                    " VALUES (?,?,?,?,?,?)", data)
        except sqlite3.IntegrityError:
            raise DuplicateError("A student with this registration number or email already exists.")
        return data[0]

    def _student_id(self, reg_no: str) -> int:
        reg = v.reg_no(reg_no)
        row = self.conn.execute("SELECT id FROM students WHERE reg_no=?", (reg,)).fetchone()
        if not row:
            raise NotFoundError(f"No student with registration number {reg}.")
        return row["id"]

    def get_student(self, reg_no: str) -> Dict:
        self._student_id(reg_no)
        row = self.conn.execute("SELECT * FROM students WHERE reg_no=?",
                                (v.reg_no(reg_no),)).fetchone()
        return dict(row)

    def update_student(self, reg_no: str, /, **fields) -> Dict:
        sid = self._student_id(reg_no)
        if not fields:
            raise ValidationError("Nothing to update.")
        clean = {}
        for key, val in fields.items():
            if key not in _UPDATABLE:
                raise ValidationError(f"Field '{key}' cannot be updated.")
            clean[key] = _UPDATABLE[key](val)
        sets = ", ".join(f"{k}=?" for k in clean)
        try:
            with self.conn:
                self.conn.execute(f"UPDATE students SET {sets} WHERE id=?",
                                  (*clean.values(), sid))
        except sqlite3.IntegrityError:
            raise DuplicateError("That email is already used by another student.")
        return self.get_student(reg_no)

    def delete_student(self, reg_no: str) -> None:
        sid = self._student_id(reg_no)
        with self.conn:
            self.conn.execute("DELETE FROM students WHERE id=?", (sid,))

    def list_students(self, department: Optional[str] = None) -> List[Dict]:
        sql, args = "SELECT * FROM students", ()
        if department:
            sql, args = sql + " WHERE department=?", (v.department(department),)
        return [dict(r) for r in self.conn.execute(sql + " ORDER BY reg_no", args)]

    def search_students(self, term: str) -> List[Dict]:
        like = f"%{(term or '').strip()}%"
        rows = self.conn.execute(
            "SELECT * FROM students WHERE name LIKE ? OR reg_no LIKE ? OR email LIKE ?"
            " ORDER BY reg_no", (like, like.upper(), like))
        return [dict(r) for r in rows]

    # ------------------------------------------------------------- courses
    def add_course(self, code, title, credits) -> str:
        data = (v.course_code(code), v.title(title), v.credits(credits))
        try:
            with self.conn:
                self.conn.execute("INSERT INTO courses VALUES (?,?,?)", data)
        except sqlite3.IntegrityError:
            raise DuplicateError(f"Course {data[0]} already exists.")
        return data[0]

    def _course(self, code: str) -> sqlite3.Row:
        code = v.course_code(code)
        row = self.conn.execute("SELECT * FROM courses WHERE code=?", (code,)).fetchone()
        if not row:
            raise NotFoundError(f"No course with code {code}.")
        return row

    def list_courses(self) -> List[Dict]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM courses ORDER BY code")]

    # --------------------------------------------------------- enrollments
    def enroll(self, reg_no: str, code: str) -> None:
        sid, course = self._student_id(reg_no), self._course(code)
        try:
            with self.conn:
                self.conn.execute("INSERT INTO enrollments (student_id, course_code) VALUES (?,?)",
                                  (sid, course["code"]))
        except sqlite3.IntegrityError:
            raise DuplicateError("Student is already enrolled in this course.")

    def _require_enrolled(self, reg_no: str, code: str):
        sid, course = self._student_id(reg_no), self._course(code)
        row = self.conn.execute(
            "SELECT id FROM enrollments WHERE student_id=? AND course_code=?",
            (sid, course["code"])).fetchone()
        if not row:
            raise NotFoundError("Student is not enrolled in this course.")
        return sid, course["code"]

    def record_marks(self, reg_no: str, code: str, marks) -> None:
        m = v.marks(marks)
        sid, code = self._require_enrolled(reg_no, code)
        with self.conn:
            self.conn.execute("UPDATE enrollments SET marks=? WHERE student_id=? AND course_code=?",
                              (m, sid, code))

    # ---------------------------------------------------------- attendance
    def mark_attendance(self, reg_no: str, code: str, day: str, present: bool) -> None:
        d = v.iso_date(day)
        sid, code = self._require_enrolled(reg_no, code)
        with self.conn:
            self.conn.execute(
                "INSERT INTO attendance (student_id, course_code, day, present) VALUES (?,?,?,?)"
                " ON CONFLICT(student_id, course_code, day) DO UPDATE SET present=excluded.present",
                (sid, code, d, 1 if present else 0))

    def attendance_summary(self, reg_no: str) -> List[Dict]:
        sid = self._student_id(reg_no)
        rows = self.conn.execute(
            "SELECT e.course_code AS code, c.title AS title,"
            " COUNT(a.id) AS total, COALESCE(SUM(a.present),0) AS present"
            " FROM enrollments e JOIN courses c ON c.code=e.course_code"
            " LEFT JOIN attendance a ON a.student_id=e.student_id AND a.course_code=e.course_code"
            " WHERE e.student_id=? GROUP BY e.course_code ORDER BY e.course_code", (sid,))
        out = []
        for r in rows:
            pct = round(100.0 * r["present"] / r["total"], 1) if r["total"] else None
            out.append({"code": r["code"], "title": r["title"], "total": r["total"],
                        "present": r["present"], "percent": pct,
                        "shortage": pct is not None and pct < grading.ATTENDANCE_MIN})
        return out

    # ------------------------------------------------------------- results
    def transcript(self, reg_no: str) -> Dict:
        student = self.get_student(reg_no)
        rows = self.conn.execute(
            "SELECT c.code, c.title, c.credits, e.marks FROM enrollments e"
            " JOIN courses c ON c.code=e.course_code WHERE e.student_id=? ORDER BY c.code",
            (student["id"],))
        courses, graded = [], []
        for r in rows:
            item = dict(r)
            if r["marks"] is None:
                item.update(grade="-", points=None)
            else:
                g, p = grading.grade_for(r["marks"])
                item.update(grade=g, points=p)
                graded.append((r["credits"], p))
            courses.append(item)
        return {"student": student, "courses": courses, "cgpa": grading.cgpa(graded),
                "credits_earned": sum(c for c, p in graded if p > 0)}

    def rank_list(self, limit: int = 10) -> List[Dict]:
        ranked = []
        for s in self.list_students():
            t = self.transcript(s["reg_no"])
            if any(c["points"] is not None for c in t["courses"]):
                ranked.append({"reg_no": s["reg_no"], "name": s["name"],
                               "department": s["department"], "cgpa": t["cgpa"]})
        ranked.sort(key=lambda r: (-r["cgpa"], r["reg_no"]))
        return ranked[:limit]

    def department_stats(self) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT department, COUNT(*) AS students, ROUND(AVG(year),1) AS avg_year"
            " FROM students GROUP BY department ORDER BY department")
        return [dict(r) for r in rows]

    # -------------------------------------------------------------- export
    def export_students_csv(self, path: str) -> int:
        students = self.list_students()
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        cols = ["reg_no", "name", "email", "phone", "department", "year"]
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(students)
        return len(students)
