import requests
import os
from groq import Groq
from fastapi import HTTPException

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not set.")
    
client = Groq(api_key=api_key)
    

def read_prompt_file(prompt_file_path='prompt.txt'):
    if not os.path.exists(prompt_file_path):
        return "Default system prompt if file not found."
    
    try:
        with open(prompt_file_path, 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return "Default system prompt if file not found."
    except FileNotFoundError:
        return "Default system prompt if file not found."

def chat_content_api(user_message, system_prompt_override=None):
    try:
        if system_prompt_override:
            system_prompt = system_prompt_override
        else:
            system_prompt = read_prompt_file()
           
        print(f"System prompt: {system_prompt}")
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
            ],
            temperature=0.7,
            max_tokens=1024
        )

        return completion.choices[0].message.content
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq API: {e}")
        return None

'''
GET /chat?query=What is the capital of France?
'''
def test_groq_get(query: str):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": query
            }],
            temperature=0.7,
            max_tokens=1024
        )
        
        return {
            "status": "success",
            "response": completion.choices[0].message.content
        }
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq API: {e}")
        raise HTTPException(status_code=500, detail="Network issue or invalid API key.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Example usage
    user_message = "Write a hello world program in Python"
    response = call_groq_api(user_message)
    if response:
        print("Groq Response:", response)