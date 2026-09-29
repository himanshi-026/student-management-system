import os
import tempfile
import unittest

from sms import StudentManager, ValidationError, NotFoundError, DuplicateError
from sms import grading


class SMSTests(unittest.TestCase):
    def setUp(self):
        self.m = StudentManager(":memory:")
        self.m.add_student("24bce1001", "aarav sharma", "Aarav@Example.com",
                           "9876500001", "cse", 2)
        self.m.add_course("cse1001", "Python", 4)
        self.m.add_course("MAT1001", "Calculus", 2)

    def tearDown(self):
        self.m.close()

    # --- students
    def test_add_normalises_and_get(self):
        s = self.m.get_student("24BCE1001")
        self.assertEqual((s["name"], s["email"], s["department"]),
                         ("Aarav Sharma", "aarav@example.com", "CSE"))

    def test_duplicate_reg_and_email(self):
        with self.assertRaises(DuplicateError):
            self.m.add_student("24BCE1001", "X Y", "x@y.com", "9876500009", "CSE", 1)
        with self.assertRaises(DuplicateError):
            self.m.add_student("24BCE1002", "X Y", "aarav@example.com", "9876500009", "CSE", 1)

    def test_validation(self):
        bad = [("BADREG", "A", "a@b.com", "9876500009", "CSE", 1),
               ("24BCE1002", "A1", "a@b.com", "9876500009", "CSE", 1),
               ("24BCE1002", "Ab", "not-email", "9876500009", "CSE", 1),
               ("24BCE1002", "Ab", "a@b.com", "12345", "CSE", 1),
               ("24BCE1002", "Ab", "a@b.com", "9876500009", "CSE", 9)]
        for args in bad:
            with self.assertRaises(ValidationError):
                self.m.add_student(*args)

    def test_update_and_delete(self):
        self.m.update_student("24BCE1001", year=3, phone="9123456780")
        self.assertEqual(self.m.get_student("24BCE1001")["year"], 3)
        with self.assertRaises(ValidationError):
            self.m.update_student("24BCE1001", reg_no="24BCE9999")
        self.m.delete_student("24BCE1001")
        with self.assertRaises(NotFoundError):
            self.m.get_student("24BCE1001")

    def test_search(self):
        self.assertEqual(len(self.m.search_students("aarav")), 1)
        self.assertEqual(len(self.m.search_students("zzz")), 0)

    # --- courses / enrollment
    def test_enroll_rules(self):
        self.m.enroll("24BCE1001", "CSE1001")
        with self.assertRaises(DuplicateError):
            self.m.enroll("24BCE1001", "CSE1001")
        with self.assertRaises(NotFoundError):
            self.m.enroll("24BCE1001", "XYZ9999")
        with self.assertRaises(NotFoundError):
            self.m.record_marks("24BCE1001", "MAT1001", 80)   # not enrolled

    def test_marks_range(self):
        self.m.enroll("24BCE1001", "CSE1001")
        with self.assertRaises(ValidationError):
            self.m.record_marks("24BCE1001", "CSE1001", 101)

    # --- grading
    def test_grade_boundaries(self):
        self.assertEqual(grading.grade_for(90), ("S", 10))
        self.assertEqual(grading.grade_for(89.9), ("A", 9))
        self.assertEqual(grading.grade_for(40), ("E", 5))
        self.assertEqual(grading.grade_for(39.9), ("F", 0))

    def test_cgpa(self):
        self.m.enroll("24BCE1001", "CSE1001")   # 4 credits
        self.m.enroll("24BCE1001", "MAT1001")   # 2 credits
        self.m.record_marks("24BCE1001", "CSE1001", 95)   # 10 pts
        self.m.record_marks("24BCE1001", "MAT1001", 65)   # 7 pts
        t = self.m.transcript("24BCE1001")
        self.assertEqual(t["cgpa"], round((4 * 10 + 2 * 7) / 6, 2))

    def test_ungraded_courses_ignored_in_cgpa(self):
        self.m.enroll("24BCE1001", "CSE1001")
        self.assertEqual(self.m.transcript("24BCE1001")["cgpa"], 0.0)

    def test_rank_list_order(self):
        self.m.add_student("24BCE1002", "Diya Patel", "d@e.com", "9876500002", "CSE", 2)
        for reg, mk in (("24BCE1001", 60), ("24BCE1002", 95)):
            self.m.enroll(reg, "CSE1001")
            self.m.record_marks(reg, "CSE1001", mk)
        ranks = self.m.rank_list()
        self.assertEqual([r["reg_no"] for r in ranks], ["24BCE1002", "24BCE1001"])

    # --- attendance
    def test_attendance_percentage_and_shortage(self):
        self.m.enroll("24BCE1001", "CSE1001")
        for i in range(1, 5):
            self.m.mark_attendance("24BCE1001", "CSE1001", f"2026-08-0{i}", i <= 2)
        s = self.m.attendance_summary("24BCE1001")[0]
        self.assertEqual((s["total"], s["present"], s["percent"]), (4, 2, 50.0))
        self.assertTrue(s["shortage"])

    def test_attendance_can_be_corrected_and_validated(self):
        self.m.enroll("24BCE1001", "CSE1001")
        self.m.mark_attendance("24BCE1001", "CSE1001", "2026-08-01", False)
        self.m.mark_attendance("24BCE1001", "CSE1001", "2026-08-01", True)
        s = self.m.attendance_summary("24BCE1001")[0]
        self.assertEqual((s["total"], s["present"]), (1, 1))
        with self.assertRaises(ValidationError):
            self.m.mark_attendance("24BCE1001", "CSE1001", "01-08-2026", True)

    def test_delete_cascades(self):
        self.m.enroll("24BCE1001", "CSE1001")
        self.m.mark_attendance("24BCE1001", "CSE1001", "2026-08-01", True)
        self.m.delete_student("24BCE1001")
        for table in ("enrollments", "attendance"):
            n = self.m.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            self.assertEqual(n, 0)

    # --- export
    def test_export_csv(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "out.csv")
            self.assertEqual(self.m.export_students_csv(path), 1)
            with open(path) as f:
                self.assertIn("24BCE1001", f.read())


if __name__ == "__main__":
    unittest.main()
