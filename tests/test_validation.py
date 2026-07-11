import pandas as pd

from services.student_table import add_students, make_student_table, remove_students
from services.validation import validate_students


def test_default_has_25_rows():
    assert len(make_student_table()) == 25


def test_add_and_remove_five_rows():
    table = make_student_table()
    assert len(add_students(table)) == 30
    assert len(remove_students(add_students(table))) == 25


def test_maximum_is_200_rows():
    assert len(add_students(make_student_table(200))) == 200


def test_empty_student_is_error():
    _, errors, _ = validate_students(make_student_table(1))
    assert any("관찰 내용" in error for error in errors)


def test_private_information_is_blocked():
    table = make_student_table(1)
    table.at[0, "관찰 메모"] = "연락처는 010-1234-5678"
    _, errors, _ = validate_students(table)
    assert any("전화번호" in error for error in errors)
