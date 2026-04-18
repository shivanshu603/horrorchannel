import os
import random
import ffmpeg

class Composer:
    def __init__(self):
        self.temp_dir = os.path.join(os.getcwd(), "assets", "temp")
        self.final_dir = os.path.join(os.getcwd(), "assets", "final")
        self.avatar_path = os.path.join(os.getcwd(), "assets", "avatar", "avatars.mp4")

        # ✅ ROOT bgmusic.mp3 (as per your setup)
        self.bg_music_path = os.path.join(os.getcwd(), "bgmusic.mp3")

        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)

        self.transitions = ['fade', 'wipeleft', 'wiperight', 'smoothleft', 'smoothright']

    def get_duration(self, filepath):
        try:
            probe = ffmpeg.probe(filepath)
            return float(probe['format']['duration'])
        except:
            return 0.0

    # ================== AUDIO MIX ==================
    def mix_audio(self, voice_audio, duration):
        try:
            if os.path.exists(self.bg_music_path):
                bg_music = (
                    ffmpeg.input(self.bg_music_path, stream_loop=-1)
                    .filter('atrim', duration=duration + 1)
                    .filter('volume', 0.12)  # subtle horror bg
                )

                bg_music = bg_music.filter('adelay', '200|200')

                final_audio = ffmpeg.filter(
                    [voice_audio, bg_music],
                    'amix',
                    inputs=2,
                    duration='first',
                    dropout_transition=2
                )

                return final_audio
            else:
                print("⚠️ bgmusic.mp3 not found")
                return voice_audio

        except Exception as e:
            print(f"⚠️ Audio Mix Error: {e}")
            return voice_audio

    # ================== SCENE PROCESS ==================
    def process_scene(self, scene, video_list, is_avatar=False):
        scene_id = scene.get('id', 1)
        audio_path = scene.get('audio_path')
        total_duration = scene.get('duration', 0)

        if not audio_path or not os.path.exists(audio_path):
            print(f"⚠️ Audio missing for Scene {scene_id}")
            return None

        output_path = os.path.join(self.temp_dir, f"scene_{scene_id}.mp4")

        try:
            voice_audio = ffmpeg.input(audio_path)
            audio_stream = self.mix_audio(voice_audio, total_duration)

            # ================== VIDEO ==================
            if is_avatar and os.path.exists(self.avatar_path):
                print(f"⚙️ Scene {scene_id}: 🤖 Avatar Mode")

                video_stream = (
                    ffmpeg.input(self.avatar_path, stream_loop=-1)
                    .trim(duration=total_duration + 0.5)
                    .setpts('PTS-STARTPTS')
                    .filter('scale', 1080, 1920, force_original_aspect_ratio='increase')
                    .filter('crop', 1080, 1920)
                    .filter('fps', fps=30)
                )

            else:
                print(f"⚙️ Scene {scene_id}: 🎞️ Multi-Clip Mode")

                if not isinstance(video_list, list) or len(video_list) == 0:
                    print(f"⚠️ No videos for scene {scene_id}")
                    return None

                num_clips = len(video_list)
                clip_duration = total_duration / num_clips

                video_streams = []

                for i, path in enumerate(video_list):
                    try:
                        stream = (
                            ffmpeg.input(path, stream_loop=-1)
                            .trim(duration=clip_duration + (0.2 if i == num_clips - 1 else 0))
                            .setpts('PTS-STARTPTS')
                            .filter('scale', 1080, 1920)
                            .filter('crop', 1080, 1920)
                            .filter('fps', fps=30)
                        )
                        video_streams.append(stream)

                    except Exception as e:
                        print(f"⚠️ Clip error: {e}")

                # 🔥 Smooth concat (NO transitions inside scene)
                video_stream = ffmpeg.concat(*video_streams, v=1, a=0)

            # ================== OUTPUT ==================
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

    # ================== RENDER ALL ==================
    def render_all_scenes(self, script_data, video_lists):
        rendered_paths = []
        avatar_indices = []

        if len(script_data) >= 4 and os.path.exists(self.avatar_path):
            valid_range = list(range(1, len(script_data)-1))
            count = min(2, len(valid_range))
            avatar_indices = random.sample(valid_range, count)
            print(f"🎲 Avatar scenes: {[i+1 for i in avatar_indices]}")

        for i, scene in enumerate(script_data):
            video_list = video_lists[i]
            is_avatar = i in avatar_indices

            output_path = self.process_scene(scene, video_list, is_avatar)

            if output_path:
                rendered_paths.append(output_path)

        return rendered_paths

    # ================== FINAL STITCH ==================
    def concatenate_with_transitions(self, video_paths, output_filename="final_short.mp4"):
        print("🎬 Smart cinematic stitching...")

        output_path = os.path.join(self.final_dir, output_filename)

        if not video_paths:
            return None

        input1 = ffmpeg.input(video_paths[0])
        v_stream = input1.video
        a_stream = input1.audio
        current_dur = self.get_duration(video_paths[0])

        for i in range(1, len(video_paths)):
            next_clip = ffmpeg.input(video_paths[i])
            next_dur = self.get_duration(video_paths[i])

            # 🔥 less transition spam
            use_transition = random.choice([True, False, False])

            # avoid transition at start/end
            if i == 1 or i == len(video_paths) - 1:
                use_transition = False

            if use_transition:
                trans_dur = 0.4
                offset = current_dur - trans_dur
                effect = random.choice(self.transitions)

                print(f"✨ Transition: {effect}")

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

            else:
                print("➡️ Hard cut")

                v_stream = ffmpeg.concat(v_stream, next_clip.video, v=1, a=0)
                a_stream = ffmpeg.concat(a_stream, next_clip.audio, v=0, a=1)

                current_dur += next_dur

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
