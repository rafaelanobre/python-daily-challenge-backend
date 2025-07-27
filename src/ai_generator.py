import os
from http.client import HTTPException

from openai import OpenAI
from typing import Dict, Any

from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

secret_key = os.getenv('OPEN_AI_KEY')

client = OpenAI(api_key=secret_key)


class QuestionModel(BaseModel):
    title: str
    options: Dict[str, Any]
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
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answer_id": 0, // Index of the correct answer (0-3)
            "explanation": "Detailed explanation of why the correct answer is right"
        }

        Make sure the options are plausible but with only one clearly correct answer.
    """
    try:
        response = client.responses.parse(
            model='gpt-4.1-nano',
            input=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user','content': f'Generate a {difficulty} difficulty challenge'}
            ],
            text_format=QuestionModel,
            temperature=0.7
        )
        challenge_data = response.output_parse

        required_fields = ['title', 'options', 'correct_answer_id', 'explanation']

        for field in required_fields:
            if field not in challenge_data:
                raise ValueError(f'Missing required field: {field}')

        return challenge_data

    except Exception as e:
        print(e)
        return {
            "title": "Basic Python List Operation",
            "options": [
                "my_list.append(5)",
                "my_list.add(5)",
                "my_list.push(5)",
                "my_list.insert(5)",
            ],
            "correct_answer_id": 0,
            "explanation": "In Python, append() is the correct method to add an element to the end of a list."
        }