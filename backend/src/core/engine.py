import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .models import Rule, Condition, ConditionOperator, MatchMode, Action, ActionType, AuditLogEntry, LogStatus
from .database import Database
from ..extractors.system_extractor import SystemExtractor
from ..extractors.text_extractor import TextExtractor
from ..extractors.pdf_extractor import PdfExtractor
from ..extractors.media_extractor import MediaExtractor
from ..actions.dispatcher import ActionDispatcher

# System-reserved variable keys that cannot be overwritten by dynamic regex capture groups
RESERVED_VARIABLE_KEYS = {
    "file.name", "file.stem", "file.extension", "file.size_bytes", "file.size_formatted",
    "file.created_date", "file.created_year", "file.created_month", "file.created_day",
    "file.modified_date", "file.directory", "file.path",
    "content.text", "content.snippet", "content.word_count", "content.line_count",
    "pdf.title", "pdf.author", "pdf.subject", "pdf.creator", "pdf.page_count", "pdf.created_date",
    "image.width", "image.height", "image.camera_make", "image.camera_model", "image.date_taken",
    "image.iso", "image.format"
}

class RuleEngine:
    def __init__(self, db: Database):
        self.db = db
        self.extractors = [
            SystemExtractor(),
            TextExtractor(),
            PdfExtractor(),
            MediaExtractor()
        ]

    def extract_variables(self, file_path: str) -> Dict[str, Any]:
        variables: Dict[str, Any] = {}
        for extractor in self.extractors:
            if extractor.can_handle(file_path):
                data = extractor.extract(file_path)
                variables.update(data)
        return variables

    def evaluate_condition(self, condition: Condition, variables: Dict[str, Any]) -> bool:
        field_val = variables.get(condition.field)
        target_val = condition.value

        # Field missing or null
        if field_val is None:
            return False

        op = condition.operator

        if op == ConditionOperator.EQUALS:
            return str(field_val).lower() == str(target_val).lower()

        elif op == ConditionOperator.NOT_EQUALS:
            return str(field_val).lower() != str(target_val).lower()

        elif op == ConditionOperator.CONTAINS:
            return str(target_val).lower() in str(field_val).lower()

        elif op == ConditionOperator.NOT_CONTAINS:
            return str(target_val).lower() not in str(field_val).lower()

        elif op == ConditionOperator.STARTS_WITH:
            return str(field_val).lower().startswith(str(target_val).lower())

        elif op == ConditionOperator.ENDS_WITH:
            return str(field_val).lower().endswith(str(target_val).lower())

        elif op == ConditionOperator.GREATER_THAN:
            try:
                return float(field_val) > float(target_val)
            except (ValueError, TypeError):
                return False

        elif op == ConditionOperator.LESS_THAN:
            try:
                return float(field_val) < float(target_val)
            except (ValueError, TypeError):
                return False

        elif op == ConditionOperator.MATCHES_REGEX:
            try:
                target_str = str(target_val)
                # Cap regex pattern length to prevent excessively complex nested patterns
                if len(target_str) > 1000:
                    return False
                # Limit evaluated text length to first 64 KB to mitigate ReDoS
                field_str = str(field_val)[:65536]
                match = re.search(target_str, field_str, re.IGNORECASE)
                if match:
                    # Save any named capture groups as dynamic variables safely!
                    groupdict = match.groupdict()
                    for k, v in groupdict.items():
                        is_reserved = (
                            k in RESERVED_VARIABLE_KEYS
                            or any(k.startswith(p) for p in ("file.", "content.", "pdf.", "image.", "system.", "date."))
                        )
                        if not is_reserved and k not in variables:
                            variables[k] = v
                        # Provide explicit custom namespace for unambiguous referencing
                        variables[f"custom.{k}"] = v
                    return True
                return False
            except (re.error, TimeoutError):
                return False

        elif op == ConditionOperator.BEFORE:
            try:
                dt_field = datetime.fromisoformat(str(field_val))
                dt_target = datetime.fromisoformat(str(target_val))
                return dt_field < dt_target
            except Exception:
                return False

        elif op == ConditionOperator.AFTER:
            try:
                dt_field = datetime.fromisoformat(str(field_val))
                dt_target = datetime.fromisoformat(str(target_val))
                return dt_field > dt_target
            except Exception:
                return False

        elif op == ConditionOperator.IN_LAST_DAYS:
            try:
                days = float(target_val)
                dt_field = datetime.fromisoformat(str(field_val))
                return dt_field >= (datetime.now() - timedelta(days=days))
            except Exception:
                return False

        return False

    def matches_rule(self, rule: Rule, variables: Dict[str, Any]) -> bool:
        if not rule.enabled:
            return False

        if not rule.conditions:
            return True  # A rule with no conditions matches all files

        # Filter by monitored folders if specified
        if rule.monitored_folders:
            file_dir = os.path.normpath(variables.get("file.parent_path", "")).lower()
            matched_folder = False
            for folder in rule.monitored_folders:
                norm_f = os.path.normpath(folder).lower()
                if file_dir == norm_f or file_dir.startswith(norm_f + os.sep) or file_dir.startswith(norm_f):
                    matched_folder = True
                    break
            if not matched_folder:
                return False

        results = [self.evaluate_condition(c, variables) for c in rule.conditions]

        if rule.match_mode == MatchMode.ALL:
            return all(results)
        else:
            return any(results)

    def process_file(self, file_path: str, rules: Optional[List[Rule]] = None) -> List[AuditLogEntry]:
        if not os.path.exists(file_path):
            return []

        if rules is None:
            rules = self.db.get_rules(enabled_only=True)

        current_path = os.path.abspath(file_path)
        stat = os.stat(current_path)
        mtime = stat.st_mtime
        logs: List[AuditLogEntry] = []

        for rule in rules:
            if not os.path.exists(current_path):
                break

            # Avoid re-processing the same file modification with the same rule
            if self.db.is_recently_processed(current_path, mtime, rule.id):
                continue

            # Extract full variables (cloned per rule)
            variables = self.extract_variables(current_path)

            if self.matches_rule(rule, variables):
                rule_matched = True
                
                # Execute actions in sequence
                for action in rule.actions:
                    status, dest_path, details = ActionDispatcher.execute(action, current_path, variables)
                    
                    log_entry = AuditLogEntry(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        source_path=current_path,
                        destination_path=dest_path,
                        action_type=action.type.value,
                        status=status,
                        details=details
                    )
                    self.db.add_log(log_entry)
                    logs.append(log_entry)

                    # Update current path if moved or renamed
                    if dest_path and status == LogStatus.SUCCESS and action.type in [ActionType.MOVE, ActionType.RENAME]:
                        current_path = dest_path

                    # If file deleted or recycled, stop remaining actions
                    if not os.path.exists(current_path):
                        break

                # Mark file as processed by this rule
                self.db.mark_processed(current_path, mtime, rule.id)

                if rule.stop_processing_on_match:
                    break

        return logs
