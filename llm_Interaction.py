from dotenv import load_dotenv
from google import genai
from google.genai import types
from data_pipeline.embedding import search
import os

load_dotenv()

client = genai.Client(api_key=os.getenv('API-KEY'))

def query_llm(user_prompt):

    relevant_chunks = search(user_prompt, 1)
    context = "\n\n".join(relevant_chunks)

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a helpful assistant."
                    "Answer the question using ONLY the provided context."
                    "If the answer is not in the context, say you do not know."
                )
            ),
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"""
                            Context:
                            {context}

                            Question:
                            {user_prompt}
                            """
                        }
                    ]
                }
            ]
        )

        return response.text
    except Exception as e:
        print(f"An error occured when formulating response: {e}")