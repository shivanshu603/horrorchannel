import os
import random
import ffmpeg

class Composer:
    def __init__(self):
        self.temp_dir = os.path.join(os.getcwd(), "assets", "temp")
        self.final_dir = os.path.join(os.getcwd(), "assets", "final")
        self.avatar_path = os.path.join(os.getcwd(), "assets", "avatar", "avatars.mp4")
        self.bg_music_path = "bgmusic.mp3"   # Root folder mein hai
        
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)
        
        self.transitions = ['fade', 'diagbr', 'diagtl', 'wipeleft', 'wiperight']

    def get_duration(self, filepath):
        try:
            probe = ffmpeg.probe(filepath)
            return float(probe['format']['duration'])
        except:
            return 0.0

    def process_scene(self, scene, video_pair, is_avatar=False):
        scene_id = scene.get('id', 1)
        audio_path = scene.get('audio_path')
        total_duration = scene.get('duration', 0)

        if not audio_path or not os.path.exists(audio_path):
            print(f"   ⚠️ Audio missing for Scene {scene_id}")
            return None

        output_path = os.path.join(self.temp_dir, f"scene_{scene_id}.mp4")

        try:
            voice_audio = ffmpeg.input(audio_path)

            # Background Music (soft volume)
            if os.path.exists(self.bg_music_path):
                bg_music = (
                    ffmpeg.input(self.bg_music_path, stream_loop=-1)
                    .filter('volume', 0.18)        # Bahut soft background music
                    .filter('atrim', duration=total_duration + 1)
                )
                # Mix voice + background music
                audio_stream = ffmpeg.filter([voice_audio, bg_music], 'amix', inputs=2, duration='first')
            else:
                audio_stream = voice_audio

            if is_avatar and os.path.exists(self.avatar_path):
                print(f"   ⚙️ Processing Scene {scene_id}: 🤖 Avatar Mode")
                video_stream = (
                    ffmpeg.input(self.avatar_path, stream_loop=-1)
                    .trim(duration=total_duration + 0.5)
                    .setpts('PTS-STARTPTS')
                    .filter('scale', 1080, 1920, force_original_aspect_ratio='increase')
                    .filter('crop', 1080, 1920)
                    .filter('fps', fps=30)
                )
            else:
                print(f"   ⚙️ Processing Scene {scene_id}: 🎞️ A/B Split Mode")
                path_a, path_b = video_pair
                
                dur_a = total_duration / 2
                dur_b = total_duration / 2 + 0.3

                stream_a = (
                    ffmpeg.input(path_a, stream_loop=-1)
                    .trim(duration=dur_a)
                    .setpts('PTS-STARTPTS')
                    .filter('scale', 1080, 1920).filter('crop', 1080, 1920)
                    .filter('fps', fps=30)
                )

                stream_b = (
                    ffmpeg.input(path_b, stream_loop=-1)
                    .trim(duration=dur_b)
                    .setpts('PTS-STARTPTS')
                    .filter('scale', 1080, 1920).filter('crop', 1080, 1920)
                    .filter('fps', fps=30)
                )

                video_stream = ffmpeg.concat(stream_a, stream_b, v=1, a=0)

            # Final Output
            runner = ffmpeg.output(
                video_stream, 
                audio_stream, 
                output_path,
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                preset='medium',
                movflags='faststart'
            )
            
            runner.run(overwrite_output=True, quiet=True)
            return output_path

        except Exception as e:
            print(f"❌ Render Fail Scene {scene_id}: {e}")
            return None

    def render_all_scenes(self, script_data, video_pairs):
        rendered_paths = []
        avatar_indices = []

        if len(script_data) >= 4 and os.path.exists(self.avatar_path):
            valid_range = list(range(1, len(script_data)-1))
            count = min(2, len(valid_range))
            avatar_indices = random.sample(valid_range, count)
            print(f"🎲 Avatar injected in scenes: {[i+1 for i in avatar_indices]}")

        for i, scene in enumerate(script_data):
            current_pair = video_pairs[i]
            is_avatar = i in avatar_indices

            if is_avatar:
                current_pair = (self.avatar_path, None)

            output_path = self.process_scene(scene, current_pair, is_avatar)
            if output_path:
                rendered_paths.append(output_path)

        return rendered_paths

    def concatenate_with_transitions(self, video_paths, output_filename="final_short.mp4"):
        print("🎬 Stitching final video with transitions & background music...")

        output_path = os.path.join(self.final_dir, output_filename)
        
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass

        if not video_paths:
            return None

        input1 = ffmpeg.input(video_paths[0])
        v_stream = input1.video
        a_stream = input1.audio
        current_dur = self.get_duration(video_paths[0])

        for i in range(1, len(video_paths)):
            next_clip = ffmpeg.input(video_paths[i])
            next_dur = self.get_duration(video_paths[i])
            
            trans_dur = 0.6
            offset = current_dur - trans_dur

            effect = random.choice(self.transitions)

            v_stream = ffmpeg.filter(
                [v_stream, next_clip.video], 
                'xfade', 
                transition=effect, 
                duration=trans_dur, 
                offset=offset
            )
            
            a_stream = ffmpeg.filter(
                [a_stream, next_clip.audio], 
                'acrossfade', 
                d=trans_dur
            )
            
            current_dur = (current_dur + next_dur) - trans_dur

        try:
            runner = ffmpeg.output(
                v_stream, 
                a_stream, 
                output_path,
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                preset='medium',
                movflags='faststart'
            )
            
            runner.run(overwrite_output=True, quiet=False)
            
            print(f"✅ FINAL VIDEO SAVED: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Stitching Error: {e}")
            return None
