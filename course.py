import os
import re

class Course:
    def __init__(self, raw_course):
        self.raw_course = raw_course
        self.polished_course = ""
        self.chapters = self.format_chapters()
        print(len(self.chapters))
        self.current_chapter = ""

    def format_chapters(self):
        self.format_raw_course()
        chapters = self.create_chapters_dictionnary()
        return chapters

    def format_raw_course(self):
        self.remove_header()
        self.remove_introduction()
        self.remove_footer()

    def remove_header(self):
        header_pattern = re.compile(r'^---[\s\S]+?---\s*')
        self.polished_course = re.sub(header_pattern, '', self.raw_course)

    def remove_introduction(self):
        self.polished_course = self.polished_course.split('+++')[1]

    def remove_footer(self):
        footer_marker = "## Acknowledgments and keep digging the rabbit hole"
        self.polished_course = self.polished_course.split(footer_marker)[0]

    def create_chapters_dictionnary(self):

        chapters_dictionnary = []
        section_index = 0
        sections = self.extract_sections()

        for section in sections:
            section_index += 1
            chapter_index = 0
            chapters = self.extract_chapters_from(section)
            for chapter in chapters:
                chapter_index += 1
                chapter_dictionnary = {
                        'section_index': section_index,
                        'chapter_index': chapter_index,
                        'text': chapter
                }
                chapters_dictionnary.append(chapter_dictionnary)
        return chapters_dictionnary

    def extract_sections(self):
        sections_split = re.split(r'\n#\s[^\n]+\n', self.polished_course)
        sections = [section.strip() for section in sections_split if section.strip()]
        return sections

    def extract_chapters_from(self, section):
        chapters_split = re.split(r'\n##\s[^\n]+\n', section)
        chapters = [chapter.strip() for chapter in chapters_split if chapter.strip()]
        return chapters


    def get_current_chapter_text(self, section_index, chapter_index):
        for chapter in self.chapters:
            if chapter['section_index'] == section_index and chapter['chapter_index'] == chapter_index:
                return chapter['text']
        return None

    def get_current_section_index(self):
        return self.current_chapter['section_index']

    def get_current_chapter_index(self):
        return self.current_chapter['chapter_index']

"""
test zone --> I should do that properly in test_course.py
path = "./inputs/test/"
with open(os.path.join(path, 'en.md'), 'r') as file:
    raw_course = file.read()

course = Course(raw_course)

# Extract the text of Chapter 2 from Section 2
chapter_text = course.get_chapter_text(2, 2)
if chapter_text:
    print(chapter_text)
else:
    print("Chapter not found!")
"""
