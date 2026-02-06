from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
MONGODBURI=os.getenv("MONGODB_URL")
if API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set")
collection_name="doctors"
collection_name2="appointments"
MONGODB_DB_NAME="medical_office"
Model_name = "gpt-4o-mini"