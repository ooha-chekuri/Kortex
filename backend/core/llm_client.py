from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self) -> None:
        self.provider = os.getenv("KORTEX_LLM_PROVIDER", "ollama").lower()
        self.model = os.getenv("KORTEX_LLM_MODEL", "llama3")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ollama_host = os.getenv("OLLAMA_HOST")

    def generate(self, prompt: str, temperature: float = 0.1) -> str:
        if self.provider == "openai":
            return self._generate_openai(prompt, temperature)
        return self._generate_ollama(prompt, temperature)

    def _generate_openai(self, prompt: str, temperature: float) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.openai_api_key)
        response = client.responses.create(
            model=self.model,
            input=prompt,
            temperature=temperature,
        )
        return response.output_text.strip()

    def _generate_ollama(self, prompt: str, temperature: float) -> str:
        import ollama

        client_kwargs = {}
        if self.ollama_host:
            client_kwargs["host"] = self.ollama_host
        client = ollama.Client(**client_kwargs)
        response = client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": temperature},
        )
        return response["response"].strip()


@lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    return LLMClient()
