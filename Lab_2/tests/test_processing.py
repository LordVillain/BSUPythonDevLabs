import pytest
from lab.models import Student
from lab.errors import StudentNotFoundError, DuplicateStudentError
from lab.processing import StudentManager


class TestStudentManager:

    def test_add_student_success(self):
        manager = StudentManager()
        student = Student(id=1, name="Иван Иванов", grades=[80, 90])
        manager.addStudent(student)
        assert len(manager.students) == 1
        assert manager.students[0] == student

    def test_add_student_duplicate_id_raises_error(self):
        manager = StudentManager()
        s1 = Student(id=1, name="А", grades=[80])
        s2 = Student(id=1, name="Б", grades=[90])
        manager.addStudent(s1)
        with pytest.raises(DuplicateStudentError, match="Студент с id=1 уже существует"):
            manager.addStudent(s2)

    def test_remove_student_success(self):
        manager = StudentManager()
        student = Student(id=1, name="Иван", grades=[85])
        manager.addStudent(student)
        manager.removeStudent(1)
        assert len(manager.students) == 0

    def test_remove_nonexistent_student_raises_error(self):
        manager = StudentManager()
        with pytest.raises(StudentNotFoundError, match="Студент с id=999 не найден"):
            manager.removeStudent(999)

    def test_update_grades_success(self):
        manager = StudentManager()
        student = Student(id=1, name="Петр", grades=[70, 80])
        manager.addStudent(student)
        manager.updateGrades(1, [90, 95])
        assert manager.students[0].grades == [90, 95]
        assert manager.students[0].average() == 92.5

    def test_update_grades_nonexistent_student_raises_error(self):
        manager = StudentManager()
        with pytest.raises(StudentNotFoundError):
            manager.updateGrades(1, [100])

    def test_get_group_average_empty(self):
        manager = StudentManager()
        assert manager.getGroupAverage() == 0.0

    def test_get_group_average_with_data(self):
        manager = StudentManager()
        manager.addStudent(Student(1, "A", [80, 90]))
        manager.addStudent(Student(2, "B", [70]))
        assert manager.getGroupAverage() == 80.0

    def test_get_statistics_empty(self):
        manager = StudentManager()
        stats = manager.getStatistics()
        assert stats["total_students"] == 0
        assert stats["group_average"] == 0.0
        assert stats["best_student"] is None
        assert stats["worst_student"] is None

    def test_get_statistics_with_students(self):
        manager = StudentManager()
        manager.addStudent(Student(1, "Анна", [100, 90]))
        manager.addStudent(Student(2, "Борис", [60, 70]))
        stats = manager.getStatistics()
        assert stats["total_students"] == 2
        assert stats["group_average"] == 80.0
        assert stats["best_student"].name == "Анна"
        assert stats["worst_student"].name == "Борис"

    def test_sort_by_id(self):
        manager = StudentManager()
        manager.addStudent(Student(3, "Вася", [80]))
        manager.addStudent(Student(1, "Анна", [90]))
        manager.sortStudents("id")
        assert [s.id for s in manager.students] == [1, 3]

    def test_sort_by_name(self):
        manager = StudentManager()
        manager.addStudent(Student(1, "Петр", [85]))
        manager.addStudent(Student(2, "Анна", [95]))
        manager.sortStudents("name")
        assert [s.name for s in manager.students] == ["Анна", "Петр"]

    def test_sort_by_avg(self):
        manager = StudentManager()
        manager.addStudent(Student(1, "Петр", [70, 80]))
        manager.addStudent(Student(2, "Анна", [90, 100]))
        manager.addStudent(Student(3, "Зоя", [90, 100]))
        manager.sortStudents("avg")
        names = [s.name for s in manager.students]
        assert names == ["Анна", "Зоя", "Петр"]

    def test_sort_invalid_criterion_raises_error(self):
        manager = StudentManager()
        with pytest.raises(ValueError, match="Неизвестный критерий сортировки: invalid"):
            manager.sortStudents("invalid")

    def test_get_top_n(self):
        manager = StudentManager()
        manager.addStudent(Student(1, "Петр", [70]))
        manager.addStudent(Student(2, "Анна", [100]))
        manager.addStudent(Student(3, "Зоя", [95]))
        top2 = manager.get_top_n(2)
        assert len(top2) == 2
        assert top2[0].name == "Анна"
        assert top2[1].name == "Зоя"

    def test_get_top_n_more_than_available(self):
        manager = StudentManager()
        manager.addStudent(Student(1, "Один", [80]))
        top5 = manager.get_top_n(5)
        assert len(top5) == 1
        assert top5[0].name == "Один"

    def test_get_top_n_empty(self):
        manager = StudentManager()
        top3 = manager.get_top_n(3)
        assert top3 == []