from openai import OpenAI 
from typing import List
from dotenv import load_dotenv
import shutil

load_dotenv()
model = OpenAI()

# to be replaced with chunking code
def chunk_code(code: str, lines_per_chunk: int = 20) -> List[str]:
    """Split code into chunks of specified number of lines"""
    lines = code.split('\n')
    return ['\n'.join(lines[i:i+lines_per_chunk]) 
            for i in range(0, len(lines), lines_per_chunk)]

#to be replaced with prompt for each chunk
def call_llm(chunk: str, context: str) -> str:
    """Call the LLM with chat format"""
    messages = [
        {
            "role": "system", 
            "content": "You are an Angular developer migrating code from to 7 to 15."
        },
        {
            "role": "user", 
            "content": (
                f"Context from previous migration:\n{context}\n\n"
                f"Migrate this code chunk:\n{chunk}"
            )
        }
    ]
    
    response = model.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
        max_tokens=2000
    )
    return response.choices[0].message.content.strip()


def update_code_from_text(code_path: str, output_path: str = None) -> str:
    """Update Angular code from a text input and optionally write to a .ts file."""
    chunks = chunk_code(code_text) #get list of all chunks
    updated_chunks = [] #stores updated chunks
    context = "" #stores context
    
    for chunk in chunks:
        updated_chunk = call_llm(chunk, context) # gets updated chunk from llm
        updated_chunks.append(updated_chunk) # appends it to get entire chunk
        context += "\n" + updated_chunk  # Accumulate context for subsequent chunks
    
    updated_code = '\n'.join(updated_chunks) #joins all the code together
    
    if output_path: 
        with open(output_path, 'w') as file:
            file.write(updated_code)

    update_code_from_text(, 'angular_15.ts')