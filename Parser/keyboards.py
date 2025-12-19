from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import COURSES, DAYS_REVERSE
import services

def kb_courses_menu():
    buttons = []
    for c_id, c_data in COURSES.items():
        buttons.append([InlineKeyboardButton(text=f"📅 {c_data['name']}", callback_data=f"sel_course:{c_id}")])
    buttons.append([InlineKeyboardButton(text="🔎 Найти преподавателя", callback_data="find_teacher")])
    buttons.append([InlineKeyboardButton(text="➕ Добавить курс", callback_data="add_new_course")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kb_streams(course_id, structure):
    buttons = []
    for s_key in sorted(structure.keys()):
        name = structure[s_key]["name"].split("(")[0][:30].strip()
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"str:{course_id}:{s_key}")])
    buttons.append([InlineKeyboardButton(text="🔙 К выбору курса", callback_data="start_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kb_groups(course_id, stream_key, structure):
    if stream_key not in structure: return None
    groups = sorted(structure[stream_key]["groups"])
    buttons = []
    row = []
    for g in groups:
        row.append(InlineKeyboardButton(text=f"{g} гр.", callback_data=f"grp:{course_id}:{stream_key}:{g}"))
        if len(row) == 3: 
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"sel_course:{course_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kb_depts(course_id, stream_key, group_num, structure):
    try:
        depts = structure[stream_key]["col_map"][group_num]
    except KeyError: return None
    buttons = []
    row = []
    for d_name, col_idx in depts.items():
        btn_txt = "Общая" if not d_name or "Подгр" in d_name else d_name[:20]
        row.append(InlineKeyboardButton(text=btn_txt, callback_data=f"dpt:{course_id}:{stream_key}:{group_num}:{col_idx}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"str:{course_id}:{stream_key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kb_days(course_id, stream_key, group_num, col_idx):
    buttons = []
    row = []
    for code, name in DAYS_REVERSE.items():
        row.append(InlineKeyboardButton(text=name, callback_data=f"day:{code}:{course_id}:{stream_key}:{group_num}:{col_idx}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton(text="📅 Вся неделя", callback_data=f"day:full:{course_id}:{stream_key}:{group_num}:{col_idx}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"grp:{course_id}:{stream_key}:{group_num}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kb_teacher_search_scope(teacher_name):
    buttons = [[InlineKeyboardButton(text="🌍 Во всех курсах", callback_data=f"t_scope:all:{teacher_name}")]]
    for c_id, c_data in COURSES.items():
        buttons.append([InlineKeyboardButton(text=f"📂 Только {c_data['name']}", callback_data=f"t_scope:{c_id}:{teacher_name}")])
    buttons.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="start_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def kb_teacher_days(scope, teacher_name):
    buttons = []
    row = []
    safe_name = teacher_name[:15]
    for code, name in DAYS_REVERSE.items():
        row.append(InlineKeyboardButton(text=name, callback_data=f"t_res:{code}:{scope}:{safe_name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton(text="📅 Вся неделя", callback_data=f"t_res:full:{scope}:{safe_name}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="find_teacher")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)