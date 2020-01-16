import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from hakaze import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("UVICORN_HOST", "0.0.0.0"),
        port=int(os.getenv("UVICORN_PORT", "8080")),
        log_level="info",
    )
