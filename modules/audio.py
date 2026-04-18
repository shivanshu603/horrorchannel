import os
import asyncio
import edge_tts
from mutagen.mp3 import MP3

class AudioEngine:
    def __init__(self):
        # 🔥 Best expressive Hindi voice (horror ke liye)
        self.voice = "hi-IN-SwaraNeural"

        self.output_dir = os.path.join(os.getcwd(), "assets", "audio_clips")
        os.makedirs(self.output_dir, exist_ok=True)

    # ================== TEXT → SSML ==================
    def to_ssml(self, text):
        text = self.add_pauses(text)

        return f"""
<speak version="1.0" xml:lang="hi-IN">
    <voice name="{self.voice}">
        <prosody rate="-18%" pitch="-3st" volume="+0%">
            {text}
        </prosody>
    </voice>
</speak>
"""

    # ================== SMART PAUSES ==================
    def add_pauses(self, text):
        replacements = {
            "...": '<break time="800ms"/>',
            "\n": '<break time="500ms"/>',
            ".": '.<break time="400ms"/>',
            ",": ',<break time="200ms"/>',
        }

        for k, v in replacements.items():
            text = text.replace(k, v)

        return text

    # ================== HUMAN STYLE FORMAT ==================
    def format_for_tts(self, text):
        # 🔥 Break into natural spoken lines
        text = text.replace(". ", ".\n")
        text = text.replace("...", "...\n")

        # Hinglish natural pauses
        text = text.replace("लेकिन", "\n... लेकिन")
        text = text.replace("फिर", "\nफिर")
        text = text.replace("और", "\nऔर")

        return text

    # ================== AUDIO GENERATION ==================
    async def generate_audio(self, text, output_filename, retries=3):
        output_path = os.path.join(self.output_dir, output_filename)

        for attempt in range(retries):
            try:
                ssml_text = self.to_ssml(text)

                communicate = edge_tts.Communicate(
                    text=ssml_text,
                    voice=self.voice
                )

                await communicate.save(output_path)

                print(f"🎙️ Audio Generated (Cinematic Horror Voice)")
                return output_path

            except Exception as e:
                print(f"⚠️ Audio Error (Attempt {attempt+1}/{retries}): {e}")
                await asyncio.sleep(2)

        raise Exception("❌ Audio generation failed")

    # ================== GET DURATION ==================
    def get_audio_duration(self, file_path):
        try:
            audio = MP3(file_path)
            return audio.info.length
        except:
            return 0.0

    # ================== PROCESS SCRIPT ==================
    async def process_script(self, script_data):
        print("🎙️ Generating Horror Audio (Next Level)...")

        for scene in script_data:
            scene_id = scene.get('id', 1)

            # 🔥 Format text like human narration
            raw_text = scene.get('text', '')
            formatted_text = self.format_for_tts(raw_text)

            filename = f"voice_{scene_id}.mp3"

            try:
                file_path = await self.generate_audio(formatted_text, filename)
                duration = self.get_audio_duration(file_path)

                scene['audio_path'] = file_path
                scene['duration'] = duration

                print(f"✅ Scene {scene_id}: {duration:.2f}s")

            except Exception as e:
                print(f"❌ Scene {scene_id} failed: {e}")
                continue

        return script_data
