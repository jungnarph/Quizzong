import requests
from django.conf import settings

def check_profanity(message_content):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Does the following message contain any profanity, hate speech, or offensive language? Reply only with 'Yes' or 'No'. Message: \"{message_content}\""
                    }
                ]
            }
        ]
    }

    response = requests.post(
        f"{url}?key={settings.GEMINI_API_KEY}",
        headers=headers,
        json=data
    )

    print("Gemini Response:", response.status_code, response.text)  # DEBUG

    if response.status_code == 200:
        try:
            text_response = response.json()['candidates'][0]['content']['parts'][0]['text'].strip().lower()
            print("Gemini Reply:", text_response)
            return "yes" in text_response
        except (KeyError, IndexError):
            print("Gemini parsing error")
            return False
    else:
        print("Gemini API call failed")
        return False
