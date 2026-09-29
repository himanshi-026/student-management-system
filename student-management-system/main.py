#!/usr/bin/env python3
"""Student Management System - entry point.

    python main.py             # interactive menu
    python main.py --demo      # load sample data first, then open the menu
    python main.py --demo-report   # load sample data and just print a report
"""
import argparse

from sms import StudentManager
from sms.cli import run, show_transcript, show_attendance, table
from sms.demo import seed


def main():
    p = argparse.ArgumentParser(description="Student Management System")
    p.add_argument("--db", default="sms.db", help="SQLite database file (default sms.db)")
    p.add_argument("--demo", action="store_true", help="load sample data if DB is empty")
    p.add_argument("--demo-report", action="store_true",
                   help="load sample data, print a sample report and exit")
    a = p.parse_args()

    mgr = StudentManager(a.db)
    try:
        if a.demo or a.demo_report:
            print("Sample data loaded." if seed(mgr) else "Database already has data; not reseeding.")
        if a.demo_report:
            show_transcript(mgr.transcript("24BCE1002"))
            print("\n  Attendance (24BME1004):")
            show_attendance(mgr.attendance_summary("24BME1004"))
            print("\n  Rank list:")
            table([{**r, "rank": i + 1} for i, r in enumerate(mgr.rank_list())],
                  ["rank", "reg_no", "name", "department", "cgpa"])
        else:
            run(mgr)
    finally:
        mgr.close()


if __name__ == "__main__":
    main()
