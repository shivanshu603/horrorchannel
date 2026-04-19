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

    def generate_script(self):
        print("🎬 Generating Global Did You Know Short...")

        prompt = """
You are a master horror storyteller creating VIRAL Hindi Horror Podcast Shorts.

Create ONE extremely suspenseful, creepy horror story (50-60 seconds).

Rules:
- Language: Hinglish (natural spoken Hindi + Urdu tone)
- Start with a VERY STRONG hook (fear + curiosity)
- Story must feel REAL (no fantasy monsters, use realistic horror like:
  - haunted house
  - unknown calls
  - night incidents
  -use some characters like a family, friends, or a lone person and their name for relatability
  - shadow sightings
  - real-life inspired horror
)
- Build suspense step-by-step (slow tension, then twist)
- Add background sound cues like:
  (sudden silence...), (footsteps...), (door creak...), (whisper...)
- End with a disturbing twist or question

Return ONLY JSON:

[
  {
    "id": 1,
    "title": "SEO optimized scary title in Hinglish",
    "text": "Full horror narration script",
    "visual_1": "dark cinematic horror scene ",
    "visual_2": "creepy realistic visuals ",
    "visual_3": "night environment horror visuals",
    "visual_4": "shadow or unknown presence visuals",
    "visual_5": "fear climax visuals"
  }
]
"""

        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-1.5-flash","gemini-1.5-flash-8b"]

        for model_name in models:
            for attempt in range(3):
                try:
                    print(f"🔄 Trying {model_name} (Attempt {attempt+1}/3)")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )

                    clean = response.text.strip().replace("```json", "").replace("```", "").strip()
                    result = json.loads(clean)

                    # Save topic for avoiding repetition
                    title = result[0].get("title", "") if isinstance(result, list) else ""
                    if title:
                        self.save_history(title)

                    print(f"✅ SUCCESS with {model_name}")
                    return result   # ← List return kar rahe hain

                except Exception as e:
                    err = str(e)
                    print(f"❌ Failed {model_name}: {err[:150]}")
                    if "503" in err or "high demand" in err:
                        time.sleep(10)
                        continue
                    else:
                        break

        print("❌ All models failed.")
        return None


if __name__ == "__main__":
    brain = ContentBrain()
    output = brain.generate_script()
    if output:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print("✅ latest_script.json saved")
