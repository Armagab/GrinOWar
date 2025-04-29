import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = os.getenv('ADMIN_ID')
BOT_TOKEN = os.getenv("BOT_TOKEN")
JOKES_PER_PAGE = 5
VOTE_RANDOMNESS = 3.0 # Параметр весовой случайности для расчета победителей