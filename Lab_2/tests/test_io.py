import csv
import pytest
from lab.models import Student
from lab.errors import InvalidDataError, FileError
from lab.io_utils import readStudentsFromCSV, writeStudentsToCSV, exportTopNtoCSV


@pytest.fixture
def students_list():
    return [
        Student(1, "Иванов", [80, 90]),
        Student(2, "Петров", [60]),
        Student(3, "Сидоров", [])
    ]


def test_write_and_read_roundtrip(tmp_path, students_list):
    file = tmp_path / "students.csv"

    # Записываем
    writeStudentsToCSV(file, students_list, write_header=True)

    # Читаем
    loaded = readStudentsFromCSV(file, has_header=True)

    assert len(loaded) == 3
    assert loaded[0].id == 1
    assert loaded[0].name == "Иванов"
    assert loaded[0].grades == [80, 90]


def test_write_empty_file_with_header(tmp_path):
    file = tmp_path / "empty.csv"

    writeStudentsToCSV(file, [], write_header=True)

    with open(file, encoding="utf-8") as f:
        lines = f.read().strip().splitlines()

    assert lines == ["id,name"]


def test_write_empty_file_without_header(tmp_path):
    file = tmp_path / "empty.csv"

    writeStudentsToCSV(file, [], write_header=False)

    with open(file, encoding="utf-8") as f:
        content = f.read().strip()

    assert content == ""


def test_read_invalid_id(tmp_path):
    file = tmp_path / "bad.csv"
    file.write_text("id,name,grade1\nabc,Иванов,90", encoding="utf-8")

    with pytest.raises(InvalidDataError):
        readStudentsFromCSV(file)


def test_read_invalid_grade(tmp_path):
    file = tmp_path / "bad.csv"
    file.write_text("id,name,grade1\n1,Иванов,not_a_number", encoding="utf-8")

    with pytest.raises(InvalidDataError):
        readStudentsFromCSV(file)


def test_read_out_of_range_grade(tmp_path):
    file = tmp_path / "bad.csv"
    file.write_text("id,name,grade1\n1,Иванов,200", encoding="utf-8")

    with pytest.raises(InvalidDataError):
        readStudentsFromCSV(file)


def test_file_not_found():
    with pytest.raises(FileError):
        readStudentsFromCSV("no_such_file.csv")


def test_export_top_n(tmp_path, students_list):
    file = tmp_path / "top.csv"
    exportTopNtoCSV(file, students_list, n=2)

    with open(file, encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert rows[0] == ["id", "name", "average", "grades"]
    # Иванов (avg 85.0) и Петров (avg 60.0) должны попасть в топ-2
    assert rows[1][1] == "Иванов"
    assert rows[2][1] == "Петров"


def test_write_and_read_without_header(tmp_path, students_list):
    file = tmp_path / "students.csv"

    writeStudentsToCSV(file, students_list, write_header=False)
    loaded = readStudentsFromCSV(file, has_header=False)

    assert len(loaded) == len(students_list)
    assert loaded[1].name == "Петров"
