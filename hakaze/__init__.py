import logging
from dotenv import load_dotenv

load_dotenv()

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)
