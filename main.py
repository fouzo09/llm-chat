from openai import OpenAI, APIError
from dotenv import load_dotenv
import os
import gradio as gr
from pathlib import Path

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL")
INSTRUCT_PROMPT = os.getenv("INSTRUCT_PROMPT")
JAVA_EXPERT_INSTRUCT_PROMPT = Path("prompts/JAVA_EXPERT_INSTRUCT_PROMPT.md").read_text(encoding="utf-8")

open_ai_client = OpenAI()


def ask_gpt(message):
    """Envoie la conversation au modele GTP et renvoie une reponse"""
    stream = open_ai_client.responses.create(
        model=OPENAI_MODEL,
        instructions=JAVA_EXPERT_INSTRUCT_PROMPT,
        input=message,
        stream=True
    )
    for response in stream:
        if response.type == "response.output_text.delta":
            yield response.delta

if __name__ == "__main__":
    history = []
    while True:
        try:
            question = input("Ask something : ")
        except(KeyboardInterrupt, EOFError):
            break
        if not question:
            break


        history.append({"role": "user", "content": question})
        response = ""
        
        try:
            for chunck in ask_gpt(history):
                response += chunck
                print(chunck, end="", flush=True)
            history.append({"role": "user", "content": response})
        except APIError as e:
            print(f"OpenAI error {e.message}")
            history.pop()
            continue
        print()
            