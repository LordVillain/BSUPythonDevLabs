import pytest
from lab.models import Student


def test_student_init_with_grades():
    s = Student(1, "Иванов", [90, 80, 70])
    assert s.id == 1
    assert s.name == "Иванов"
    assert s.grades == [90, 80, 70]


def test_student_init_without_grades():
    s = Student(2, "Петров")
    assert s.grades == []


@pytest.mark.parametrize(
    "grades, expected_avg",
    [
        ([100, 90, 80], 90.0),
        ([50], 50.0),
        ([], 0.0),
    ],
)
def test_student_average(grades, expected_avg):
    s = Student(1, "Test", grades)
    assert pytest.approx(s.average(), rel=1e-2) == expected_avg


def test_student_repr_contains_info():
    s = Student(3, "Сидоров", [100, 0])
    rep = repr(s)
    assert "Student" in rep
    assert "Сидоров" in rep
    assert "avg=50.00" in rep
