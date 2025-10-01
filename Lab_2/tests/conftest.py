import pytest
from lab.models import Student

@pytest.fixture
def sample_students():
    """Фикстура: список студентов для тестов."""
    return [
        Student(1, "Иванов Иван", [78, 85, 90]),
        Student(2, "Петров Петр", [65, 70, 0]),
        Student(3, "Сидорова Анна", [92, 88, 95]),
        Student(4, "Кузнецов Олег", [100, 90]),
        Student(5, "Васильева Юлия", [80]),
    ]