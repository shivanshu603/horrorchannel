import os
import requests
import random

class AssetManager:
    def __init__(self):
        self.api_key = "hZBjjYowDAauyvn9rioK5qYMHFdCq11rKnmWo4OQlXhZspsVuo2DkpCP"
        self.base_url = "https://api.pexels.com/videos/search"
        self.headers = {"Authorization": self.api_key}

        self.assets_dir = os.path.join(os.getcwd(), "assets", "video_clips")
        os.makedirs(self.assets_dir, exist_ok=True)

        # 🔥 PREDEFINED HORROR THEMES
        self.horror_themes = [
            "dark empty room",
            "haunted house night",
            "creepy corridor",
            "abandoned building",
            "shadow figure dark",
            "night street alone",
            "flickering lights room",
            "horror silhouette",
            "scary hallway",
            "foggy night road",
            "lonely apartment night"
        ]

    # ================== SMART QUERY ==================
    def generate_queries(self, scene):
        base_queries = []

        # Use AI visuals if available
        v1 = scene.get("visual_1", "")
        v2 = scene.get("visual_2", "")
        v3 = scene.get("visual_3", "")

        if v1:
            base_queries.append(v1)
        if v2:
            base_queries.append(v2)
        if v3:
            base_queries.append(v3)

        # Add horror fallback
        while len(base_queries) < 5:
            base_queries.append(random.choice(self.horror_themes))

        return base_queries[:5]  # 🔥 Always 4–5 clips

    # ================== SEARCH ==================
    def search_video(self, query):
        params = {
            "query": query,
            "per_page": 4,
            "orientation": "portrait",
            "size": "medium"
        }

        try:
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=10)
            if response.status_code != 200:
                return None

            data = response.json()

            if not data.get("videos"):
                return None

            video = random.choice(data["videos"])
            files = video["video_files"]

            files.sort(key=lambda x: x["width"] * x["height"], reverse=True)

            return files[0]["link"]

        except:
            return None

    # ================== DOWNLOAD ==================
    def download_video(self, url, filename):
        path = os.path.join(self.assets_dir, filename)

        if os.path.exists(path):
            return path

        try:
            with requests.get(url, stream=True, timeout=15) as r:
                r.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
            return path
        except:
            return None

    # ================== MAIN ==================
    def get_videos(self, script_data):
        print("🎥 Downloading Cinematic Horror Clips...")

        all_scenes_videos = []

        for scene in script_data:
            scene_id = scene["id"]

            queries = self.generate_queries(scene)

            scene_videos = []

            for i, query in enumerate(queries):
                print(f"   🔍 Scene {scene_id}: {query}")

                url = self.search_video(query)

                if url:
                    path = self.download_video(url, f"scene_{scene_id}_{i}.mp4")

                    if path:
                        scene_videos.append(path)

            # 🔥 Fallback (ensure at least 2 clips)
            if len(scene_videos) < 2:
                print(f"⚠️ Scene {scene_id} low clips, using fallback")
                while len(scene_videos) < 2:
                    scene_videos.append(random.choice(scene_videos) if scene_videos else None)

            all_scenes_videos.append(scene_videos)

            print(f"   ✅ Scene {scene_id}: {len(scene_videos)} clips ready")

        return all_scenes_videos
