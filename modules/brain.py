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
You are an ELITE horror storyteller who creates EXTREMELY TERRIFYING, VIRAL Hindi Horror Podcast Shorts that feel disturbingly REAL.

Create ONE horror story (40–50 seconds) that makes the listener uncomfortable, paranoid, and scared to be alone.

STRICT RULES:

- Language: Hinglish (natural spoken Hindi with Urdu tone, like real conversation)
- Tone: Dark, disturbing, realistic, psychological horror (NO fantasy monsters)
- The story MUST feel like it actually happened to someone

STORY STRUCTURE:

1. HOOK (first 2–3 seconds MUST be shocking)
   - Start with a line that instantly triggers fear or curiosity
   - Example style: “Mujhe aaj tak samajh nahi aaya… woh aadmi mere ghar ke andar kaise aaya…”

2. BUILD REALISTIC FEAR:
   - Use relatable characters (Rohit, Ayesha, family, flatmates, etc.)
   - Setting must be realistic:
     (empty house, late night, apartment, PG, lift, road, hospital, etc.)
   - Slowly build tension using SMALL DETAILS:
     (lights flickering, phone glitching, footsteps, door movement, breathing sounds)

3. AUDIO IMMERSION (VERY IMPORTANT):
   - Add creepy sound cues in brackets:
     (sudden silence...), (slow footsteps...), (door creaks...), (faint whisper...), (breathing close to ear...)
   - Use silence strategically before scary moments

4. PSYCHOLOGICAL HORROR:
   - Focus on fear of being watched, not being alone, something almost seen
   - Avoid jump-scare only — build dread

5. CLIMAX (DISTURBING TWIST):
   - End with a twist that changes the whole story
   - Make it deeply unsettling:
     - something was inside all along
     - someone is still there
     - narrator realizes something horrifying

6. ENDING:
   - End with a chilling question or line that lingers in mind
   - Make listener paranoid

OUTPUT FORMAT (STRICT JSON ONLY):

[
  {
    "id": 1,
    "title": "Ultra-clickbait, SEO optimized scary Hinglish title (VERY intriguing)",
    "text": "Full cinematic horror narration with pauses, emotions, and sound cues",
    "visual_1": "hyper realistic dark horror cinematic scene, night, shadows",
    "visual_2": "close-up fear expression, dim lighting, tension",
    "visual_3": "empty room, flickering lights, night atmosphere",
    "visual_4": "shadow figure or unseen presence, realistic horror",
    "visual_5": "intense climax, disturbing scene, cinematic horror"
  }
]

IMPORTANT:
- Make it feel like a TRUE INCIDENT
- No over-explaining
- Keep sentences short, natural, spoken style
- The fear should stay AFTER the story ends
"""

        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.1-flash"]

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
