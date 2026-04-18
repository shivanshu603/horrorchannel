import asyncio
import time
import os
import shutil

from modules.brain import ContentBrain
from modules.asset_manager import AssetManager
from modules.audio import AudioEngine
from modules.composer import Composer


# ================== CLEAN CACHE ==================
def clean_cache():
    folders = [
        "assets/audio_clips",
        "assets/video_clips",
        "assets/temp"
    ]

    for folder in folders:
        path = os.path.join(os.getcwd(), folder)

        if not os.path.exists(path):
            continue

        for file in os.listdir(path):
            file_path = os.path.join(path, file)

            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except:
                pass


# ================== HOOK BOOST ==================
def optimize_hook(text):
    lines = text.split("\n")

    if len(lines) > 2:
        # Make first line sharper
        lines[0] = "Kal raat... jo hua... woh normal nahi tha..."

    return "\n".join(lines)


# ================== CREATE SHORT ==================
async def create_one_short():
    print("🚀 Creating Horror Short...\n")

    try:
        # ===== SCRIPT =====
        brain = ContentBrain()
        script_data = brain.generate_script()

        if not script_data:
            return False

        scene = script_data[0]

        # 🔥 Hook Optimization
        scene["text"] = optimize_hook(scene.get("text", ""))

        # ===== AUDIO =====
        audio_engine = AudioEngine()
        script_data = await audio_engine.process_script(script_data)

        # ===== ASSETS =====
        asset_manager = AssetManager()
        assets_map = asset_manager.get_videos(script_data)

        if not assets_map:
            return False

        # ===== VIDEO =====
        composer = Composer()
        scene_paths = composer.render_all_scenes(script_data, assets_map)

        if not scene_paths:
            return False

        final_video = composer.concatenate_with_transitions(scene_paths)

        if not final_video or not os.path.exists(final_video):
            return False

        print("✅ Video Ready")

        # ===== CLEAN =====
        clean_cache()

        # ===== UPLOAD =====
        print("📤 Uploading...\n")

        from modules.uploader import YouTubeUploader
        uploader = YouTubeUploader()

        title = scene.get("title", "Scary Horror Story")

        # 🔥 POWER TITLE
        final_title = f"😱 {title} | Don't Watch Alone | Real Horror"

        description = f"""
😨 WARNING: This is not just a story...

{scene.get("text","")[:400]}...

अगर डर लगा 😱 तो LIKE करो
और ऐसे horror videos के लिए SUBSCRIBE 🔔

#Horror #Scary #HindiHorror #Ghost #ViralShorts
"""

        video_id = uploader.upload(
            video_path=final_video,
            title=final_title[:100],
            description=description,
            tags=[
                "horror story",
                "scary video",
                "ghost story",
                "dark horror",
                "creepy story",
                "viral shorts",
                "hindi horror"
            ]
        )

        if video_id:
            print(f"✅ Uploaded: https://youtu.be/{video_id}")
            return True

        return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


# ================== MAIN LOOP ==================
async def main():
    print("💀 HORROR AI ENGINE RUNNING...\n")

    start_time = time.time()
    count = 0

    while True:
        count += 1
        print(f"\n🎬 SHORT #{count}\n")

        # 🔁 Retry system
        for attempt in range(2):
            success = await create_one_short()

            if success:
                print(f"✅ Short #{count} DONE\n")
                break
            else:
                print(f"⚠️ Retry {attempt+1}")

        print("⏳ Waiting 7 minutes...\n")
        await asyncio.sleep(420)

        if time.time() - start_time > 18000:
            print("⏹️ STOP (limit reached)")
            break


if __name__ == "__main__":
    asyncio.run(main())
