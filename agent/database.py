import sqlite3
import os
import json
from datetime import datetime
from agent.logger import ProjectLogger
from agent.planner import VideoPlan

class DatabaseManager:
    def __init__(self, db_file: str, logger: ProjectLogger):
        self.db_file = db_file
        self.logger = logger
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.setup_database()

    def setup_database(self):
        """Creates the necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT UNIQUE NOT NULL,
                prompt TEXT NOT NULL,
                status TEXT NOT NULL,
                asset_directory TEXT NOT NULL,
                plan_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        self.conn.commit()

    def create_preliminary_project(self, prompt: str) -> int:
        """Creates a temporary project record. Returns its ID."""
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        temp_name = f"temp_{timestamp}"
        cursor.execute('''
            INSERT INTO projects (project_name, prompt, status, asset_directory)
            VALUES (?, ?, ?, ?)
        ''', (temp_name, prompt, "Initialized", "temp"))
        self.conn.commit()
        return cursor.lastrowid

    def save_plan_and_finalize_project(self, project_id: int, project_name: str, asset_directory: str, plan: VideoPlan):
        """Updates the project with its final name, directory, and the full content plan."""
        cursor = self.conn.cursor()
        plan_json_str = plan.model_dump_json()
        cursor.execute('''
            UPDATE projects
            SET project_name = ?, asset_directory = ?, plan_json = ?, updated_at = ?
            WHERE id = ?
        ''', (project_name, asset_directory, plan_json_str, datetime.now(), project_id))
        self.conn.commit()
        self.logger.info(f"Project plan and final name '{project_name}' saved to database.")

    def update_project_status(self, project_id: int, status: str):
        """Updates the status of a project."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE projects
            SET status = ?, updated_at = ?
            WHERE id = ?
        ''', (status, datetime.now(), project_id))
        self.conn.commit()
        self.logger.status_update(status)

    def get_project_by_name(self, project_name: str) -> dict:
        """Retrieves project details by project_name."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, prompt, asset_directory, plan_json, project_name FROM projects WHERE project_name = ?
        ''', (project_name,))
        result = cursor.fetchone()
        if not result:
            raise FileNotFoundError(f"Project '{project_name}' not found in the database.")
        if not result[3]:
            raise ValueError(f"Project '{project_name}' found, but its plan has not been generated yet. Cannot proceed.")
        
        return {
            "id": result[0], 
            "prompt": result[1], 
            "asset_directory": result[2], 
            "plan": VideoPlan.model_validate_json(result[3]),
            "project_name": result[4] 
        }

    def get_last_failed_project(self) -> dict:
        """Retrieves the most recent project with a 'Failed' status."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, prompt, asset_directory, plan_json, project_name FROM projects 
            WHERE status = 'Failed' AND project_name NOT LIKE 'temp_%'
            ORDER BY updated_at DESC 
            LIMIT 1
        ''')
        result = cursor.fetchone()
        if not result:
            raise FileNotFoundError("No failed projects found in the database to resume.")
        if not result[3]:
             raise ValueError(f"Project '{result[4]}' found, but its plan has not been generated. Cannot resume.")
        self.logger.info(f"Found last failed project to resume: {result[4]}")
        return {"id": result[0], "prompt": result[1], "asset_directory": result[2], "plan": VideoPlan.model_validate_json(result[3]), "project_name": result[4]}

    def get_last_project(self) -> dict:
        """Retrieves the most recently updated project, regardless of status."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, prompt, asset_directory, plan_json, project_name FROM projects
            WHERE project_name NOT LIKE 'temp_%'
            ORDER BY updated_at DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        if not result:
            raise FileNotFoundError("No projects found in the database.")
        if not result[3]:
             raise ValueError(f"Project '{result[4]}' found, but its plan is missing. Cannot proceed.")
        self.logger.info(f"Found last project to operate on: {result[4]}")
        return {"id": result[0], "prompt": result[1], "asset_directory": result[2], "plan": VideoPlan.model_validate_json(result[3]), "project_name": result[4]}

    def __del__(self):
        if self.conn:
            self.conn.close() 