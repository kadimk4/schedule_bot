import json
from datetime import datetime, timedelta
from utils.config import settings

def get_links(is_tomorrow: bool = False) -> str:
    message = "Владелец - @username \n" \
    "doubleRR fashion demon antisocial"
    return message