BOT_TOKEN = "8028619716:AAF_pbIXjJ2hAxg9vXr427GV7fMxXms2QXM"

# Список курсов по умолчанию
COURSES = {
    "c1": {
        "name": "3 курс (ФПМИ)",
        "sheet_id": "14-YxxIaNrIohX5QwtQRgPARvj0LbMHLQ",
        "gid": "1243294014"
    }
}

# Дни недели (код -> название)
DAYS_REVERSE = {
    "mon": "Понедельник", "tue": "Вторник", "wed": "Среда",
    "thu": "Четверг", "fri": "пятница", "sat": "суббота"
}

# Словарь для поиска (все в нижнем регистре)
DAYS_SEARCH_MAP = {k: v.lower() for k, v in DAYS_REVERSE.items()}