from course import Course
from model import OpenaiQuizzMakerModel
from view import ViewCLI
import os
import time
import yaml
import textwrap

class MyDumper(yaml.Dumper):
    # Increase the indentation for lists
    increase_indent = lambda self, flow, indentless=False: super(MyDumper, self).increase_indent(flow, False)

class Controller():
    def __init__(self):

        self.view = ViewCLI()

        self.folder_to_course_path = self.view.get_folder_to_course_path()
        self.input_subfolder_name = os.path.basename(self.folder_to_course_path)
        self.raw_course = self.read_course()
        self.course = Course(self.raw_course)
        self.current_chapter_text = ""

        # next variables could be in a class of its own
        self.QUIZZ_INDEX = self.view.get_initial_quizz_index()
        self.yml_quizz_path = ""
        self.yml_quizzes = ""
        self.yml_quizz = ""

        self.NUM_CHAPTERS = len(self.course.chapters)

        self.start_time = time.time()
        self.processing_times = []
        self.index = 0

        self.model = None # A model is instanciated for each chapter

    def read_course(self):
        with open(os.path.join(self.folder_to_course_path, 'en.md'), 'r') as file:
            return file.read()

    def create_course_based_quizzes(self):

        for chapter in self.course.chapters:
            self.load_chapter()
            self.load_quizz_maker_model()
            self.batch_quizz_creation_of_current_chapter()


    def load_chapter(self):
        self.course.current_chapter = self.course.chapters[self.index]
        self.current_chapter_text = self.course.current_chapter['text']



    def load_quizz_maker_model(self):
        self.model = OpenaiQuizzMakerModel()


    def batch_quizz_creation_of_current_chapter(self):

        self.view.update_progress_bar(self.index, self.NUM_CHAPTERS)
        section_index = self.course.get_current_section_index()
        chapter_index = self.course.get_current_chapter_index()
        message = f'Quizz Creation for Chapter {section_index}.{chapter_index}'
        self.view.work_in_progress(message)

        self.yml_quizzes = self.model.get_yml_quizzes_from_(self.current_chapter_text)
        self.format_yml_quizzes()
        self.extract_yml_quizz()

        self.view.work_done(message)
        self.update_processing_times()
        self.estimate_remaining_time()

    def format_yml_quizzes(self):

        self.split_quizzes()
        self.remove_unnecessary_newlines()
        self.reorganize_yml_properties()

    def split_quizzes(self):
        self.yml_quizzes = self.yml_quizzes.split('\n\n')

    def remove_unnecessary_newlines(self):
        self.yml_quizzes = [quiz.strip() for quiz in self.yml_quizzes if quiz.strip()]

    def reorganize_yml_properties(self):
        reorganised_quizzes = []

        for quiz_str in self.yml_quizzes:

            quiz = yaml.safe_load(quiz_str)

            reorganised_quiz = {
                'course': self.input_subfolder_name,
                'part': self.course.get_current_section_index(),
                'chapter': self.course.get_current_chapter_index(),
                'difficulty': quiz['difficulty'],
                'duration': quiz['duration'],
                'author': 'DecouvreBitcoin',
                'tags': quiz['tags'],
                'question': quiz['question'],
                'answer': quiz['answer'],
                'wrong_answers': quiz['wrong_answers'],
                'explanation': quiz['explanation'],
                'reviewed': False
            }

            reorganised_quiz_str = yaml.dump(reorganised_quiz, Dumper=MyDumper, sort_keys=False, default_flow_style=False)

            # Post-process for `explanation` field
            lines = reorganised_quiz_str.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("explanation:"):
                    # Replace the start of the explanation
                    lines[i] = "explanation: |"
                    # Extract the actual explanation content (without the key)
                    explanation_content = line[len("explanation: "):]
                    # Split it into lines (based on space separation)
                    wrapped_lines = textwrap.wrap(explanation_content, width=76) # assuming max width of 80 with 2 space indentation and ">- "
                    # Add 2 spaces to every line of the explanation text and join it
                    indented_wrapped_lines = ['  ' + wl for wl in wrapped_lines]
                    # Replace the current line with the new formatted lines
                    lines[i] = lines[i] + '\n' + '\n'.join(indented_wrapped_lines)
                    break  # Assuming there's only one "explanation" key per quiz

            reorganised_quiz_str = '\n'.join(lines)

            reorganised_quizzes.append(reorganised_quiz_str)

        self.yml_quizzes = reorganised_quizzes

    def extract_yml_quizz(self):
        for yml_quizz in self.yml_quizzes:
            self.yml_quizz = yml_quizz
            self.create_yml_quizz_path()
            if not self.check_existence_of_current_quizz_index():
                self.save_yml_quizz()
            self.update_quizz_index()

    def create_yml_quizz_path(self):
        quizz_index_string = self.quizz_index_to_string()
        self.yml_quizz_path = f"./outputs/{self.input_subfolder_name}/{quizz_index_string}.yml"

    def check_existence_of_current_quizz_index(self):
        return os.path.exists(self.yml_quizz_path)

    def save_yml_quizz(self):
        self.create_destination_if_needed()
        with open(self.yml_quizz_path, "w", encoding="utf-8") as f:
            f.write(self.yml_quizz)

    def update_quizz_index(self):
        self.QUIZZ_INDEX += 1

    def quizz_index_to_string(self):
        quizz_index_string = "{:04}".format(self.QUIZZ_INDEX)
        return quizz_index_string


    def create_destination_if_needed(self):
        destination = f"./outputs/{self.input_subfolder_name}"
        os.makedirs(destination, exist_ok=True)

    def update_processing_times(self):
        end_time = time.time()
        self.processing_times.append(end_time - self.start_time)


    def estimate_remaining_time(self):
        if self.index > 0:
            average_time = self.get_average_time()
            remaining_chapters = self.NUM_CHAPTERS - (self.index + 1)
            SECONDS = average_time * remaining_chapters
            self.view.estimated_remaining_time(SECONDS)
        self.index += 1

    def get_average_time(self):
        SUM = sum(self.processing_times)
        TOTAL = len(self.processing_times)
        average_time = SUM / TOTAL
        return average_time
