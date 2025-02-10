from openai import OpenAI 
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
model = OpenAI()

def chunk_code(code: str, lines_per_chunk: int = 20) -> List[Dict]:
    """
    Split code into chunks of a specified number of lines,
    and assign each chunk an ID.
    Returns a list of dictionaries with keys "id" and "code".
    """
    lines = code.splitlines()
    chunks = []
    for i in range(0, len(lines), lines_per_chunk):
        chunk_id = i // lines_per_chunk
        chunk_text = '\n'.join(lines[i:i+lines_per_chunk])
        chunks.append({"id": chunk_id, "code": chunk_text})
    return chunks

def call_llm(chunks: List[Dict]) -> str:
    """
    Call the LLM with a prompt containing all code chunks.
    The prompt instructs the LLM to upgrade the Angular code from version 7 to 15,
    and to output only the upgraded chunk for each chunk ID.
    
    The expected response format is:
    
      Chunk 0:
      <upgraded code>
      
      Chunk 1:
      <upgraded code>
      
    The system instructs the LLM to include a final line that reads '---End of Output---'
    when it has finished outputting all the necessary chunks. If that termination marker
    is not present in the response, the function appends the output as an assistant message,
    sends a follow-up user message requesting the remaining content, and repeats until complete.
    """
    # Build the initial prompt containing all chunks.
    chunks_text = ""
    for chunk in chunks:
        chunks_text += f"Chunk {chunk['id']}:\n{chunk['code']}\n\n"

    # Create the conversation history with system and initial user message.
    messages = [
        {
            "role": "system",
            "content": (
                "You are an experienced Angular developer tasked with upgrading Angular code "
                "from version 7 to version 15. For each provided code chunk (identified by its chunk id), "
                "analyze the code and determine if any changes are needed. If the code requires an upgrade, "
                "output only the upgraded code along with its corresponding chunk id using the exact format below:\n\n"
                "Chunk <id>:\n<upgraded code>\n\n"
                "If no changes are needed in a chunk, do not output anything for that chunk. "
                "Do not include any commentary or extra text. "
                "When you have output all required chunks, please include a final line that reads "
                "'---End of Output---'."
            )
        },
        {
            "role": "user",
            "content": f"Here are the code chunks:\n\n{chunks_text}"
        }
    ]
    
    full_response = ""
    complete = False

    while not complete:
        # Call the LLM with the entire conversation history.
        response = model.chat.completions.create(
            model="gpt-4o",  # Replace with the correct model name.
            messages=messages,
        )
        answer = response.choices[0].message.content.strip()
        
        # Append the answer to the overall response.
        full_response += "\n" + answer
        
        # Explicitly add the LLM's output as an assistant message to the conversation.
        messages.append({
            "role": "assistant",
            "content": answer
        })

        # Check if the termination marker is present.
        if '---End of Output---' in answer:
            complete = True
        else:
            # Add a follow-up user message asking for the rest of the content.
            messages.append({
                "role": "user",
                "content": (
                    "It appears your previous response was truncated. "
                    "Please continue outputting the rest of the upgraded code chunks in the same format, "
                    "without repeating the previous content."
                )
            })

    # Remove the termination marker before returning.
    full_response = full_response.replace('---End of Output---', '').strip()
    return full_response

def update_code(file_path: str, output_path: str = None, lines_per_chunk: int = 20) -> str:
    """
    Read the Angular code from a file, split it into numbered chunks,
    send all the chunks at once to the LLM to get an upgraded version,
    and then optionally write the upgraded code (with chunk ids) to an output file.
    
    The response will include upgraded code along with the corresponding chunk IDs.
    """
    with open(file_path, 'r') as file:
        code = file.read()
    
    # Split code into chunks with an associated id.
    chunks = chunk_code(file_path, lines_per_chunk=lines_per_chunk)
    
    # Call the LLM once with all chunks as input.
    upgraded_response = call_llm(chunks)
    
    if output_path:
        with open(output_path, 'w') as file:
            file.write(upgraded_response)
    
    return upgraded_response


updated_code = update_code('angular_7.ts', 'angular_15.ts')
print(updated_code)