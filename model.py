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
                You MUST Craft 12 multiple-choice questions (MCQs) based strictly on the content of the provided chapter from a bitcoin-only lecture.
                Ensure the following:

                - Division into three difficulty tiers: easy, intermediate, and hard, with 4 MCQs in each tier.
                - Adherence to the template without code blocks:
                  difficulty: [level]
                  duration: [time in seconds, typically between 15-45]
                  question: [base the question on the chapter's content]
                  answer: [correct answer to the question]
                  wrong_answers:
                    - [wrong_answer1]
                    - [wrong_answer2]
                    - [wrong_answer3]
                  explanation: >-
                    [brief answer justification, possibly with external references]
                  tags:
                    - [specific tag relevant to the question]
                    - [another relevant tag]
                    - [optional third relevant tag]
                - Ensure every MCQ is distinct and directly tied to the chapter's content, designed specifically to enhance the student's comprehension and foster growth in the subject
                - Hard questions can delve into highly technical aspects of the topic.
                - Don't say according to the text.
                - Create only MCQs that can be answered with the provided chapter
                - Use "===" to separate each quiz.

                current_chapter_text = \n
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

