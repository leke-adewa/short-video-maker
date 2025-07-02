import json
import time
from pydantic import BaseModel, Field
from typing import List, Dict

from google.genai import types
from agent import config
from agent.api_manager import ApiKeyManager
from agent.logger import ProjectLogger

class WordPair(BaseModel):
    source_word: str = Field(description="The word/phrase in the source language.")
    target_word: str = Field(description="The translation of the word/phrase in the target language.")

class VideoPlan(BaseModel):
    project_slug: str = Field(description="A short, descriptive, 2-4 word slug for the project in kebab-case (e.g., 'japanese-bar-words').")
    source_language: str = Field(description="The language for the video's audience (e.g., 'Ukrainian'). Inferred from the user's prompt.")
    target_language: str = Field(description="The language being taught (e.g., 'Japanese'). Inferred from the user's prompt.")
    topic: str = Field(description="A short, descriptive topic for the video content (e.g., 'Essential Japanese Bar Vocabulary').")
    video_title: str = Field(description="A catchy, engaging video title in the source_language, suitable for social media.")
    video_description: str = Field(description="A brief video description in the source_language, explaining the content.")
    intro_text: str = Field(description="A clear intro in the source language that explains the format. Example: 'I will show you a word, and you have 5 seconds to remember the translation!'")
    word_pairs: List[WordPair] = Field(description="A list of words pairs for the lesson. Strictly adhere to the user's request for 'words' vs 'phrases'.")
    music_prompt: str = Field(description="A short prompt for generating background music (e.g., 'calm lofi beat', 'upbeat tokyo night vibe').")
    image_generation_prompt: str = Field(description="A detailed, creative prompt for an AI image generator to create a background image that fits the video's topic and mood. E.g., 'A vibrant, slightly abstract digital painting of a Japanese bar at night, with neon signs reflecting on wet pavement, cinematic, 9:16 aspect ratio.'")
    hashtags: List[str] = Field(description="A list of 8-12 relevant hashtags, including some in the source_language and some in the target_language.")

class ContentPlanner:
    def __init__(self, api_manager: ApiKeyManager, logger: ProjectLogger):
        self.api_manager = api_manager
        self.logger = logger

    def generate_plan(self, user_prompt: str) -> VideoPlan:
        self.logger.info("Starting content planning...", details={"user_prompt": user_prompt})

        system_instruction = (
            "You are an expert multilingual content planner for short-form language-learning videos. Your task is to analyze the user's prompt and create a detailed, structured plan in valid JSON, adhering strictly to the provided schema. Follow these rules meticulously:\n"
            "1. **Language Identification:** Correctly identify both the `source_language` (for the audience) and the `target_language` (to be learned) from the prompt. Do NOT default to English unless explicitly requested.\n"
            "2. **Content Specificity:** Pay close attention to the user's request for content type. If they ask for '5 words', provide exactly 5 single words. If they ask for '4 phrases', provide 4 phrases. If they ask for '7 Beatles songs', provide 7 song titles. Do not mix content types.\n"
            "3. **Introductory Text:** The `intro_text` must be in the `source_language` and clearly explain the video's interactive format (e.g., 'You will see a word and have X seconds to guess the translation.').\n"
            "4. **Metadata Generation:** Generate a `video_title` and `video_description` in the `source_language` for easy posting on social media.\n"
            "5. **Image Prompt:** Based on the `topic`, create a rich, descriptive `image_generation_prompt` for an AI image model. It should evoke a mood and style suitable for the content, and specify a vertical 9:16 aspect ratio.\n"
            "6. **Project Slug:** Create a short, clean, kebab-case `project_slug` that summarizes the video's theme.\n"
            "7. **Hashtags:** Provide a mix of relevant hashtags in both the source and target languages to maximize reach."
        )

        for attempt in range(len(self.api_manager.keys)):
            try:
                client = self.api_manager.get_client()
                self.logger.info("Generating video plan with Gemini...")
                response = client.models.generate_content(
                    model=config.PLANNER_MODEL,
                    contents=user_prompt,
                    config={
                        "system_instruction": system_instruction,
                        "response_mime_type": "application/json",
                        "response_schema": VideoPlan,
                    },
                )
                time.sleep(config.PLANNER_DELAY_S)
                
                if not response.parsed:
                    raise Exception("Model returned a valid response, but the JSON content could not be parsed.")
                
                plan_obj = response.parsed

                # --- Language Support Validation ---
                source_lang_lower = plan_obj.source_language.lower()
                target_lang_lower = plan_obj.target_language.lower()

                if source_lang_lower not in config.TTS_SUPPORTED_LANGUAGES:
                    raise ValueError(f"Source language '{plan_obj.source_language}' is not supported for TTS. Please choose from: {sorted(list(config.TTS_SUPPORTED_LANGUAGES))}")
                if target_lang_lower not in config.TTS_SUPPORTED_LANGUAGES:
                    raise ValueError(f"Target language '{plan_obj.target_language}' is not supported for TTS. Please choose from: {sorted(list(config.TTS_SUPPORTED_LANGUAGES))}")
                # --- End Validation ---

                self.logger.success("Successfully generated content plan.", details=plan_obj.model_dump())
                return plan_obj

            except Exception as e:
                if "429" in str(e) and "RESOURCE_EXHAUSTED" in str(e):
                    self.logger.warning(f"Planner hit quota limit: {e}")
                    try:
                        self.api_manager.switch_key()
                        continue
                    except Exception as switch_e:
                        self.logger.error(f"Failed to switch API key: {switch_e}", exc_info=True)
                        raise switch_e
                else:
                    self.logger.error(f"Content planning failed with non-quota error.", exc_info=True)
                    raise Exception(f"Content planning failed: {e}")
        
        raise Exception("Content planning failed: All API keys hit their quota limits.") 
