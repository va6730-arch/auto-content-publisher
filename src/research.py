import os
import re
import json
import requests
import xml.etree.ElementTree as ET

GEMINI_MODEL = "gemini-2.5-flash"


def get_trends(geo="IN"):
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    root = ET.fromstring(r.content)
    titles = [i.find("title").text for i in root.iter("item")]
    return titles[:20]


def ask_gemini(prompt):
    key = os.environ["GEMINI_API_KEY"]
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
    )
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, headers=headers, json=body, timeout=60)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def pick_topic():
    trends = get_trends()
    prompt = (
        "Here are today's trending searches: "
        + ", ".join(trends)
        + ". Pick ONE topic best suited for a safe, informative, "
        "faceless YouTube video. Avoid politics, violence and "
        "adult content. Reply ONLY with JSON, no extra text, "
        'in this format: {"topic": "...", "reason": "...", '
        '"keywords": ["...", "..."]}'
    )
    text = ask_gemini(prompt)
    text = re.sub(r"```json|```", "", text).strip()
    return json.loads(text)


if __name__ == "__main__":
    topic = pick_topic()
    print(json.dumps(topic, ensure_ascii=False, indent=2))
    with open("topic.json", "w", encoding="utf-8") as f:
        json.dump(topic, f, ensure_ascii=False, indent=2)
