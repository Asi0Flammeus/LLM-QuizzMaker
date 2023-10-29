import os
import time
import openai
import tiktoken
from dotenv import load_dotenv
from openai.error import RateLimitError, Timeout, APIError, ServiceUnavailableError

class OpenaiQuizzMakerModel:
    """
    This class provide the methods for using a LLM specifically for Quizz Creation.
    """
    def __init__(self):

        yml_quizzes = ""
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model_engine = "gpt-4"
        self.error_handler = APIErrorHandler()

        self.pre_prompt = ("""
                        Craft 9 MCQs from the provided bitcoin-only lecture chapter:

                        Guidelines:
                        - Three difficulty tiers: hard, intermediate, easy (3 MCQs each).
                        - Each MCQ should promote understanding and exploration.
                        - Questions must be unique and chapter-derived though not example-based.
                        - Clear, unambiguous answers are essential.
                        - No ":" or quotation marks in MCQ content.
                        - Two blank lines between quizzes.
                        - For hard questions, delve into technical details.

                        MCQ Template:
                        difficulty: [level]
                        duration: [15-45] (in seconds)
                        question: [from chapter]
                        answer: [correct answer]
                        wrong_answers:
                          - [wrong1]
                          - [wrong2]
                          - [wrong3]
                        explanation: [justification with references if needed]
                        tags:
                          - [topic tag]
                          - [relevant tag]
                          - [optional tag]


                        Chapter Content:\n
                    """)

        self.temperature = 0.1

    def get_yml_quizzes_from_(self, current_chapter_text):
        try:
            current_prompt = self.pre_prompt + current_chapter_text
            return self.get_response_from_OpenAI_API_with(current_prompt)
        except Exception as e:
            self.error_handler.handle_error(e)
            return self.get_yml_quizzes_from_(current_chapter_text)

    def get_response_from_OpenAI_API_with(self, current_prompt):
        response = openai.ChatCompletion.create(
            model = self.model_engine,
            messages=[
                {"role": "user", "content": current_prompt}
            ],
            temperature=self.temperature
        )
        return response['choices'][0]['message']['content']


class APIErrorHandler:
    def __init__(self):
        self.error_handlers = {
            RateLimitError: "Rate limit",
            Timeout: "Timeout",
            APIError: "API",
            ServiceUnavailableError: "Service Unavailable",
        }
        self.sleep_time = 5

    def handle_error(self, error):
        error_type = type(error)
        error_message = self.error_handlers.get(error_type, f"{error}")
        print(f"An {error_message} error occured. Retry in {self.sleep_time} seconds...")
        time.sleep(self.sleep_time)

