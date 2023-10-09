from ..course import Course

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
