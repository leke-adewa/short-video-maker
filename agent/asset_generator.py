import asyncio
import os
import random
import time
import wave
from io import BytesIO
from typing import Callable, Any, Dict

from PIL import Image
from google import genai
from google.genai import types

from agent import config
from agent.api_manager import ApiKeyManager
from agent.logger import ProjectLogger
from agent.planner import VideoPlan


class ContentGenerationError(Exception):
    """Custom exception for when an API call succeeds but returns no usable content."""
    pass


class AssetGenerator:
    def __init__(self, api_manager: ApiKeyManager, logger: ProjectLogger):
        self.api_manager = api_manager
        self.logger = logger

    def _execute_with_retry(self, api_call_func: Callable[[genai.Client], Any]):
        """Executes an API call with retry logic for key rotation."""
        max_attempts = len(self.api_manager.keys)
        for attempt in range(max_attempts):
            try:
                client = self.api_manager.get_client()
                response = api_call_func(client)
                return response
            except Exception as e:
                is_quota_error = "429" in str(e) and "RESOURCE_EXHAUSTED" in str(e)
                is_content_error = isinstance(e, ContentGenerationError)

                if is_quota_error or is_content_error:
                    log_message = f"Asset generator hit quota limit: {e}" if is_quota_error else f"Asset generator received empty/invalid content: {e}"
                    self.logger.warning(log_message)
                    if attempt < max_attempts - 1:
                        try:
                            self.api_manager.switch_key()
                            continue
                        except Exception as switch_e:
                            self.logger.error(f"Failed to switch API key: {switch_e}", exc_info=True)
                            raise switch_e
                    else:
                        raise Exception("Asset generation failed: All available API keys have been exhausted or returned invalid content.")
                else: # Non-retriable error
                    self.logger.error(f"A non-retriable error occurred in asset generation: {e}", exc_info=True)
                    raise e

    def generate_core_assets(self, plan: VideoPlan, project_dir: str):
        """Generates all assets except for music, which requires a final duration."""
        self.logger.info("Generating TTS audio for intro and word pairs...")
        self._generate_tts_audio(plan.intro_text, os.path.join(project_dir, "intro_audio.wav"))
        for i, pair in enumerate(plan.word_pairs):
            self._generate_tts_audio(pair.target_word, os.path.join(project_dir, f"word_{i}.wav"))
        self.logger.success("All TTS audio generated.")

        self.logger.info("Generating background image...")
        self._generate_background_image(plan.image_generation_prompt, os.path.join(project_dir, "background.png"))
        self.logger.success("Background image generated.")

    def generate_music_asset(self, plan: VideoPlan, duration_s: float, project_dir: str):
        """Generates the music track for the calculated video duration."""
        music_path = os.path.join(project_dir, "music.wav")
        self.logger.info(f"Generating music track for {duration_s:.2f}s...")
        try:
            asyncio.run(self._generate_music_with_timeout(plan.music_prompt, duration_s, music_path))
        except Exception as e:
            self.logger.warning(f"Music generation failed and will be SKIPPED. Reason: {e}")
            if os.path.exists(music_path):
                try:
                    os.remove(music_path)
                except OSError as os_e:
                    self.logger.error(f"Could not remove partial music file: {os_e}", exc_info=True)

    def _get_wav_duration(self, file_path: str) -> float:
        with wave.open(file_path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)

    def _generate_tts_audio(self, text: str, output_path: str) -> float:
        # --- Voice Selection Logic (NEW) ---
        if config.TTS_RANDOM_VOICE:
            chosen_voice = random.choice(config.TTS_VOICES)
            self.logger.info(f"Randomly selected voice for TTS: '{chosen_voice}'")
        else:
            chosen_voice = config.TTS_DEFAULT_VOICE
        
        log_details = {"text": text, "output_path": output_path, "voice": chosen_voice}
        # --- End Voice Selection ---
        
        if os.path.exists(output_path):
            duration = self._get_wav_duration(output_path)
            self.logger.info(f"Skipping existing TTS for '{text[:30]}...'.", details=log_details)
            return duration

        self.logger.info(f"Generating TTS for '{text[:30]}...'.", details=log_details)

        def api_call_and_validate(client: genai.Client):
            response = client.models.generate_content(
                model=config.TTS_MODEL, contents=f"Say: {text}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=chosen_voice)))
                )
            )
            if not response or not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
                error_detail = f"TTS API returned no valid content for text '{text}'."
                raise ContentGenerationError(error_detail)
            return response

        try:
            response = self._execute_with_retry(api_call_and_validate)
            time.sleep(config.TTS_DELAY_S)
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            with wave.open(output_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(audio_data)
            duration = self._get_wav_duration(output_path)
            self.logger.info(f"Saved TTS audio to {os.path.basename(output_path)} ({duration:.2f}s).", details=log_details)
            return duration
        except Exception as e:
            error_msg = f"Failed to generate TTS for '{text}' after all retries."
            self.logger.error(error_msg, exc_info=True, details=log_details)
            raise Exception(error_msg) from e

    def _generate_background_image(self, prompt: str, output_path: str):
        log_details = {"prompt": prompt, "output_path": output_path}
        if os.path.exists(output_path):
            self.logger.info("Skipping existing background image.", details=log_details)
            return
        self.logger.info("Requesting new background image from API.", details=log_details)

        def api_call_and_validate(client: genai.Client):
            response = client.models.generate_content(
                model=config.IMAGE_MODEL, contents=prompt,
                config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'])
            )
            if not response or not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
                raise ContentGenerationError(f"Image API returned no valid content for prompt: {prompt}")
            return response

        try:
            response = self._execute_with_retry(api_call_and_validate)
            time.sleep(config.IMAGE_DELAY_S)
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    Image.open(BytesIO(image_data)).save(output_path)
                    self.logger.info(f"Saved background image to {os.path.basename(output_path)}", details=log_details)
                    return
            raise Exception("No image data found in response, even though the candidate was valid.")
        except Exception as e:
            error_msg = f"Failed to generate background image after all retries."
            self.logger.error(error_msg, exc_info=True, details=log_details)
            raise Exception(error_msg) from e

    async def _generate_music_with_timeout(self, prompt: str, duration_s: float, output_path: str):
        log_details = {"prompt": prompt, "duration_s": duration_s, "output_path": output_path}
        if os.path.exists(output_path):
            self.logger.info("Skipping existing music track.", details=log_details)
            return
        timeout_margin = 60.0
        total_timeout = duration_s + timeout_margin
        self.logger.info(f"Requesting music track (timeout: {total_timeout:.0f}s).", details=log_details)
        try:
            await asyncio.wait_for(
                self._music_generation_logic(prompt, duration_s, output_path),
                timeout=total_timeout
            )
        except asyncio.TimeoutError:
            error_msg = f"Music generation timed out after {total_timeout:.0f} seconds."
            self.logger.error(error_msg, details=log_details)
            if os.path.exists(output_path):
                os.remove(output_path)
            raise Exception(error_msg)
        except Exception as e:
            self.logger.error(f"An error occurred during music generation: {e}", exc_info=True, details=log_details)
            raise e

    async def _music_generation_logic(self, prompt: str, duration_s: float, output_path: str):
        sample_rate, channels, sample_width = 48000, 2, 2
        target_bytes = int(duration_s * sample_rate * channels * sample_width)
        audio_buffer = bytearray()
        client = self.api_manager.get_client()
        async with client.aio.live.music.connect(model=config.MUSIC_MODEL) as session:
            await session.set_weighted_prompts(prompts=[types.WeightedPrompt(text=prompt, weight=1.0)])
            await session.set_music_generation_config(config=types.LiveMusicGenerationConfig(bpm=90, temperature=1.0))
            await session.play()
            async for message in session.receive():
                if message.server_content and message.server_content.audio_chunks:
                    for chunk in message.server_content.audio_chunks:
                        audio_buffer.extend(chunk.data)
                if len(audio_buffer) >= target_bytes:
                    self.logger.info("Target audio duration reached. Stopping stream capture.")
                    break
            await session.stop()
        if len(audio_buffer) < target_bytes:
            self.logger.warning(f"Stream ended before reaching target duration. Saved {len(audio_buffer) / (sample_rate * channels * sample_width):.2f}s of {duration_s:.2f}s requested.")
        final_audio = audio_buffer[:target_bytes]
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(final_audio)
        self.logger.success(f"Successfully generated music and saved to {os.path.basename(output_path)}") 
