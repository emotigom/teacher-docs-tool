from zipfile import ZipFile

from services.exporter import export_xlsx
from services.generator import generate_mock_records
from services.student_table import make_student_table


def test_export_has_exactly_two_sheets(tmp_path):
    table = make_student_table(1)
    table.at[0, "주요 활동"] = "토의"
    path = export_xlsx(table, generate_mock_records(table), tmp_path)
    with ZipFile(path) as workbook:
        sheets = [name for name in workbook.namelist() if name.startswith("xl/worksheets/sheet")]
    assert len(sheets) == 2
