import requests
from django.conf import settings

def generate_recommendation(prompt: str) -> str:
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(f"{url}?key={settings.GEMINI_API_KEY}", headers=headers, json=data)

    print("Gemini Response:", response.status_code, response.text)

    if response.status_code == 200:
        try:
            text_response = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            return text_response
        except (KeyError, IndexError):
            print("Gemini parsing error")
            return "AI recommendation service is currently unavailable."
    else:
        print("Gemini API call failed")
        return "AI recommendation service is currently unavailable."
