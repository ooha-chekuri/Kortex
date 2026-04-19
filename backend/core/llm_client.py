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
        self.last_error: str | None = None

    def generate(self, prompt: str, temperature: float = 0.1) -> str:
        """Generate text using the configured LLM provider."""

        # Route to specific provider
        if self.provider == "ollama":
            return self._generate_ollama(prompt, temperature)
        elif self.provider == "openai":
            return self._generate_openai(prompt, temperature)
        elif self.provider == "groq":
            return self._generate_groq(prompt, temperature)
        elif self.provider == "gemini":
            return self._generate_gemini(prompt, temperature)
        else:
            # Default fallback
            return self._generate_gemini(prompt, temperature)

    def _generate_openai(self, prompt: str, temperature: float) -> str:
        if not self.openai_api_key or self.openai_api_key == "your_openai_api_key_here":
            raise ValueError("OpenAI API key not configured")

        from openai import OpenAI

        client = OpenAI(api_key=self.openai_api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    def _generate_gemini(self, prompt: str, temperature: float) -> str:
        if not self.gemini_api_key or self.gemini_api_key.startswith("your_"):
            raise ValueError("Gemini API key not configured")

        from google import genai

        client = genai.Client(api_key=self.gemini_api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"temperature": temperature},
        )
        return response.text.strip()

    def _generate_ollama(self, prompt: str, temperature: float) -> str:
        # Check if ollama is available
        try:
            import ollama
        except ImportError:
            raise ImportError("ollama package not installed. Run: pip install ollama")

        # Check if ollama server is running
        try:
            client_kwargs = {}
            if self.ollama_host:
                client_kwargs["host"] = self.ollama_host
            client = ollama.Client(**client_kwargs)
            # Try a simple request to check connectivity
            client.list()
        except Exception as e:
            raise ConnectionError(f"Ollama server not accessible: {e}")

        # Generate response
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
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key or groq_key == "your_groq_key_here":
            raise ValueError("Groq API key not configured")

        from openai import OpenAI

        client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
        )
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()


# Global client instance
_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create the LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def reset_llm_client() -> None:
    """Reset the LLM client to force re-creation."""
    global _llm_client
    _llm_client = None
