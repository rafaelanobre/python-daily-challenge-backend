import os
from openai import OpenAI
from typing import Dict, Any

from pydantic import BaseModel
from dotenv import load_dotenv
from .logger import get_logger

load_dotenv()

secret_key = os.getenv('OPEN_AI_KEY')

client = OpenAI(api_key=secret_key)
logger = get_logger()


class OptionsModel(BaseModel):
    A: str
    B: str
    C: str
    D: str


class QuestionModel(BaseModel):
    title: str
    options: OptionsModel
    correct_answer_id: int
    explanation: str


def generate_challenge_with_ai(difficulty: str) -> Dict[str, Any]:
    system_prompt = """You are an expert coding challenge creator.
        Your task is to generate a coding question with multiple choice answers.
        The question should be appropriate for the specified difficulty level.
        The question must be about python or back-end.

        For easy questions: Focus on basic syntax, simple operations, or common programming concepts.
        For medium questions: Cover intermediate concepts like data structures, algorithms, or language features.
        For hard questions: Include advanced topics, design patterns, optimization techniques, or complex algorithms.

        Return the challenge in the following JSON structure:
        {
            "title": "The question title",
            "options": {"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"},
            "correct_answer_id": 0, // Index of the correct answer (0-3)
            "explanation": "Detailed explanation of why the correct answer is right"
        }
        The 'options' field must be a JSON object with keys 'A', 'B', 'C', and 'D', each mapping to a string answer. Do not use a list or array for options.

        Make sure the options are plausible but with only one clearly correct answer.
    """
    try:
        response = client.responses.parse(
            model='gpt-4.1-nano',
            instructions= system_prompt,
            input= f'Generate a {difficulty} difficulty challenge',
            text_format=QuestionModel,
            temperature=0.7
        )
        challenge_data = response.output_parsed

        # Log the raw challenge_data for debugging
        logger.info(f"AI challenge_data: {challenge_data}")

        # Use Pydantic's new model_validate method (parse_obj is deprecated)
        challenge = QuestionModel.model_validate(challenge_data)

        return {
            "title": challenge.title,
            "options": challenge.options.model_dump(),
            "correct_answer_id": challenge.correct_answer_id,
            "explanation": challenge.explanation
        }

    except Exception as e:
        logger.error(f"Failed to generate challenge with AI for difficulty {difficulty}")
        logger.error(f"ERROR DETAILS: {e}")
        return {
            "title": "Basic Python List Operation",
            "options": {
                "A": "my_list.append(5)",
                "B": "my_list.add(5)",
                "C": "my_list.push(5)",
                "D": "my_list.insert(5)",
            },
            "correct_answer_id": 0,
            "explanation": "In Python, append() is the correct method to add an element to the end of a list."
        }