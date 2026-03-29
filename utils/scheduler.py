import json
from datetime import datetime, timedelta
from utils.config import settings

def get_schedule_for_day(is_tomorrow: bool = False) -> str:
    target_date = datetime.now()
    if is_tomorrow:
        target_date += timedelta(days=1)
    
    day_name = target_date.strftime("%A")
    
    try:
        with open(settings.schedule_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        day_data = data.get(day_name, [])
        
        if not day_data:
            return f"📅 {day_name}: Занятий нет или расписание не заполнено."
        
        prefix = "Завтра" if is_tomorrow else "Сегодня"
        return f"📅 {prefix} ({day_name}):\n" + "\n".join(day_data)
        
    except FileNotFoundError:
        return "Ошибка: Файл расписания не найден."
    
def get_current_and_next_lessons():
    now = datetime.now().time()
    day_name = datetime.now().strftime("%A")
    
    try:
        with open(settings.schedule_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        today_lessons = data.get(day_name, [])
        if not today_lessons or "Выходной" in today_lessons[0]:
            return "Сегодня выходной, пар нет! 🎉", None

        current = None
        next_l = None

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

                    if i + 1 < len(today_lessons):
                        next_l = today_lessons[i+1]
                    break
                
                if now < start_time:
                    next_l = lesson
                    break
            except ValueError:
                continue

        return current, next_l

    except Exception as e:
        print(f"Ошибка в scheduler'e: {e}",)
        return None, None