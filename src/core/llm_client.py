from __future__ import annotations

import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self) -> None:
        self.provider = os.getenv("KORTEX_LLM_PROVIDER", "gemini").lower()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("KORTEX_LLM_MODEL", "gemini-1.5-flash")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    def generate(self, prompt: str, temperature: float = 0.1) -> str:
        """Generate text - never raises ConnectionError."""
        print(f"\n[LLM_HUB] Provider: {self.provider}, Model: {self.model}")
        try:
            # Priority: Groq > Gemini > OpenAI > Ollama > Mock
            if self.provider == "groq" and self.groq_api_key:
                print("[LLM_HUB] Using Groq (ultra-fast)")
                return self._generate_groq(prompt, temperature)
            elif self.provider == "gemini" and self.gemini_api_key:
                print("[LLM_HUB] Using Gemini")
                return self._generate_gemini(prompt, temperature)
            elif self.provider == "openai" and self.openai_api_key:
                print("[LLM_HUB] Using OpenAI")
                return self._generate_openai(prompt, temperature)
            elif self.provider == "ollama":
                print("[LLM_HUB] Using Ollama")
                return self._generate_ollama(prompt, temperature)
            else:
                print("[LLM_HUB] Fallback to mock (no API key)")
                return self._generate_mock()
        except Exception as e:
            print(f"[LLM_HUB] Error: {str(e)}")
            logging.error(f"Kortex LLM Error: {str(e)}")
            return self._generate_mock()

    def _generate_mock(self) -> str:
        return (
            "Based on the retrieved context, I can provide the following information:\n\n"
            "The relevant documents have been found in the knowledge base. "
            "Please refer to the sources for detailed technical information.\n\n"
            "*Sources: See attached context documents*"
        )

    def _generate_groq(self, prompt: str, temperature: float) -> str:
        from groq import Groq

        client = Groq(api_key=self.groq_api_key)
        # Use llama3-70b for best results, or mixtral-8x7b for speed
        model = os.getenv("KORTEX_GROQ_MODEL", "llama3-70b-8192")
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()

    def _generate_gemini(self, prompt: str, temperature: float) -> str:
        import google.generativeai as genai
        import time
        from google.api_core import exceptions

        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel(self.model)

        for attempt in range(3):
            try:
                response = model.generate_content(
                    prompt, generation_config={"temperature": temperature}
                )
                return response.text.strip()
            except exceptions.ResourceExhausted as e:
                wait_time = (attempt + 1) * 5
                print(f"[LLM_HUB] Quota exceeded, waiting {wait_time}s")
                time.sleep(wait_time)
            except Exception as e:
                raise e
        return self._generate_mock()

    def _generate_openai(self, prompt: str, temperature: float) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.openai_api_key)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()

    def _generate_ollama(self, prompt: str, temperature: float) -> str:
        import ollama

        client = ollama.Client(host=self.ollama_host)
        response = client.generate(
            model=self.model, prompt=prompt, options={"temperature": temperature}
        )
        return response["response"].strip()


# Singleton - no streamlit dependency
_client = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
