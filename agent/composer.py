import os
import wave
import numpy as np
from PIL import Image, ImageFilter
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
    CompositeAudioClip,
    ColorClip,
    vfx,
)
# CHANGE: Imported 'volumex' from its correct submodule 'moviepy.audio.fx.all' for moviepy v1.0.3.
from moviepy.audio.fx.all import volumex
from agent import config
from agent.logger import ProjectLogger
from agent.planner import VideoPlan

class VideoComposer:
    def __init__(self, logger: ProjectLogger):
        self.logger = logger

    def _get_wav_duration(self, file_path: str) -> float:
        try:
            with wave.open(file_path, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return frames / float(rate)
        except (wave.Error, FileNotFoundError) as e:
            self.logger.error(f"Could not read WAV duration for {file_path}: {e}", exc_info=True)
            raise

    def _get_font_for_language(self, language: str, font_type: str) -> str:
        """
        Selects the appropriate font from config based on language.
        Falls back to 'default' if the language is not specifically defined.
        font_type must be one of 'intro', 'challenge', or 'reveal'.
        """
        lang_key = language.lower()
        font_set = config.FONT_MAPPINGS.get(lang_key, config.FONT_MAPPINGS["default"])
        
        # Log if fallback is used
        if lang_key not in config.FONT_MAPPINGS:
            self.logger.info(f"No specific font mapping for '{language}'. Using 'default' fonts.")
            
        font_path = font_set.get(font_type)
        if not os.path.exists(font_path):
             self.logger.error(f"Font file not found at path: {font_path}. Please ensure fonts are installed correctly.", exc_info=True)
             # Fallback to default just in case of a bad path in a specific config
             return config.FONT_MAPPINGS["default"][font_type]
        return font_path
    
    def calculate_video_duration(self, plan: VideoPlan, project_dir: str) -> float:
        self.logger.info("Calculating final video duration...")
        try:
            intro_audio_path = os.path.join(project_dir, "intro_audio.wav")
            intro_duration = self._get_wav_duration(intro_audio_path)
            current_time = 0.5 + intro_duration + config.SCENE_PAUSE_S
            for i in range(len(plan.word_pairs)):
                current_time += config.CHALLENGE_DURATION_S
                word_audio_path = os.path.join(project_dir, f"word_{i}.wav")
                word_duration = self._get_wav_duration(word_audio_path)
                reveal_duration = max(word_duration + 0.5, config.REVEAL_DURATION_S)
                current_time += reveal_duration + config.SCENE_PAUSE_S
            self.logger.success(f"Calculated video duration: {current_time:.2f} seconds.")
            return current_time
        except Exception as e:
            error_msg = f"Failed to calculate video duration. Asset files might be missing. Error: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)

    def create_video(self, plan: VideoPlan, project_dir: str, final_duration: float):
        self.logger.info("Starting video composition...")
        try:
            bg_image_path = os.path.join(project_dir, "background.png")
            music_path = os.path.join(project_dir, "music.wav")
            intro_audio_path = os.path.join(project_dir, "intro_audio.wav")

            bg_clip = ImageClip(bg_image_path).set_duration(final_duration).resize(config.VIDEO_DIMENSIONS)

            darken_overlay = (ColorClip(size=config.VIDEO_DIMENSIONS, color=(0, 0, 0))
                              .set_opacity(config.BACKGROUND_DARKEN_OPACITY)
                              .set_duration(final_duration))

            intro_audio_clip = AudioFileClip(intro_audio_path)

            video_clips = [bg_clip, darken_overlay]
            audio_clips = [intro_audio_clip.set_start(0.5)]
            current_time = 0.5 + intro_audio_clip.duration + config.SCENE_PAUSE_S

            # --- Scene 1: Intro ---
            font_intro = self._get_font_for_language(plan.source_language, 'intro')
            intro_text_clip = (TextClip(plan.intro_text, font=font_intro, fontsize=120, color='white',
                                       stroke_color='white', stroke_width=0, size=(int(config.VIDEO_DIMENSIONS[0] * 0.9), None), method='caption')
                               .set_position('center')
                               .set_start(0.5)
                               .set_duration(intro_audio_clip.duration))
            # intro_text_clip = intro_text_clip.fx(vfx.fadein, 0.5).fx(vfx.fadeout, 0.5)
            video_clips.append(intro_text_clip)

            # --- Scenes 2-N: Words ---
            font_challenge = self._get_font_for_language(plan.source_language, 'challenge')
            font_reveal = self._get_font_for_language(plan.target_language, 'reveal')
            for i, pair in enumerate(plan.word_pairs):
                # Part 1: Challenge
                challenge_start = current_time
                challenge_text_clip = (TextClip(pair.source_word, font=font_challenge, fontsize=140, color='yellow',
                                               stroke_color='white', stroke_width=0, size=(int(config.VIDEO_DIMENSIONS[0] * 0.9), None), method='caption')
                                       .set_position(('center', 0.25), relative=True)
                                       .set_start(challenge_start)
                                       .set_duration(config.CHALLENGE_DURATION_S)
                                    #    .fx(vfx.fadein, 0.3)
                                       )
                video_clips.append(challenge_text_clip)

                def subtle_zoom(t):
                    return 1 + 0.02 * np.sin(t * np.pi / config.COUNTDOWN_ANIMATION_DURATION)

                animated_bg_segment = (bg_clip
                                      .subclip(challenge_start, challenge_start + config.CHALLENGE_DURATION_S)
                                      .set_start(challenge_start)
                                      .resize(subtle_zoom))

                video_clips.insert(1, animated_bg_segment)

                countdown_font = self._get_font_for_language('default', 'challenge') # Countdown numbers are always fine with default

                for j in range(config.CHALLENGE_DURATION_S):
                    num = config.CHALLENGE_DURATION_S - j
                    countdown_start = challenge_start + j
                    countdown_clip = (TextClip(str(num), font=countdown_font, fontsize=200, color='white', stroke_color='white', stroke_width=0)
                                      .set_position('center')
                                      .set_start(countdown_start)
                                      .set_duration(1))
                    # countdown_clip = countdown_clip.fx(vfx.fadein, 0.2).fx(vfx.fadeout, 0.2)
                    video_clips.append(countdown_clip)
                current_time += config.CHALLENGE_DURATION_S

                # Part 2: Reveal
                word_audio_path = os.path.join(project_dir, f"word_{i}.wav")
                word_audio_clip = AudioFileClip(word_audio_path)

                reveal_start = current_time
                reveal_duration = max(word_audio_clip.duration + 0.5, config.REVEAL_DURATION_S)
                reveal_text_clip = (TextClip(pair.target_word, font=font_reveal, fontsize=140, color='white',
                                             stroke_color='white', stroke_width=0, size=(int(config.VIDEO_DIMENSIONS[0] * 0.9), None), method='caption')
                                    .set_position('center')
                                    .set_start(reveal_start)
                                    .set_duration(reveal_duration)
                                    # .fx(vfx.fadein, 0.3).fx(vfx.fadeout, 0.5)
                                    )

                video_clips.append(reveal_text_clip)
                audio_clips.append(word_audio_clip.set_start(reveal_start + 0.2))
                current_time += reveal_duration + config.SCENE_PAUSE_S

            # --- Final Assembly ---
            final_audio_mix = []
            if os.path.exists(music_path):
                self.logger.info("Music track found. Including in final mix.")
                music_clip = (AudioFileClip(music_path)
                              .fx(volumex, config.MUSIC_VOLUME)
                              .set_duration(final_duration))
                final_audio_mix.append(music_clip)
            else:
                self.logger.warning("No music track found. Composing video with voiceover only.")

            final_audio_mix.extend(audio_clips)
            final_audio = CompositeAudioClip(final_audio_mix).set_duration(final_duration)

            final_video = CompositeVideoClip(video_clips, size=config.VIDEO_DIMENSIONS).set_duration(final_duration)
            final_video.audio = final_audio

            output_path = os.path.join(project_dir, "final_video.mp4")
            self.logger.info(f"Writing final video to {output_path}...")

            temp_audio_path = os.path.join(project_dir, "temp-audio.mp3")

            final_video.write_videofile(output_path, fps=24, codec='libx264', temp_audiofile=temp_audio_path)
            self.logger.success(f"Video composed successfully and saved to {os.path.basename(output_path)}")

        except Exception as e:
            error_msg = f"Video composition failed: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)