import os
from dotenv import load_dotenv
load_dotenv()

# BASE_URL = 'http://localhost:8000' # не добавлять закрывающий /
BASE_URL = os.getenv("BASE_URL")
