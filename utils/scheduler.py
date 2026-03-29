import json
from datetime import datetime, timedelta
from utils.config import settings

def _load_schedule_data() -> dict:
    try:
        with open(settings.schedule_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_schedule_for_day(group_name: str, is_tomorrow: bool = False, specific_day: str = None) -> str:
    target_date = datetime.now() + timedelta(days=1 if is_tomorrow else 0)
    day_name = specific_day or target_date.strftime("%A")
    
    data = _load_schedule_data()
    if not data:
        return "Ошибка: Файл расписания не найден."
        
    group_data = data.get(group_name, {})
    day_data = group_data.get(day_name, [])
    
    if not day_data:
        return f"📅 {day_name} ({group_name}): Занятий нет."
    
    prefix = day_name if specific_day else ("Завтра" if is_tomorrow else "Сегодня")
    return f"📅 {prefix} для {group_name}:\n" + "\n".join(day_data)

def get_full_week_schedule(group_name: str) -> str:
    data = _load_schedule_data()
    if not data:
        return "Ошибка: Файл расписания не найден."
        
    group_data = data.get(group_name, {})
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    full_schedule = []
    for day in days_order:
        lessons = group_data.get(day, [])
        if lessons:
            full_schedule.append(f"📅 *{day}*:\n" + "\n".join(lessons))
        else:
            full_schedule.append(f"📅 *{day}*: Занятий нет.")
            
    return f"📍 Расписание группы *{group_name}* на неделю:\n\n" + "\n\n".join(full_schedule)
    
def get_current_and_next_lessons(group_name: str):
    now = datetime.now().time()
    day_name = datetime.now().strftime("%A")
    
    try:
        data = _load_schedule_data()
        group_data = data.get(group_name, {})
        today_lessons = group_data.get(day_name, [])
        
        if not today_lessons or "Выходной" in today_lessons[0]:
            return "Сегодня выходной, пар нет! 🎉", None

        current, next_l = None, None

        for i, lesson in enumerate(today_lessons):
            if " - " not in lesson:
                continue

            try:
                time_part = lesson.split(" | ")[0]
                start_str, end_str = time_part.split(" - ")
            
                start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
                end_time = datetime.strptime(end_str.strip(), "%H:%M").time()
            
                if start_time <= now <= end_time:
                    current = lesson
                    next_l = today_lessons[i+1] if i + 1 < len(today_lessons) else None
                    break
                
                if now < start_time:
                    next_l = lesson
                    break
            except ValueError:
                continue

        return current, next_l

    except Exception as e:
        print(f"Ошибка в scheduler'e: {e}")
        return None, None