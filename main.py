import os
import argparse
from datetime import datetime
from dotenv import load_dotenv

from agent.database import DatabaseManager
from agent.api_manager import ApiKeyManager
from agent.planner import ContentPlanner, VideoPlan
from agent.asset_generator import AssetGenerator
from agent.composer import VideoComposer
from agent import config
from agent.logger import setup_logger, ProjectLogger

def run_project(project_id: int, project_name: str, project_dir: str, plan: VideoPlan, db_manager: DatabaseManager, api_manager: ApiKeyManager, logger: ProjectLogger):
    """The main project execution pipeline."""
    final_video_path = os.path.join(project_dir, "final_video.mp4")
    if os.path.exists(final_video_path):
        logger.success(f"Project '{project_name}' already has a final video. Skipping full run.")
        return project_name, plan
        
    asset_gen = AssetGenerator(api_manager, logger)
    composer = VideoComposer(logger)

    # --- Asset Generation ---
    db_manager.update_project_status(project_id, "Generating Core Assets")
    asset_gen.generate_core_assets(plan, project_dir)
    
    # --- Duration Calculation ---
    db_manager.update_project_status(project_id, "Calculating Duration")
    video_duration = composer.calculate_video_duration(plan, project_dir)

    # --- Music Generation ---
    db_manager.update_project_status(project_id, "Generating Music")
    asset_gen.generate_music_asset(plan, video_duration, project_dir)

    # --- Video Composition ---
    db_manager.update_project_status(project_id, "Composing Video")
    composer.create_video(plan, project_dir, video_duration)
    
    return project_name, plan

def _delete_asset(path: str, logger: ProjectLogger):
    """Safely deletes a file if it exists and logs the action."""
    if os.path.exists(path):
        try:
            os.remove(path)
            logger.info(f"Deleted existing asset: {os.path.basename(path)}")
        except OSError as e:
            logger.error(f"Could not delete asset {path}: {e}", exc_info=True)
            raise

def _load_project(arg_value, db_manager: DatabaseManager, logger: ProjectLogger, failed_only=False):
    """Loads project data based on an argument value (project name or True)."""
    if arg_value is True:
        if failed_only:
            logger.info("No project name specified, finding last failed project...")
            return db_manager.get_last_failed_project()
        else:
            logger.info("No project name specified, finding last project...")
            return db_manager.get_last_project()
    else:
        project_name = arg_value
        logger.info(f"Loading specified project: {project_name}")
        return db_manager.get_project_by_name(project_name)

def handle_regeneration(args, db_manager, api_manager, logger):
    """Handles all asset regeneration tasks."""
    task_flag_map = {
        'regenerate': args.regenerate,
        'regenerate_video': args.regenerate_video,
        'regenerate_background': args.regenerate_background,
        'regenerate_intro': args.regenerate_intro,
        'regenerate_music': args.regenerate_music,
        'regenerate_words': args.regenerate_words,
        'regenerate_word_0': args.regenerate_word_0
    }
    
    arg_value = None
    for flag, value in task_flag_map.items():
        if value is not None:
            arg_value = value
            break
    
    if arg_value is None:
        raise ValueError("Regeneration mode was entered, but no valid flag was found.")

    project_info = _load_project(arg_value, db_manager, logger)
    project_id = project_info["id"]
    logger.set_project_id(project_id)
    project_name = project_info["project_name"]
    project_dir = project_info["asset_directory"]
    plan = project_info["plan"]
    os.makedirs(project_dir, exist_ok=True)

    asset_gen = AssetGenerator(api_manager, logger)
    composer = VideoComposer(logger)

    if args.regenerate is not None:
        logger.status_update(f"Regenerating all assets for project: {project_name}")
        _delete_asset(os.path.join(project_dir, "background.png"), logger)
        _delete_asset(os.path.join(project_dir, "intro_audio.wav"), logger)
        for i in range(len(plan.word_pairs)):
            _delete_asset(os.path.join(project_dir, f"word_{i}.wav"), logger)
        _delete_asset(os.path.join(project_dir, "music.wav"), logger)
        _delete_asset(os.path.join(project_dir, "final_video.mp4"), logger)
        
        project_name, plan = run_project(project_id, project_name, project_dir, plan, db_manager, api_manager, logger)
        db_manager.update_project_status(project_id, "Completed")
        return project_name, plan

    # Handle individual asset regeneration below
    regenerated_video = False
    
    if args.regenerate_background:
        logger.status_update("Regenerating background image")
        _delete_asset(os.path.join(project_dir, "background.png"), logger)
        asset_gen._generate_background_image(plan.image_generation_prompt, os.path.join(project_dir, "background.png"))
    
    if args.regenerate_intro:
        logger.status_update("Regenerating intro audio")
        _delete_asset(os.path.join(project_dir, "intro_audio.wav"), logger)
        asset_gen._generate_tts_audio(plan.intro_text, os.path.join(project_dir, "intro_audio.wav"))

    if args.regenerate_words:
        logger.status_update("Regenerating all word audio files")
        for i, pair in enumerate(plan.word_pairs):
            _delete_asset(os.path.join(project_dir, f"word_{i}.wav"), logger)
            asset_gen._generate_tts_audio(pair.target_word, os.path.join(project_dir, f"word_{i}.wav"))

    if args.regenerate_word_0:
        logger.status_update("Regenerating word_0.wav")
        word_index = 0
        if len(plan.word_pairs) > word_index:
            pair = plan.word_pairs[word_index]
            _delete_asset(os.path.join(project_dir, f"word_{word_index}.wav"), logger)
            asset_gen._generate_tts_audio(pair.target_word, os.path.join(project_dir, f"word_{word_index}.wav"))
        else:
            logger.error(f"Project does not have a word at index {word_index}.")

    if args.regenerate_music:
        logger.status_update("Regenerating music track")
        _delete_asset(os.path.join(project_dir, "music.wav"), logger)
        db_manager.update_project_status(project_id, "Calculating Duration for Music")
        video_duration = composer.calculate_video_duration(plan, project_dir)
        db_manager.update_project_status(project_id, "Regenerating Music")
        asset_gen.generate_music_asset(plan, video_duration, project_dir)

    if args.regenerate_video:
        logger.status_update("Regenerating final video")
        _delete_asset(os.path.join(project_dir, "final_video.mp4"), logger)
        db_manager.update_project_status(project_id, "Calculating Duration for Video")
        video_duration = composer.calculate_video_duration(plan, project_dir)
        db_manager.update_project_status(project_id, "Regenerating Video")
        composer.create_video(plan, project_dir, video_duration)
        db_manager.update_project_status(project_id, "Completed")
        regenerated_video = True
    
    logger.success(f"Regeneration task for '{project_name}' completed.")
    if regenerated_video:
        return project_name, plan
    return None, None

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="AI Language Learning Video Agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", type=str, help="The creative prompt for a new video.")
    group.add_argument("--resume", nargs='?', const=True, default=None, help="Resume a project. Provide a project_name or leave blank to resume the last failed project.")
    group.add_argument("-r", "--regenerate", nargs='?', const=True, default=None, help="Regenerate all assets and video for a project. Provide a project_name or leave blank for the last project.")
    group.add_argument("-rv", "--regenerate-video", nargs='?', const=True, default=None, help="Regenerate only the final video file. Provide a project_name or leave blank for the last project.")
    group.add_argument("-rb", "--regenerate-background", nargs='?', const=True, default=None, help="Regenerate only the background image. Provide a project_name or leave blank for the last project.")
    group.add_argument("-ri", "--regenerate-intro", nargs='?', const=True, default=None, help="Regenerate only the intro audio. Provide a project_name or leave blank for the last project.")
    group.add_argument("-rm", "--regenerate-music", nargs='?', const=True, default=None, help="Regenerate only the music audio. Provide a project_name or leave blank for the last project.")
    group.add_argument("-rw", "--regenerate-words", nargs='?', const=True, default=None, help="Regenerate all word audio files. Provide a project_name or leave blank for the last project.")
    group.add_argument("-rw0", "--regenerate-word-0", nargs='?', const=True, default=None, help="Regenerate only word_0.wav audio. Provide a project_name or leave blank for the last project.")
    
    args = parser.parse_args()

    project_id = None
    logger = setup_logger()
    db_manager = None
    
    try:
        db_manager = DatabaseManager(config.DB_FILE, logger)
        api_manager = ApiKeyManager(logger)
        
        completed_name, completed_plan = None, None

        if args.prompt:
            user_prompt = args.prompt
            project_id = db_manager.create_preliminary_project(user_prompt)
            logger.set_project_id(project_id)
            logger.info(f"Project initialized with temporary ID: {project_id}")

            db_manager.update_project_status(project_id, "Planning")
            planner = ContentPlanner(api_manager, logger)
            plan_data = planner.generate_plan(user_prompt)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            project_name = f"{plan_data.project_slug}-{timestamp}"
            project_dir = os.path.join(config.OUTPUT_DIR, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            db_manager.save_plan_and_finalize_project(project_id, project_name, project_dir, plan_data)
            completed_name, completed_plan = run_project(project_id, project_name, project_dir, plan_data, db_manager, api_manager, logger)
            db_manager.update_project_status(project_id, "Completed")

        elif args.resume is not None:
            project_info = _load_project(args.resume, db_manager, logger, failed_only=True)
            project_id = project_info["id"]
            logger.set_project_id(project_id)
            project_dir = project_info["asset_directory"]
            project_name = project_info["project_name"]
            plan_data = project_info["plan"]
            logger.info(f"Successfully loaded plan for '{project_name}' from database.")
            completed_name, completed_plan = run_project(project_id, project_name, project_dir, plan_data, db_manager, api_manager, logger)
            db_manager.update_project_status(project_id, "Completed")
        
        else: # Regeneration tasks
            completed_name, completed_plan = handle_regeneration(args, db_manager, api_manager, logger)

        # --- Print final success summary if a video was produced ---
        if completed_name and completed_plan:
            project_dir = os.path.join(config.OUTPUT_DIR, completed_name)
            console = logger.console
            console.print("\n" + "✨" * 30, style="bold magenta")
            logger.success(f"Project '{completed_name}' completed successfully!")
            console.print(f"🎥 Final video archived in: [cyan]{project_dir}/[/cyan]")
            console.print("--------------------")
            console.print(f"✅ [bold]Title ({completed_plan.source_language}):[/bold] {completed_plan.video_title}")
            console.print(f"✅ [bold]Description ({completed_plan.source_language}):[/bold] {completed_plan.video_description}")
            console.print(f"✅ [bold]Hashtags:[/bold] {' '.join(completed_plan.hashtags)}")
            console.print("✨" * 30, style="bold magenta")

    except Exception as e:
        error_message = f"An unhandled error occurred in the main process: {e}"
        if logger:
            logger.error(error_message, exc_info=True)
            if project_id and db_manager:
                db_manager.update_project_status(project_id, "Failed")
        else:
            # Fallback for errors before logger initialization
            print(f"A fatal error occurred: {e}")

if __name__ == "__main__":
    main() 