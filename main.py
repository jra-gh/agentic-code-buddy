import argparse
import os

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
args = parser.parse_args()

from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
from google.genai import types

messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

# user_prompt = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."
print(f"User prompt: {args.user_prompt}")

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=messages,
)

if response.usage_metadata:
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
else:
    raise RuntimeError("Google is too busy and/or stressed to deal with you.")

print(f"Response:\n{response.text}")
