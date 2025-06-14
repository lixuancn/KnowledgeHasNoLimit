import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

class LLMClient:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.client = self._get_client()

    def _get_client(self)->OpenAI:
        load_dotenv()

        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY_TEST"),
            base_url="https://api.deepseek.com"
        )

        return client

    def send_messages(self, messages):
        response = self.client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
        )
        return response