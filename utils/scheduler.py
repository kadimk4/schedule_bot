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