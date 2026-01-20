import argparse
import os

from call_function import available_functions, call_function
from config import MODEL_NAME
from prompts import system_prompt

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
from google.genai import types

messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
client = genai.Client(api_key=api_key)
response = None

for _ in range(20):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
        ),
    )

    if response.usage_metadata:
        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    else:
        raise RuntimeError("Google is too busy and/or stressed to deal with you.")

    if response.candidates and len(response.candidates) > 0:
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)

    function_responses = []

    if response.function_calls:
        for call in response.function_calls:
            function_call_result = call_function(call, verbose=args.verbose)
            if function_call_result.parts and len(function_call_result.parts) > 0:
                if function_call_result.parts[0].function_response:
                    if function_call_result.parts[0].function_response.response:
                        function_responses.append(function_call_result.parts[0])
                        if args.verbose:
                            print(
                                f"-> {function_call_result.parts[0].function_response.response}".replace(
                                    "\\'", "'"
                                )
                            )
        messages.append(types.Content(role="user", parts=function_responses))
    elif response.text:
        print(f"Final response:\n{response.text}")
        break
    else:
        print("No valid response received. Ending run")
        exit(1)

if response and response.text is None:
    print("Maximum iterations reached without a final responses. Ending run")
    exit(1)
