from typing import List

class Student:
    def __init__(self, student_id=None, name=None, grades: List[int] = None, id=None):
        if student_id is None and id is None:
            raise ValueError("Необходимо указать id студента")
        self.id = student_id if student_id is not None else id
        self.name = name
        self.grades = grades or []

    def average(self):
        if not self.grades:
            return 0.0
        return sum(self.grades) / len(self.grades)

    def __repr__(self):
        return f"Student(id={self.id}, name='{self.name}', grades={self.grades}, avg={self.average():.2f})"
