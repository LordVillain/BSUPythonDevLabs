from typing import List, Optional
from .models import Student
from .errors import StudentNotFoundError, DuplicateStudentError

class StudentManager:
    def __init__(self):
        self.students: List[Student] = []

    def addStudent(self, student: Student) -> None:
        for s in self.students:
            if s.id == student.id:
                raise DuplicateStudentError(f"Студент с id={student.id} уже существует")
        self.students.append(student)

    def removeStudent(self, student_id: int) -> None:
        for i, s in enumerate(self.students):
            if s.id == student_id:
                del self.students[i]
                return
        raise StudentNotFoundError(f"Студент с id={student_id} не найден")

    def updateGrades(self, student_id: int, new_grades: List[int]) -> None:
        student = self.findStudent(student_id)
        student.grades = new_grades

    def findStudent(self, student_id: int) -> Student:
        for s in self.students:
            if s.id == student_id:
                return s
        raise StudentNotFoundError(f"Студент с id={student_id} не найден")

    def getGroupAverage(self) -> float:
        all_grades = []

        for s in self.students:
            for grade in s.grades:
                all_grades.append(grade)

        if len(all_grades) == 0:
            return 0.0

        return sum(all_grades) / len(all_grades)

    def getStatistics(self) -> dict:
        if not self.students:
            return {
                "total_students": 0,
                "group_average": 0.0,
                "best_student": None,
                "worst_student": None
            }

        best = max(self.students, key=lambda s: s.average())
        worst = min(self.students, key=lambda s: s.average())

        return {
            "total_students": len(self.students),
            "group_average": self.getGroupAverage(),
            "best_student": best,
            "worst_student": worst
        }

    def sortStudents(self, by: str = "id") -> None:
        if by == "id":
            self.students.sort(key=lambda s: s.id)
        elif by == "name":
            self.students.sort(key=lambda s: s.name)
        elif by == "avg":
            self.students.sort(key=lambda s: (-s.average(), s.name))
        else:
            raise ValueError(f"Неизвестный критерий сортировки: {by}")

    def get_top_n(self, n: int) -> List[Student]:
        sorted_students = sorted(self.students, key=lambda s: (-s.average(), s.name))
        return sorted_students[:n]