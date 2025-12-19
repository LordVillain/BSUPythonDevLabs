import asyncio
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from config import COURSES, DAYS_SEARCH_MAP, DAYS_REVERSE
from states import AppStates
import services as srv
import keyboards as kb

router = Router()

# старт
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    del_msg = await message.answer("...", reply_markup=ReplyKeyboardRemove())
    await del_msg.delete()
    await message.answer("👋 <b>Главное меню</b>", reply_markup=kb.kb_courses_menu(), parse_mode="HTML")

@router.callback_query(F.data == "start_menu")
async def cb_start_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("👋 <b>Главное меню</b>", reply_markup=kb.kb_courses_menu(), parse_mode="HTML")

# добавление курса
@router.callback_query(F.data == "add_new_course")
async def cb_add_course(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✍️ Введите <b>название</b> курса:", parse_mode="HTML")
    await state.set_state(AppStates.waiting_for_course_name)

@router.message(StateFilter(AppStates.waiting_for_course_name))
async def process_course_name(message: Message, state: FSMContext):
    await state.update_data(c_name=message.text)
    await message.answer("🔗 Отправьте <b>ссылку</b> на Google таблицу:")
    await state.set_state(AppStates.waiting_for_course_link)

@router.message(StateFilter(AppStates.waiting_for_course_link))
async def process_course_link(message: Message, state: FSMContext):
    link = message.text
    sheet_match = re.search(r"/d/([a-zA-Z0-9-_]+)", link)
    gid_match = re.search(r"[#&]gid=([0-9]+)", link)
    if not sheet_match:
        await message.answer("❌ Ссылка некорректна.")
        return
    data = await state.get_data()
    new_id = f"c{len(COURSES) + 1}"
    COURSES[new_id] = {
        "name": data['c_name'],
        "sheet_id": sheet_match.group(1),
        "gid": gid_match.group(1) if gid_match else "0"
    }
    await state.clear()
    await message.answer(f"✅ Курс <b>{data['c_name']}</b> добавлен!", reply_markup=kb.kb_courses_menu(), parse_mode="HTML")

# навигация
@router.callback_query(F.data.startswith("sel_course:"))
async def cb_sel_course(callback: CallbackQuery):
    c_id = callback.data.split(":")[1]
    # Загружаем данные (или берем из кэша)
    await callback.message.edit_text("⏳ Загрузка...")
    loop = asyncio.get_event_loop()
    df, structure = await loop.run_in_executor(None, srv.get_cached_data, c_id)
    
    if df is None:
        await callback.message.edit_text("❌ Ошибка загрузки.", reply_markup=kb.kb_courses_menu())
        return
    await callback.message.edit_text(f"📂 Курс: <b>{COURSES[c_id]['name']}</b>", reply_markup=kb.kb_streams(c_id, structure), parse_mode="HTML")

@router.callback_query(F.data.startswith("str:"))
async def cb_str(callback: CallbackQuery):
    _, c_id, s_key = callback.data.split(":")
    structure = srv.STRUCTURE # Берем актуальную структуру из services
    await callback.message.edit_text("🎓 Выбери группу:", reply_markup=kb.kb_groups(c_id, s_key, structure))

@router.callback_query(F.data.startswith("grp:"))
async def cb_grp(callback: CallbackQuery):
    _, c_id, s_key, g_num = callback.data.split(":")
    structure = srv.STRUCTURE
    await callback.message.edit_text(f"🎓 Группа {g_num}. Кафедра:", reply_markup=kb.kb_depts(c_id, s_key, int(g_num), structure))

@router.callback_query(F.data.startswith("dpt:"))
async def cb_dpt(callback: CallbackQuery):
    _, c_id, s_key, g_num, col = callback.data.split(":")
    await callback.message.edit_text("🗓 День:", reply_markup=kb.kb_days(c_id, s_key, int(g_num), int(col)))

# логика парсинга для студентов
@router.callback_query(F.data.startswith("day:"))
async def cb_day_final(callback: CallbackQuery):
    parts = callback.data.split(":")
    day_code = parts[1]
    c_id = parts[2]
    stream_key = parts[3]
    group_num = int(parts[4])
    target_col = int(parts[5])
    
    await callback.answer()
    wait_msg = await callback.message.answer("⏳ ...")
    
    loop = asyncio.get_event_loop()
    df, structure = await loop.run_in_executor(None, srv.get_cached_data, c_id)
    if df is None: return

    stream_start_col = structure[stream_key]["base_col"]
    slots = {}
    days_order = []
    days_search = DAYS_SEARCH_MAP if day_code == "full" else {day_code: DAYS_SEARCH_MAP[day_code]}
    TIME_PATTERN = re.compile(r"\d{1,2}[\.:]\d{2}.*?-.*?\d{1,2}[\.:]\d{2}", re.DOTALL)

    for index, row in df.iterrows():
        if index < 15: continue
        day_str = str(row[0]).strip().lower()
        time_str = str(row[1]).strip()
        if not time_str or not TIME_PATTERN.search(time_str): continue
        
        is_day_match = False
        for d_key, d_val in days_search.items():
            if d_val in day_str:
                is_day_match = True
                break
        if not is_day_match: continue

        key = (str(row[0]).strip(), time_str)
        if key not in slots:
            slots[key] = {"target": [], "common": [], "blocked": False}
            if key[0] not in days_order: days_order.append(key[0])
        
        val_target = srv.clean_text(str(row[target_col]).strip())
        if val_target: slots[key]["target"].append(val_target)
        
        if target_col != stream_start_col:
            val_common = srv.clean_text(str(row[stream_start_col]).strip())
            if val_common: slots[key]["common"].append(val_common)
            if val_common:
                start, end = sorted((stream_start_col, target_col))
                for c in range(start + 1, end):
                    check_val = str(row[c]).strip()
                    if check_val and any(c.isalpha() for c in check_val):
                        slots[key]["blocked"] = True
                        break

    response_text = f"📅 <b>{COURSES[c_id]['name']}</b>\n"
    has_pairs = False
    
    for day in days_order:
        day_content = ""
        for (d, t), data in slots.items():
            if d != day: continue
            
            final_parts = []
            is_stream = False
            has_own_subject = any(srv.is_real_subject(x) for x in data["target"])
            final_parts.extend(data["target"])
            
            if not has_own_subject and not data["blocked"]:
                full_common = " ".join(data["common"]).lower()
                if "д/с" not in full_common:
                    for item in data["common"]:
                        if item not in final_parts:
                            final_parts.append(item)
                            is_stream = True
            
            unique = sorted(list(set(final_parts)), key=lambda x: not srv.is_real_subject(x))
            
            if unique:
                clean_time = t.replace("\n", " ").strip()
                subj = [x for x in unique if srv.is_real_subject(x)]
                room = [x for x in unique if not srv.is_real_subject(x)]
                block = f"🕒 <b>{clean_time}</b>\n"
                if subj: block += f"📚 <b>{subj[0]}</b>" + (f"\n👤 {', '.join(subj[1:])}" if len(subj)>1 else "")
                if room: block += f"\n📍 {', '.join(room)}"
                if is_stream: block += " <i>(Поток)</i>"
                day_content += block + "\n─────────────────\n"
        
        if day_content:
            has_pairs = True
            response_text += f"\n🗓 <b>{day.upper()}</b>\n\n{day_content}"

    await wait_msg.delete()
    if not has_pairs:
        await callback.message.answer("🏖 Пар нет.", reply_markup=kb.kb_days(c_id, stream_key, group_num, target_col))
    else:
        await callback.message.answer(response_text[:4000], parse_mode="HTML", reply_markup=kb.kb_days(c_id, stream_key, group_num, target_col))

# для преподавателей
@router.callback_query(F.data == "find_teacher")
async def cb_find_teach(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✍️ Введите фамилию преподавателя:")
    await state.set_state(AppStates.waiting_for_teacher)

@router.message(StateFilter(AppStates.waiting_for_teacher))
async def process_teach_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.clear()
    await message.answer(f"🔎 Где искать <b>{name}</b>?", reply_markup=kb.kb_teacher_search_scope(name), parse_mode="HTML")

@router.callback_query(F.data.startswith("t_scope:"))
async def cb_t_scope(callback: CallbackQuery):
    parts = callback.data.split(":")
    scope = parts[1]
    name = parts[2]
    await callback.message.edit_text(f"🗓 День для <b>{name}</b>:", reply_markup=kb.kb_teacher_days(scope, name), parse_mode="HTML")

@router.callback_query(F.data.startswith("t_res:"))
async def cb_t_res(callback: CallbackQuery):
    parts = callback.data.split(":")
    day_code = parts[1]
    scope = parts[2]
    teacher_name = ":".join(parts[3:])
    await callback.answer()
    
    wait_msg = await callback.message.answer(f"🔎 Ищу <b>{teacher_name}</b>...", parse_mode="HTML")
    days_search = DAYS_SEARCH_MAP if day_code == "full" else {day_code: DAYS_SEARCH_MAP[day_code]}
    courses_to_search = list(COURSES.keys()) if scope == "all" else [scope]
    
    final_results = {}
    
    for c_id in courses_to_search:
        # Логика поиска
        loop = asyncio.get_event_loop()
        df, structure = await loop.run_in_executor(None, srv.get_cached_data, c_id)
        if df is None: continue
        
        query = teacher_name.lower()
        TIME_PATTERN = re.compile(r"\d{1,2}[\.:]\d{2}.*?-.*?\d{1,2}[\.:]\d{2}", re.DOTALL)
        
        # Сбор временных слотов
        temp_slots = {}
        for index, row in df.iterrows():
            if index < 15: continue
            time_str = str(row[1]).strip()
            day_str = str(row[0]).strip().lower()
            if not time_str or not TIME_PATTERN.search(time_str): continue
            
            is_match = False
            for d_val in days_search.values():
                if d_val in day_str: is_match = True
            if not is_match: continue
            
            key_base = (str(row[0]).strip(), time_str)
            for col_idx in range(2, len(row)):
                val = str(row[col_idx]).strip()
                if val:
                    full_key = (key_base[0], key_base[1], col_idx)
                    if full_key not in temp_slots: temp_slots[full_key] = []
                    temp_slots[full_key].append(val)
        
        # Поиск совпадений
        for (day, time, col_idx), content in temp_slots.items():
            full_text = " ".join(content).lower()
            if query in full_text:
                grp_name = "???"
                for s_key in structure:
                    if col_idx in structure[s_key]["col_names"]:
                        grp_name = structure[s_key]["col_names"][col_idx]
                        break
                
                parts = []
                room = ""
                for item in content:
                    cleaned = srv.clean_text(item)
                    if not cleaned: continue
                    if not srv.is_real_subject(cleaned): room = cleaned
                    else: parts.append(cleaned)
                
                lesson_str = ", ".join(parts)
                if room: lesson_str += f", 📍 {room}"
                lesson_str += f" [🎓 {grp_name}]"
                
                if day not in final_results: final_results[day] = {}
                if time not in final_results[day]: final_results[day][time] = []
                
                final_item = lesson_str
                if scope == "all": final_item += f" <i>({COURSES[c_id]['name']})</i>"
                final_results[day][time].append(final_item)

    response = f"👤 <b>{teacher_name}</b>\n"
    has_data = False
    sorted_days = sorted(final_results.keys(), key=lambda d: list(DAYS_SEARCH_MAP.values()).index(d.lower()) if d.lower() in list(DAYS_SEARCH_MAP.values()) else 99)
    
    for day in sorted_days:
        day_block = f"\n🗓 <b>{day.upper()}</b>\n"
        times = sorted(final_results[day].keys())
        for t in times:
            clean_time = t.replace("\n", " ").strip()
            day_block += f"🕒 <b>{clean_time}</b>\n"
            for l in final_results[day][t]: day_block += f"🔹 {l}\n"
            day_block += "\n"
        response += day_block
        has_data = True

    await wait_msg.delete()
    if not has_data:
        await callback.message.answer("🤷‍♂️ Не найдено.", reply_markup=kb.kb_teacher_days(scope, teacher_name))
    else:
        await callback.message.answer(response[:4000], parse_mode="HTML", reply_markup=kb.kb_teacher_days(scope, teacher_name))