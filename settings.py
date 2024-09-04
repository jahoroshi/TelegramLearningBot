import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# BASE_URL = 'http://localhost:8000' # Uncomment to set a local base URL directly

# Get the BASE_URL from environment variables
BASE_URL = f'http://{os.getenv("BASE_URL")}'
SERVER_URL = f'http://{os.getenv("SERVER_URL")}'
