from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

if API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set")
