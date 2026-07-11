from services.generator import generate_mock_records, metrics
from services.student_table import make_student_table


def test_mock_result_count_matches_students():
    table = make_student_table(2)
    table.loc[0, ["주요 활동", "강점", "참여 태도"]] = ["토의", "설명", "경청"]
    table.loc[1, ["주요 활동", "강점", "참여 태도"]] = ["조사", "비교", "성실"]
    assert len(generate_mock_records(table)) == 2


def test_character_and_utf8_byte_counts():
    assert metrics("가A") == (2, 4)
