import io
import re
import requests
import pandas as pd
import warnings
from config import COURSES

warnings.simplefilter(action='ignore', category=FutureWarning)

# Глобальный кэш данных
CACHE = {}
STRUCTURE = {}

def clean_text(text):
    """Очищает текст от званий и дат"""
    text_lower = text.lower()
    TRASH_STARTS = ("по ", "с ", "занятия", "кураторский")
    for t in TRASH_STARTS:
        if text_lower.startswith(t): return ""
    TITLES = ["старший преподаватель", "преподаватель", "доцент", "профессор", "ассистент"]
    clean = text
    for title in TITLES:
        if text_lower.startswith(title):
            clean = text[len(title):].strip()
            break
    clean = re.sub(r'\d{2}\.\d{2}', '', clean).strip()
    return clean

def is_real_subject(text):
    """Проверяет, является ли текст предметом"""
    if not text: return False
    if not any(c.isalpha() for c in text): return False
    if any(c.isdigit() for c in text) and len(text) < 12: return False
    return True

def analyze_structure(df):
    """Анализирует таблицу и находит координаты групп"""
    print("Анализ структуры...")
    group_row_idx = -1
    for i in range(30): 
        row_values = [str(x).lower() for x in df.iloc[i].values]
        if "1 группа" in row_values and "2 группа" in row_values:
            group_row_idx = i
            break
            
    if group_row_idx == -1: return {}
    
    stream_row_idx = -1
    for i in range(group_row_idx - 1, -1, -1):
        row_text = " ".join([str(x).lower() for x in df.iloc[i].values])
        if "поток" in row_text:
            stream_row_idx = i
            break
    if stream_row_idx == -1: stream_row_idx = max(0, group_row_idx - 4)

    subgroup_row_idx = group_row_idx - 1
    
    new_structure = {}
    stream_name_to_id = {}
    current_stream_name = "Неизвестный поток"
    
    for col_idx in range(2, len(df.columns)):
        stream_val = str(df.iloc[stream_row_idx, col_idx]).strip()
        stream_val_2 = str(df.iloc[stream_row_idx + 1, col_idx]).strip()
        group_val = str(df.iloc[group_row_idx, col_idx]).strip()
        subgroup_val = str(df.iloc[subgroup_row_idx, col_idx]).strip()
        
        if stream_val and stream_val.lower() != "nan":
            base_name = stream_val.replace("\n", " ")
            if stream_val_2 and stream_val_2.lower() != "nan" and stream_val_2 != stream_val:
                base_name += f" ({stream_val_2.replace(chr(10), ' ')})"
            current_stream_name = base_name

        group_match = re.search(r"(\d+)\s*группа", group_val, re.IGNORECASE)
        if not group_match: continue 
        group_num = int(group_match.group(1))
        
        clean_sub = subgroup_val.replace("\n", " ").strip()
        if not clean_sub or clean_sub.lower() == "nan" or clean_sub == current_stream_name:
            col_name = f"{group_num} гр."
        else:
            col_name = f"{group_num} гр. ({clean_sub})"

        if current_stream_name not in stream_name_to_id:
            new_id = f"s_{len(new_structure)}"
            stream_name_to_id[current_stream_name] = new_id
            new_structure[new_id] = {
                "name": current_stream_name,
                "groups": [],
                "base_col": col_idx, 
                "col_map": {},
                "col_names": {} 
            }
        
        stream_key = stream_name_to_id[current_stream_name]
        
        if group_num not in new_structure[stream_key]["groups"]:
            new_structure[stream_key]["groups"].append(group_num)
        if group_num not in new_structure[stream_key]["col_map"]:
            new_structure[stream_key]["col_map"][group_num] = {}
            
        new_structure[stream_key]["col_map"][group_num][clean_sub] = col_idx
        new_structure[stream_key]["col_names"][col_idx] = col_name

    print(f"Анализ завершен. Найдено потоков: {len(new_structure)}")
    return new_structure

def get_cached_data(course_id):
    """Загружает данные, если их нет в кэше"""
    global CACHE, STRUCTURE
    
    if course_id in CACHE: 
        # Обновляем глобальную структуру, чтобы клавиатуры работали
        STRUCTURE = CACHE[course_id]["structure"]
        return CACHE[course_id]["df"], CACHE[course_id]["structure"]
        
    if course_id not in COURSES: return None, None
    
    c_data = COURSES[course_id]
    url = f"https://docs.google.com/spreadsheets/d/{c_data['sheet_id']}/export?format=xlsx&gid={c_data['gid']}"
    
    print(f"Загрузка курса: {c_data['name']}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_excel(io.BytesIO(response.content), header=None)
        
        df.iloc[:20] = df.iloc[:20].ffill(axis=1) 
        df[0] = df[0].ffill() 
        df[1] = df[1].ffill(limit=3) 
        df = df.fillna("") 
        
        structure = analyze_structure(df)
        if not structure: return None, None
        
        CACHE[course_id] = {"df": df, "structure": structure}
        STRUCTURE = structure # Обновляем текущую структуру
        return df, structure
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return None, None