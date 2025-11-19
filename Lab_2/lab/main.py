from .processing import StudentManager
from .io_utils import readStudentsFromCSV, writeStudentsToCSV, exportTopNtoCSV
from .errors import *
from lab.models import Student

def main():
    manager = StudentManager()
    filename = "data/students.csv"

    while True:
        print("\n=== Меню ===")
        print("1. Загрузить из CSV")
        print("2. Сохранить в CSV")
        print("3. Показать всех студентов")
        print("4. Добавить студента")
        print("5. Удалить студента по id")
        print("6. Обновить оценки по id")
        print("7. Показать статистику")
        print("8. Экспорт ТОП-N студентов")
        print("9. Сортировать студентов (по avg|name|id)")
        print("0. Выход")
        print("==============")
        print()

        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                students = readStudentsFromCSV(filename)
                manager.students = students
                print(f"Загружено {len(students)} студентов.")

            elif choice == "2":
                writeStudentsToCSV(filename, manager.students)
                print("Сохранено в CSV.")

            elif choice == "3":
                print("=== Список студентов ===")
                for s in manager.students:
                    print(s)

            elif choice == "4":
                student_id = int(input("ID: "))
                name = input("Имя: ")
                grades_input = input("Оценки (через пробел): ")
                grades = [int(x) for x in grades_input.split()] if grades_input else []
                manager.addStudent(Student(student_id, name, grades))
                print("Студент добавлен.")

            elif choice == "5":
                student_id = int(input("ID студента для удаления: "))
                manager.removeStudent(student_id)
                print("Студент удалён.")

            elif choice == "6":
                try:
                    student_id = int(input("ID студента: "))
                except ValueError:
                    print("Ошибка: ID должен быть целым числом.")
                    continue

                grades_input = input("Новые оценки (через пробел): ").strip()
                if not grades_input:
                    grades = []
                else:
                    grade_strs = grades_input.split()
                    grades = []
                    valid = True
                    for g_str in grade_strs:
                        try:
                            grade = int(g_str)
                            if not (0 <= grade <= 100):
                                print(f"Ошибка: оценка '{g_str}' должна быть от 0 до 100.")
                                valid = False
                                break
                            grades.append(grade)
                        except ValueError:
                            print(f"Ошибка: '{g_str}' — не является целым числом.")
                            valid = False
                            break

                    if not valid:
                        continue  # не обновляем, возвращаемся в меню

                try:
                    manager.updateGrades(student_id, grades)
                    print("Оценки обновлены.")
                except StudentNotFoundError as e:
                    print(f"Ошибка: {e}")

            elif choice == "7":
                stats = manager.getStatistics()
                print(f"Всего студентов: {stats['total_students']}")
                print(f"Средний балл группы: {stats['group_average']:.2f}")
                if stats['best_student']:
                    print(f"Лучший: {stats['best_student'].name} ({stats['best_student'].average():.2f})")
                    print(f"Худший: {stats['worst_student'].name} ({stats['worst_student'].average():.2f})")

            elif choice == "8":
                n = int(input("ТОП-N: "))
                exportFilename = input("Имя файла для экспорта с расширением csv (по умолчанию top.csv): ") or "top.csv"
                exportTopNtoCSV(exportFilename, manager.students, n)
                print(f"ТОП-{n} экспортирован в {exportFilename}")

            elif choice == "9":
                by = input("Сортировать по (id/name/avg): ").strip().lower()
                manager.sortStudents(by)
                print("Сортировка выполнена.")

            elif choice == "0":
                print("Выход.")
                break

            else:
                print("Неверный выбор.")

        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()