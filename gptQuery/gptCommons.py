from openai import OpenAI
from .license import OPENAI_TOKEN


class CreateGPTQuery:
    OPENAI_API_KEY = OPENAI_TOKEN
    CLIENT = OpenAI(api_key=OPENAI_API_KEY)
    PROMPT = None

    def __init__(self, message):
        self._message = message
        self._result = None

    def generate(self):
        completion = self.CLIENT.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.PROMPT},
                {"role": "user", "content": self._message},
            ],
        )
        self._result = completion.choices[0].message.content

    def get_result(self):
        return self._result
