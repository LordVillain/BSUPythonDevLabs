class StudentError(Exception):
    """Базовый класс для всех ошибок студентов"""
    pass

class StudentNotFoundError(StudentError):
    pass

class DuplicateStudentError(StudentError):
    pass

class InvalidGradeError(StudentError):
    pass

class InvalidDataError(StudentError):
    pass

class FileError(StudentError):
    pass