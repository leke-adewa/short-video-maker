import sqlite3
import re
import json
from rich.console import Console
from typing import Optional, Dict, Any

class ProjectLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProjectLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path="output/projects.sqlite"):
        if not hasattr(self, 'initialized'):
            self.project_id: Optional[int] = None
            self.db_path = db_path
            self.console = Console(highlight=False, force_terminal=True)
            self.emoji_map = {
                "INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "STATUS": "🔄", "SUCCESS": "✅"
            }
            self.initialized = True

    def _get_db_connection(self):
        # Creates a new connection for each thread-local operation
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def set_project_id(self, project_id: int):
        self.project_id = project_id

    def _log_to_db(self, level: str, message: str, details: Optional[Dict[str, Any]] = None):
        if self.project_id is None:
            # Don't log to DB if project context is not set, but still print to console
            return
        details_json = json.dumps(details, indent=2) if details else None
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO logs (project_id, level, message, details) VALUES (?, ?, ?, ?)',
                    (self.project_id, level, message, details_json)
                )
                conn.commit()
        except Exception as e:
            self.console.print(f"[bold red]DB LOGGING FAILED: {e}[/bold red]")

    def _clean_message_for_console(self, message: str, level: str) -> str:
        # Hide full paths and other verbose info from console
        message = re.sub(r'output/[^/\s]+/', '', message)
        if level == "INFO":
            if "Skipping existing" in message:
                return "Asset already exists, skipping generation."
            if "Generating TTS for" in message:
                return "Generating new TTS audio..."
        if level == "WARNING" and "429 RESOURCE_EXHAUSTED" in message:
            return "API rate limit reached. Attempting to switch key."
        return message

    def _log(self, level: str, message: str, style: str, exc_info=False, details: Optional[Dict[str, Any]] = None):
        # Always log the full, detailed message to the DB
        self._log_to_db(level, message, details)
        
        # Print a cleaner, more concise message to the console
        clean_message = self._clean_message_for_console(message, level)
        emoji = self.emoji_map.get(level, "🔹")
        self.console.print(f"{emoji} [{style}]{level:<7}[/{style}] {clean_message}")
        
        if exc_info:
            self.console.print_exception(show_locals=False)

    def info(self, message: str, details: Optional[Dict[str, Any]] = None):
        self._log("INFO", message, "cyan", details=details)

    def warning(self, message: str, details: Optional[Dict[str, Any]] = None):
        self._log("WARNING", message, "yellow", details=details)

    def error(self, message: str, exc_info=False, details: Optional[Dict[str, Any]] = None):
        self._log("ERROR", message, "bold red", exc_info=exc_info, details=details)
        
    def success(self, message: str, details: Optional[Dict[str, Any]] = None):
        self._log("SUCCESS", message, "bold green", details=details)

    def status_update(self, message: str):
        emoji = self.emoji_map.get("STATUS", "🔄")
        self.console.print(f"\n[bold magenta]--- {emoji} {message} ---[/bold magenta]")
        self._log_to_db("INFO", f"Project status changed to: {message}")

def setup_logger():
    return ProjectLogger() 
