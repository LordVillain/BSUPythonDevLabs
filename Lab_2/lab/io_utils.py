import csv
from typing import List, Optional
from .models import Student
from .errors import InvalidDataError, FileError

def readStudentsFromCSV(filename: str, has_header: bool = True) -> List[Student]:
    students = []
    try:
        with open(filename, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                return students

            header = None
            start_row = 0
            if has_header:
                header = rows[0]
                start_row = 1

            for i, row in enumerate(rows[start_row:], start=start_row):
                if len(row) < 2:
                    raise InvalidDataError(f"Строка {i+1}: минимум 2 колонки (id, name)")

                try:
                    student_id = int(row[0])
                    name = row[1]
                except ValueError:
                    raise InvalidDataError(f"Строка {i+1}: id должен быть целым числом")

                grades = []
                for j, grade_str in enumerate(row[2:], start=2):
                    if grade_str.strip() == "":
                        continue
                    try:
                        grade = int(grade_str)
                        if not (0 <= grade <= 100):
                            raise InvalidDataError(f"Строка {i+1}, колонка {j+1}: оценка должна быть от 0 до 100")
                        grades.append(grade)
                    except ValueError:
                        raise InvalidDataError(f"Строка {i+1}, колонка {j+1}: оценка должна быть целым числом")

                students.append(Student(student_id, name, grades))

    except FileNotFoundError:
        raise FileError(f"Файл '{filename}' не найден")
    except PermissionError:
        raise FileError(f"Нет прав на чтение файла '{filename}'")
    except InvalidDataError:
        raise
    except Exception as e:
        raise FileError(f"Ошибка при чтении файла: {e}")

    return students


def writeStudentsToCSV(filename: str, students: List[Student], write_header: bool = True) -> None:
    if not students:
        headers = ["id", "name"]
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(headers)
        return

    max_grades = max(len(s.grades) for s in students)

    try:
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            if write_header:
                headers = ["id", "name"] + [f"grade{i+1}" for i in range(max_grades)]
                writer.writerow(headers)

            for student in students:
                row = [student.id, student.name]
                grades_padded = [str(g) if i < len(student.grades) else "" for i, g in enumerate(student.grades + [""] * max_grades)]
                row.extend(grades_padded[:max_grades])
                writer.writerow(row)

    except PermissionError:
        raise FileError(f"Нет прав на запись в файл '{filename}'")
    except Exception as e:
        raise FileError(f"Ошибка при записи в файл: {e}")


def exportTopNtoCSV(filename: str, students: List[Student], n: int) -> None:
    top_n = sorted(students, key=lambda s: (-s.average(), s.name))[:n]

    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "average", "grades"])

        for s in top_n:
            grades_str = " ".join(map(str, s.grades))
            writer.writerow([s.id, s.name, f"{s.average():.2f}", grades_str])