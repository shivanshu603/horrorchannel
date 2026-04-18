import asyncio
import time
from modules.brain import ContentBrain
from modules.asset_manager import AssetManager
from modules.audio import AudioEngine
from modules.composer import Composer
import os
import shutil

def clean_cache():
    """Safely deletes temporary files"""
    print("🧹 Cleaning up temporary files...")
    folders_to_clean = [
        os.path.join(os.getcwd(), "assets", "audio_clips"),
        os.path.join(os.getcwd(), "assets", "video_clips"),
        os.path.join(os.getcwd(), "assets", "temp")
    ]
    for folder in folders_to_clean:
        if not os.path.exists(folder):
            continue
        if "assets" not in folder:
            continue
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    print(f"   Deleted: {filename}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"   Failed to delete {file_path}: {e}")
    print("✅ Workspace cleaned!")


async def create_one_short():
    """Ek short generate + upload karega"""
    print("🚀 Starting New Short Generation...")

    # 1. BRAIN - Script Generate
    brain = ContentBrain()
    try:
        script_data = brain.generate_script()
        if not script_data:
            print("❌ Script generation failed")
            return False
    except Exception as e:
        print(f"❌ Brain Error: {e}")
        return False

    # 2. AUDIO - Natural Hindi Male Voice
    audio_engine = AudioEngine()
    try:
        script_data = await audio_engine.process_script(script_data)
    except Exception as e:
        print(f"❌ Audio Error: {e}")
        return False

    # 3. ASSETS - Stock Footage
    asset_manager = AssetManager()
    assets_map = asset_manager.get_videos(script_data)

    # 4. COMPOSER - Video Banaye
    composer = Composer()
    final_scene_paths = composer.render_all_scenes(script_data, assets_map)

    if not final_scene_paths:
        print("❌ Failed to generate scenes")
        return False

    # 5. Final Video with Transitions
    composer.concatenate_with_transitions(final_scene_paths)
    clean_cache()
    print("✅ Short successfully created!")

    # ================== YOUTUBE UPLOAD (Better SEO) ==================
    print("📤 Uploading to YouTube...")

    try:
        from modules.uploader import YouTubeUploader
        uploader = YouTubeUploader()

        scene = script_data[0] if isinstance(script_data, list) else script_data
        script_text = scene.get('text', 'Interesting Fact')

        # Strong Hinglish SEO Title
        title = f"😨 {script_text[:70]}... | DO NOT WATCH ALONE| Real Horror Story | Hindi Horror Podcast"

        # Rich SEO Description
        description = f"""😨 WARNING: This story might scare you...

{script_text[:400]}...

🧠 Duniya ke sabse interesting aur rare horror stories, true inspired incidents, aur suspenseful narrations ke liye hamare channel ko subscribe karein! 
🎧 Real Horror Stories | Night Stories | True Inspired Incidents

अगर आपको डर लगा 😱 तो LIKE जरूर करें
और ऐसी stories के लिए SUBSCRIBE करें 🔔

#HorrorStory #HindiHorror #ScaryPodcast #RealHorror #GhostStory #Suspense #DarkStories #Creepy #NightStories #ViralShorts"""
        video_path = "assets/final/final_short.mp4"

        video_id = uploader.upload(
            video_path=video_path,
            title=title[:100],
            description=description,
           tags = [
"horror story hindi",
"scary story",
"hindi horror podcast",
"real ghost story",
"creepy stories",
"dark stories",
"night horror",
"viral horror shorts",
"suspense story",
"ghost encounter",
"haunted house story",
"unknown calls story",
"shadow sighting story","real life horror",
"true inspired horror",
]
        )

        if video_id:
            print(f"✅ VIDEO UPLOADED SUCCESSFULLY!")
            print(f"🔗 https://youtu.be/{video_id}")
            return True
        else:
            print("❌ Upload failed")
            return False

    except Exception as e:
        print(f"❌ Upload Error: {e}")
        return False


async def main():
    print("🚀 CONTINUOUS HINDI FACTS MODE STARTED...")
    print("Will keep generating fresh shorts until GitHub stops the job...\n")

    short_count = 0
    start_time = time.time()

    while True:
        short_count += 1
        print(f"\n🔄 === Generating Short #{short_count} ===\n")

        success = await create_one_short()

        if success:
            print(f"✅ Short #{short_count} completed & uploaded!")
        else:
            print(f"⚠️ Short #{short_count} had some issues. Continuing...")

        # Wait before next short (balanced rate limit ke liye)
        print(f"⏳ Waiting 9 minutes before next short...\n")
        await asyncio.sleep(540)   # 9 minutes

        # Safety stop after ~5.5 hours
        if time.time() - start_time > 19800:
            print("⏹️ Maximum runtime reached (5.5 hours). Stopping now...")
            break


if __name__ == "__main__":
    asyncio.run(main())
