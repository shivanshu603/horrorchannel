import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ContentBrain:
    
    def __init__(self):
        self.history_file = "topics_history.json"
        self.history = self.load_history()

    # ================== HISTORY ==================
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"used_topics": []}

    def save_history(self, topic):
        if topic and topic not in self.history["used_topics"]:
            self.history["used_topics"].append(topic)

            if len(self.history["used_topics"]) > 200:
                self.history["used_topics"] = self.history["used_topics"][-150:]

            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)

    # ================== SCRIPT ==================
    def generate_script(self):
        print("🎬 Generating Viral Horror Short...")

        used_topics = ", ".join(self.history.get("used_topics", [])[-20:])

        prompt = f"""
You are an ELITE horror storyteller creating VIRAL Hinglish Horror Shorts.

Avoid repeating these topics:
{used_topics}

Create ONE extremely realistic horror story (40–50 sec).

RULES:
- Hinglish (natural spoken style)
- VERY short broken sentences
- Use "..." for pauses
- Make it feel like real incident

STRUCTURE:

HOOK:
Start with shocking line
Example: "Kal raat... mere room me koi tha..."

BODY:
- Real setting (ghar, PG, road, lift, hospital)
- Add small details (lights flicker, footsteps, phone glitch)

STYLE:
- Write like someone is speaking (NOT paragraph)
- Example:
"Main ghar aaya...
lights band thi...
(silence...)
phir mujhe awaaz aayi..."

CLIMAX:
- disturbing twist
- something still there

ENDING:
- scary question

VISUAL KEYWORDS (VERY IMPORTANT):
Give 5 realistic cinematic keywords:
- dark room night
- empty corridor horror
- shadow figure silhouette
- lonely road night fog
- scared person close up

OUTPUT JSON:

[
  {{
    "id": 1,
    "title": "Very clickable Hinglish horror title",
    "text": "broken emotional horror narration with pauses",
    "visual_1": "realistic horror scene keyword",
    "visual_2": "face fear expression dark",
    "visual_3": "empty room night flicker",
    "visual_4": "shadow figure dark",
    "visual_5": "disturbing climax scene"
  }}
]
"""

        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

        for model_name in models:
            for attempt in range(3):
                try:
                    print(f"🔄 {model_name} Attempt {attempt+1}")

                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )

                    clean = response.text.strip().replace("```json", "").replace("```", "").strip()
                    result = json.loads(clean)

                    if isinstance(result, list) and result:
                        title = result[0].get("title", "")
                        if title:
                            self.save_history(title)

                        print("✅ Script Generated")
                        return result

                except Exception as e:
                    print(f"❌ {model_name} Error: {str(e)[:120]}")
                    time.sleep(5)

        print("❌ All models failed")
        return None


if __name__ == "__main__":
    brain = ContentBrain()
    output = brain.generate_script()
    if output:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print("✅ latest_script.json saved")
