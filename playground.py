import os
import re
import tiktoken
import openai

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def split_text_into_chunks(text: str, MAX_TOKENS: int = 1000, ENCODING_NAME: str = "cl100k_base") -> list:
    """
    Splits the input text into chunks with a maximum token count.

    Args:
        text (str): The input text to be split.
        MAX_TOKENS (int): The maximum token count for each chunk (default: 1000).
        ENCODING_NAME (str): The encoding name to be used for tokenization (default: "cl100k_base").

    Returns:
        list: The list of chunks.
    """
    # Split the transcript into < 1000 token chunks while preserving sentences/paragraphs
    chunks = []
    sentences = re.split(r'\.\s+', text)  # Split the long string into sentences
    current_chunk = ""

    for sentence in sentences:
        sentence_tokens = num_tokens_from_string(sentence, ENCODING_NAME)

        if sentence_tokens + num_tokens_from_string(current_chunk, ENCODING_NAME) <= MAX_TOKENS:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    # Add the last remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def write_synthetic_lecture(self, language):
    """
    Writes a synthetic lecture that would be based on the transcript text in a markdown format.
    Uses the GPT-3.5 API to generate essential points from the transcript, create an outline,
    and then elaborate the outline into a full lecture.

    Args:
        language (str): The language code for the language in which the lecture is to be written.

    Returns:
        str: The transcript formatted into a synthetic lecture.
    """

    # Load the transcript from the output folder
    audio_file_name = os.path.basename(self.original_audio_file[0])
    transcript_file_path = os.path.join("./outputs", os.path.splitext(audio_file_name)[0] + f"_{language}_transcript.txt")

    with open(transcript_file_path, 'r', encoding='utf-8') as f:
        input_transcript = f.read()

    # Create multiple chunks of the transcript
    chunks = split_text_into_chunks(input_transcript)

    # Extract essential points from each chunk
    essential_points = []
    for chunk in chunks:
        prompt = f"Extract the essential points from the following transcript, focusing on facts and concepts without grammar: '{chunk}'"
        output_size = 1000 // len(chunks)
        essential_point = self.manipulate_text(prompt)[:output_size]
        essential_points.append(essential_point)

    # Join the essential points into a single string
    essential_points_string = " ".join(essential_points)

    # Create an outline from the essential points
    prompt = f"Create a detailed outline of the lecture from the following essential points, dividing it into at most 4 parts: '{essential_points_string}'"
    outline = self.manipulate_text(prompt)

    # Split the outline into parts
    parts = outline.split('\n')

    # For each part, use GPT-3.5 to generate a section of the lecture
    lecture_parts = []
    for i, part in enumerate(outline.split("\n")):
        prompt = f"Write a synthetic, easy-to-read, and enjoyable lecture. It must be in '{language}' and with a markdown syntax. you will focus on this section '{part[i]}' and you will choose from these essential points: '{essential_points_string}'"
        lecture_part = self.manipulate_text(prompt)
        lecture_parts.append(lecture_part)

    # Join the lecture parts into a single string and save it as a markdown file
    lecture = '\n'.join(lecture_parts)
    suffix = f"{language}_lecture"
    self.save_manipulated_text(lecture, suffix)

    return lecture

