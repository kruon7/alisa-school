import json
import os
import threading

from google import genai
from google.genai import types

_client_lock = threading.Lock()
_model_name = "gemini-3.6-flash"
_request_timeout = 120_000


def _get_client():
    with _client_lock:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY не задан в .env")
        if api_key == "YOUR_KEY_HERE":
            raise RuntimeError(
                "Задайте настоящий GEMINI_API_KEY в файле backend/.env "
                "(получить: https://aistudio.google.com/apikey)"
            )
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=_request_timeout),
        )
        return client


def _chat(prompt: str, *, system: str = "", temperature: float = 0.7) -> str:
    client = _get_client()
    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system if system else None,
    )
    resp = client.models.generate_content(
        model=_model_name,
        contents=prompt,
        config=config,
    )
    return resp.text or ""


def explain_topic(grade: str, subject: str, topic: str) -> str:
    system = (
        "Ты — дружелюбный школьный учитель. "
        "Объясняешь просто, понятно и интересно для ученика. "
        "Используй примеры, аналогии и сравнения. "
        "Отвечай на русском языке."
    )
    prompt = (
        f"Объясни тему '{topic}' из предмета '{subject}' для {grade} класса. "
        f"Дай развёрнутое объяснение с примерами, формулами (если есть) "
        f"и понятными аналогиями из жизни. "
        f"Используй HTML-разметку: <b>, <i>, <ul>/<li>, <code>, <br>. "
        f"Не используй <script>, <style>, <iframe>."
    )
    return _chat(prompt, system=system, temperature=0.6)


def ask_question(grade: str, subject: str, question: str, topic: str = "") -> str:
    system = (
        "Ты — AI-помощник школьника. "
        "Отвечай точно, по делу, с примерами. "
        "Если ответ не очевиден — подскажи, где искать. "
        "Отвечай на русском языке."
    )
    context = f"Тема: {topic}. " if topic else ""
    prompt = (
        f"Школьник {grade} класса, предмет: {subject}. {context}"
        f"Вопрос: {question}\n\n"
        f"Дай краткий, понятный ответ с примерами. "
        f"Используй HTML: <b>, <i>, <ul>/<li>, <code>, <br>."
    )
    return _chat(prompt, system=system, temperature=0.5)


def generate_task(subject: str, level: str) -> dict:
    system = (
        "Ты создаёшь задачи для школьников. "
        "Генерируй одну задачу с ответом и решением. "
        "Отвечай на русском языке."
    )
    diff = {"Лёгкий": "очень простую", "Средний": "средней сложности", "Сложный": "сложную, олимпиадную"}
    diff_text = diff.get(level, "средней сложности")
    prompt = (
        f"Создай одну {diff_text} задачу по предмету '{subject}'.\n"
        f"Верни JSON без markdown:\n"
        f'{{"q": "текст задачи", "a": "ответ", "solution": "пошаговое решение"}}\n'
        f"Значения должны быть строковыми."
    )
    raw = _chat(prompt, system=system, temperature=0.8)
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(lines)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"q": "Не удалось сгенерировать", "a": "", "solution": ""}