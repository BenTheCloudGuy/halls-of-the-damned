import os
from openai import OpenAI

def load_prompt_instructions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def generate_response(prompt, model_name="text-davinci-003"):
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("KNOXRPG_OAI_KEY"))
    
    # Generate response using OpenAI's LLM
    response = client.completions.create(model=model_name, prompt=prompt, max_tokens=150)
    return response.choices[0].text.strip()

if __name__ == "__main__":
    prompt_file_path = os.path.join(os.path.dirname(__file__), 'prompt-instructions.txt')
    prompt_instructions = load_prompt_instructions(prompt_file_path)
    
    response = generate_response(prompt_instructions)
    print("Generated Response:")
    print(response)
