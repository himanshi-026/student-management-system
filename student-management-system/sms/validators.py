"""Input validation helpers."""
import re
from datetime import date

from .errors import ValidationError

REG_RE = re.compile(r"^\d{2}[A-Z]{3}\d{4}$")          # e.g. 24BCE1234
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
PHONE_RE = re.compile(r"^[6-9]\d{9}$")                 # 10-digit Indian mobile
CODE_RE = re.compile(r"^[A-Z]{3,4}\d{3,4}[A-Z]?$")     # e.g. CSE1001


def reg_no(v: str) -> str:
    v = (v or "").strip().upper()
    if not REG_RE.match(v):
        raise ValidationError("Registration number must look like 24BCE1234.")
    return v


def name(v: str) -> str:
    v = " ".join((v or "").split())
    if not v or not re.match(r"^[A-Za-z][A-Za-z .'-]*$", v):
        raise ValidationError("Name must contain only letters, spaces, . ' -")
    return v.title()


def email(v: str) -> str:
    v = (v or "").strip().lower()
    if not EMAIL_RE.match(v):
        raise ValidationError("Invalid email address.")
    return v


def phone(v: str) -> str:
    v = (v or "").strip()
    if not PHONE_RE.match(v):
        raise ValidationError("Phone must be a 10-digit number starting with 6-9.")
    return v


def department(v: str) -> str:
    v = (v or "").strip().upper()
    if not v or len(v) > 30:
        raise ValidationError("Department is required (max 30 characters).")
    return v


def year(v) -> int:
    try:
        y = int(v)
    except (TypeError, ValueError):
        raise ValidationError("Year must be a number from 1 to 4.")
    if not 1 <= y <= 4:
        raise ValidationError("Year must be between 1 and 4.")
    return y


def course_code(v: str) -> str:
    v = (v or "").strip().upper()
    if not CODE_RE.match(v):
        raise ValidationError("Course code must look like CSE1001.")
    return v


def title(v: str) -> str:
    v = " ".join((v or "").split())
    if not v:
        raise ValidationError("Course title is required.")
    return v


def credits(v) -> int:
    try:
        c = int(v)
    except (TypeError, ValueError):
        raise ValidationError("Credits must be a whole number (1-10).")
    if not 1 <= c <= 10:
        raise ValidationError("Credits must be between 1 and 10.")
    return c


def marks(v) -> float:
    try:
        m = float(v)
    except (TypeError, ValueError):
        raise ValidationError("Marks must be a number from 0 to 100.")
    if not 0 <= m <= 100:
        raise ValidationError("Marks must be between 0 and 100.")
    return m


def iso_date(v: str) -> str:
    try:
        return date.fromisoformat((v or "").strip()).isoformat()
    except ValueError:
        raise ValidationError("Date must be in YYYY-MM-DD format.")
