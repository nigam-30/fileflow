import os
import shutil
import subprocess
import zipfile
from typing import Dict, Any, Optional, Tuple
from ..core.models import Action, ActionType, CollisionPolicy, AuditLogEntry, LogStatus

class ActionDispatcher:
    @staticmethod
    def resolve_template(template_str: str, variables: Dict[str, Any]) -> str:
        if not template_str:
            return ""
        result = template_str
        for key, val in variables.items():
            token = f"{{{key}}}"
            if token in result:
                result = result.replace(token, str(val))
        return result

    @staticmethod
    def get_unique_path(target_path: str) -> str:
        if not os.path.exists(target_path):
            return target_path
        
        dirname = os.path.dirname(target_path)
        base = os.path.basename(target_path)
        stem, ext = os.path.splitext(base)
        counter = 1

        while True:
            candidate = os.path.join(dirname, f"{stem} ({counter}){ext}")
            if not os.path.exists(candidate):
                return candidate
            counter += 1

    @classmethod
    def execute(cls, action: Action, source_path: str, variables: Dict[str, Any]) -> Tuple[LogStatus, Optional[str], Optional[str]]:
        """
        Executes an action on source_path using resolved variables.
        Returns: (LogStatus, destination_path, details_message)
        """
        if not os.path.exists(source_path):
            return LogStatus.FAILED, None, f"Source file does not exist: {source_path}"

        try:
            if action.type == ActionType.MOVE:
                return cls._execute_move(action, source_path, variables)
            elif action.type == ActionType.COPY:
                return cls._execute_copy(action, source_path, variables)
            elif action.type == ActionType.RENAME:
                return cls._execute_rename(action, source_path, variables)
            elif action.type == ActionType.RECYCLE:
                return cls._execute_recycle(source_path)
            elif action.type == ActionType.DELETE:
                return cls._execute_delete(source_path)
            elif action.type == ActionType.ZIP:
                return cls._execute_zip(action, source_path, variables)
            elif action.type == ActionType.RUN_COMMAND:
                return cls._execute_command(action, source_path, variables)
            elif action.type == ActionType.NOTIFY:
                return cls._execute_notify(action, variables)
            else:
                return LogStatus.FAILED, None, f"Unsupported action type: {action.type}"
        except Exception as e:
            return LogStatus.FAILED, None, f"Action execution error: {str(e)}"

    @classmethod
    def _execute_move(cls, action: Action, source_path: str, variables: Dict[str, Any]) -> Tuple[LogStatus, Optional[str], Optional[str]]:
        dest_dir = cls.resolve_template(action.destination or "", variables)
        if not dest_dir:
            return LogStatus.FAILED, None, "Move destination directory not specified"
        
        dest_dir = os.path.abspath(dest_dir)
        os.makedirs(dest_dir, exist_ok=True)

        filename = os.path.basename(source_path)
        if action.template:
            filename = cls.resolve_template(action.template, variables)
            # Ensure extension is preserved if template didn't specify one
            orig_ext = os.path.splitext(source_path)[1]
            if not os.path.splitext(filename)[1] and orig_ext:
                filename = filename + orig_ext

        target_file = os.path.join(dest_dir, filename)

        # Handle collision
        if os.path.exists(target_file):
            if action.collision_policy == CollisionPolicy.SKIP:
                return LogStatus.SKIPPED, target_file, "Destination file already exists, skipped by policy"
            elif action.collision_policy == CollisionPolicy.RENAME_WITH_COUNTER:
                target_file = cls.get_unique_path(target_file)
            elif action.collision_policy == CollisionPolicy.OVERWRITE:
                try:
                    os.remove(target_file)
                except Exception:
                    pass

        shutil.move(source_path, target_file)
        return LogStatus.SUCCESS, target_file, f"Moved to {target_file}"

    @classmethod
    def _execute_copy(cls, action: Action, source_path: str, variables: Dict[str, Any]) -> Tuple[LogStatus, Optional[str], Optional[str]]:
        dest_dir = cls.resolve_template(action.destination or "", variables)
        if not dest_dir:
            return LogStatus.FAILED, None, "Copy destination directory not specified"

        dest_dir = os.path.abspath(dest_dir)
        os.makedirs(dest_dir, exist_ok=True)

        filename = os.path.basename(source_path)
        if action.template:
            filename = cls.resolve_template(action.template, variables)
            orig_ext = os.path.splitext(source_path)[1]
            if not os.path.splitext(filename)[1] and orig_ext:
                filename = filename + orig_ext

        target_file = os.path.join(dest_dir, filename)

        if os.path.exists(target_file):
            if action.collision_policy == CollisionPolicy.SKIP:
                return LogStatus.SKIPPED, target_file, "Destination file already exists, skipped by policy"
            elif action.collision_policy == CollisionPolicy.RENAME_WITH_COUNTER:
                target_file = cls.get_unique_path(target_file)

        shutil.copy2(source_path, target_file)
        return LogStatus.SUCCESS, target_file, f"Copied to {target_file}"

    @classmethod
    def _execute_rename(cls, action: Action, source_path: str, variables: Dict[str, Any]) -> Tuple[LogStatus, Optional[str], Optional[str]]:
        if not action.template:
            return LogStatus.FAILED, None, "Rename template not specified"

        dest_dir = os.path.dirname(source_path)
        new_name = cls.resolve_template(action.template, variables)
        orig_ext = os.path.splitext(source_path)[1]
        if not os.path.splitext(new_name)[1] and orig_ext:
            new_name = new_name + orig_ext

        target_file = os.path.join(dest_dir, new_name)
        if target_file == source_path:
            return LogStatus.SKIPPED, source_path, "Filename unchanged"

        if os.path.exists(target_file):
            if action.collision_policy == CollisionPolicy.SKIP:
                return LogStatus.SKIPPED, target_file, "Target filename already exists"
            elif action.collision_policy == CollisionPolicy.RENAME_WITH_COUNTER:
                target_file = cls.get_unique_path(target_file)

        os.rename(source_path, target_file)
        return LogStatus.SUCCESS, target_file, f"Renamed to {os.path.basename(target_file)}"

    @classmethod
    def _execute_recycle(cls, source_path: str) -> Tuple[LogStatus, Optional[str], Optional[str]]:
        from send2trash import send2trash
        send2trash(source_path)
        return LogStatus.SUCCESS, None, f"Sent {os.path.basename(source_path)} to Recycle Bin"

    @classmethod
    def _execute_delete(cls, source_path: str) -> Tuple[LogStatus, Optional[str], Optional[str]]:
        os.remove(source_path)
        return LogStatus.SUCCESS, None, f"Permanently deleted {os.path.basename(source_path)}"

    @classmethod
    def _execute_zip(cls, action: Action, source_path: str, variables: Dict[str, Any]) -> Tuple[LogStatus, Optional[str], Optional[str]]:
        dest_dir = cls.resolve_template(action.destination or os.path.dirname(source_path), variables)
        os.makedirs(dest_dir, exist_ok=True)
        
        stem = variables.get("file.stem", "archive")
        zip_path = os.path.join(dest_dir, f"{stem}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(source_path, arcname=os.path.basename(source_path))

        return LogStatus.SUCCESS, zip_path, f"Archived to {zip_path}"

    @classmethod
    def _execute_command(cls, action: Action, source_path: str, variables: Dict[str, Any]) -> Tuple[LogStatus, Optional[str], Optional[str]]:
        if not action.command:
            return LogStatus.FAILED, None, "No command specified"
        
        cmd = cls.resolve_template(action.command, variables)
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if proc.returncode == 0:
            return LogStatus.SUCCESS, None, f"Executed command: {cmd}"
        else:
            return LogStatus.FAILED, None, f"Command exited with error ({proc.returncode}): {proc.stderr.strip()}"

    @classmethod
    def _execute_notify(cls, action: Action, variables: Dict[str, Any]) -> Tuple[LogStatus, Optional[str], Optional[str]]:
        title = cls.resolve_template(action.notification_title or "FileFlow Alert", variables)
        msg = cls.resolve_template(action.notification_message or "A rule was triggered.", variables)
        # Windows toast or console notification
        print(f"[NOTIFICATION] {title}: {msg}")
        return LogStatus.SUCCESS, None, f"Notification sent: {title} - {msg}"
