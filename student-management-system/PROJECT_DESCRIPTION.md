# Project Description

**Title:** Student Management System
**Domain:** Education / Database Applications
**Language:** Python 3 with SQLite

## Problem Statement
Many small institutions and departments still track student details, marks and attendance in paper registers or scattered spreadsheets. This causes duplicate or inconsistent records, calculation mistakes in grades and CGPA, slow searching, and late detection of students with attendance shortage.

## Objective
Build a reliable, easy-to-use application that stores student, course, marks and attendance data in one place, validates all input, and automatically produces grades, CGPA, attendance status and rank lists.

## Solution Overview
A menu-driven Python application backed by an SQLite database. Business logic (`StudentManager`) is separate from the interface, so it can later be reused with a GUI or web front-end. All input is validated (registration number, email, phone, marks range, dates). Database constraints prevent duplicate records and keep related data consistent.

## Key Features
- Full student CRUD with search and department filter
- Course management and student enrollment
- Marks entry with automatic grade and grade points
- Credit-weighted CGPA and printable transcript
- Attendance tracking with a 75 % shortage warning
- Rank list, department statistics and CSV export
- Sample data loader for quick demonstration
- 15 automated unit tests

## Technologies
Python 3 (standard library), SQLite, `unittest`, Git/GitHub.

## Outcome
A working, tested application with modular code that runs anywhere Python is installed, with no external dependencies.

## Learning Outcomes
Database design and SQL (constraints, foreign keys, joins, aggregation), modular programming, input validation, exception handling, unit testing and version control.
