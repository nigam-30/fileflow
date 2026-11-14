from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class MatchMode(str, Enum):
    ALL = "all"  # AND
    ANY = "any"  # OR

class ConditionOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    MATCHES_REGEX = "matches_regex"
    BEFORE = "before"
    AFTER = "after"
    IN_LAST_DAYS = "in_last_days"

class ActionType(str, Enum):
    MOVE = "move"
    COPY = "copy"
    RENAME = "rename"
    DELETE = "delete"
    RECYCLE = "recycle"
    RUN_COMMAND = "run_command"
    NOTIFY = "notify"
    ZIP = "zip"

class CollisionPolicy(str, Enum):
    OVERWRITE = "overwrite"
    SKIP = "skip"
    RENAME_WITH_COUNTER = "rename_with_counter"

class Condition(BaseModel):
    field: str  # e.g. "file.extension", "file.size_mb", "file.name", "content.text", "pdf.title"
    operator: ConditionOperator
    value: Any

class Action(BaseModel):
    type: ActionType
    destination: Optional[str] = None  # path or folder template e.g. "D:/Sorted/{file.created_year}/"
    template: Optional[str] = None     # rename template e.g. "{file.created_date}_{vendor}_{file.name}"
    collision_policy: CollisionPolicy = CollisionPolicy.RENAME_WITH_COUNTER
    command: Optional[str] = None      # for RUN_COMMAND e.g. "python script.py {file.path}"
    notification_title: Optional[str] = None
    notification_message: Optional[str] = None

class Rule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    enabled: bool = True
    monitored_folders: List[str] = Field(default_factory=list)
    match_mode: MatchMode = MatchMode.ALL
    conditions: List[Condition] = Field(default_factory=list)
    actions: List[Action] = Field(default_factory=list)
    stop_processing_on_match: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())

class LogStatus(str, Enum):
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"
    INFO = "info"

class AuditLogEntry(BaseModel):
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    rule_id: Optional[str] = None
    rule_name: Optional[str] = None
    source_path: str
    destination_path: Optional[str] = None
    action_type: Optional[str] = None
    status: LogStatus
    details: Optional[str] = None
