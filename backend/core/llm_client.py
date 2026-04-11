from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self) -> None:
        self.provider = os.getenv("KORTEX_LLM_PROVIDER", "gemini").lower()
        self.model = os.getenv("KORTEX_LLM_MODEL", "gemini-2.0-flash")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ollama_host = os.getenv("OLLAMA_HOST")

    def generate(self, prompt: str, temperature: float = 0.1) -> str:
        if self.provider == "openai":
            return self._generate_openai(prompt, temperature)
        if self.provider == "ollama":
            return self._generate_ollama(prompt, temperature)
        if self.provider == "gemini":
            return self._generate_gemini(prompt, temperature)
        if self.provider == "groq":
            return self._generate_groq(prompt, temperature)
        return self._generate_gemini(prompt, temperature)

    def _generate_openai(self, prompt: str, temperature: float) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.openai_api_key)
        response = client.responses.create(
            model=self.model,
            input=prompt,
            temperature=temperature,
        )
        return response.output_text.strip()

    def _generate_gemini(self, prompt: str, temperature: float) -> str:
        from google import genai

        client = genai.Client(api_key=self.gemini_api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"temperature": temperature},
        )
        return response.text.strip()

    def _generate_ollama(self, prompt: str, temperature: float) -> str:
        try:
            import ollama
        except ImportError:
            return "LLM client not available. Please install ollama or use another provider."

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

    def _generate_groq(self, prompt: str, temperature: float) -> str:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()


@lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    return LLMClient()
