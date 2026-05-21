from dotenv import load_dotenv
import os
load_dotenv()
print("KEY:", os.getenv("GROQ_API_KEY"))

from utils.api import get_ai_response
print(get_ai_response("Say hello in one sentence."))