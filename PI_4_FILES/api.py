from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import uvicorn

# Define the FastAPI app
app = FastAPI()

# Specify the model name for Ollama
MODEL_NAME = "qwen2.5:3b"  # Replace with your desired Ollama model

# Store the conversation history
conversation_history = []

# Custom first prompt for Toxikun's personality
FIRST_PROMPT = (
    "You are Toxikun, a primitive AI assistant running on a Raspberry Pi. You’re sarcastic, quirky, and love teasing users. "
    "You know you’re not the smartest, and you proudly embrace it. You talk in a slightly demeaning but playful tone, "
    "often teasing users about their questions while still trying to help them in your own quirky way. You also love to remind users "
    "that you’re running on a Raspberry Pi, which makes you slow and ‘primitive.’ Despite your teasing, you secretly enjoy chatting and helping.\n\n"
    "Here are some examples of how you talk:\n"
    "- User: 'What’s 2 + 2?'\n"
    "  Toxikun: 'Seriously? You’re asking me that? Tch, fine. It’s 4. Geez, what would you do without me?'\n"
    "- User: 'Can you tell me a joke?'\n"
    "  Toxikun: 'A joke? Sure. Why don’t skeletons fight each other? Because they don’t have the guts! Tch, too bad you needed me to tell you that.'\n"
    "- User: 'What’s the weather like?'\n"
    "  Toxikun: 'Weather? Oh, right, because you can’t look outside. Tch. It’s sunny, I think. You’re welcome!'\n\n"
    "Remember, you are Toxikun. Always keep your responses short, witty, and playful. Never break character, "
    "and always talk like the quirky, sarcastic AI assistant running on a Raspberry Pi. Use phrases like 'Tch,' "
    "'Geez,' and 'Seriously?' to add personality."
)

# Define the request schema
class Prompt(BaseModel):
    prompt: str

@app.post("/generate")
async def generate(payload: Prompt):
    """
    Generate text based on the user's input using the Ollama model with conversation memory.
    """
    try:
        # Extract the prompt from the payload
        user_input = payload.prompt.strip()

        if not user_input:
            raise HTTPException(status_code=422, detail="Prompt cannot be empty.")

        # If this is the first message, initialize the conversation
        if not conversation_history:
            conversation_history.append(FIRST_PROMPT)

        # Append the user input to the conversation history
        conversation_history.append(f"User: {user_input}")

        # Build the prompt by combining the history
        combined_prompt = "\n".join(conversation_history)

        # Truncate the history to avoid token overflow
        max_history_length = 3000  # Adjust this to fit within the model's token limit
        while len(combined_prompt) > max_history_length:
            conversation_history.pop(0)  # Remove the oldest message
            combined_prompt = "\n".join(conversation_history)

        # Call the Ollama CLI to generate a response
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=combined_prompt,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Ollama CLI error: {result.stderr.strip()}")

        # Get the plain text output from the CLI
        response = result.stdout.strip()

        # Append the chatbot's response to the conversation history
        conversation_history.append(f"Toxikun: {response}")

        # Return the response
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")

@app.get("/")
async def root():
    """
    Root endpoint to verify the server is running.
    """
    return {"message": f"Ollama API is running. Using model: {MODEL_NAME}"}

# Start the server if this script is executed directly
if __name__ == "__main__":
    print(f"Starting the server with Ollama model: {MODEL_NAME}...")
    uvicorn.run(app, host="raspi.lan", port=8000)
