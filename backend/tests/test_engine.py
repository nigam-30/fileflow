import os
import shutil
import tempfile
import pytest
from src.core.models import Rule, Condition, ConditionOperator, MatchMode, Action, ActionType, CollisionPolicy, LogStatus
from src.core.database import Database
from src.core.engine import RuleEngine

@pytest.fixture
def temp_workspace():
    tmp_dir = tempfile.mkdtemp(prefix="fileflow_test_")
    db_path = os.path.join(tmp_dir, "test.db")
    db = Database(db_path)
    engine = RuleEngine(db)
    
    yield tmp_dir, db, engine
    
    shutil.rmtree(tmp_dir, ignore_errors=True)

def test_system_extractor_and_condition_matching(temp_workspace):
    tmp_dir, db, engine = temp_workspace
    
    # Create a test text file
    test_file = os.path.join(tmp_dir, "report_2026.txt")
    with open(test_file, "w") as f:
        f.write("Project status report for year 2026. All tasks completed successfully.")

    variables = engine.extract_variables(test_file)
    assert variables["file.name"] == "report_2026.txt"
    assert variables["file.stem"] == "report_2026"
    assert variables["file.extension"] == "txt"
    assert "report" in variables["content.text"]

    # Test condition: file.extension == 'txt'
    cond1 = Condition(field="file.extension", operator=ConditionOperator.EQUALS, value="txt")
    assert engine.evaluate_condition(cond1, variables) is True

    # Test condition: content.text contains 'status'
    cond2 = Condition(field="content.text", operator=ConditionOperator.CONTAINS, value="status")
    assert engine.evaluate_condition(cond2, variables) is True

    # Test regex with named capture groups
    cond_regex = Condition(
        field="content.text",
        operator=ConditionOperator.MATCHES_REGEX,
        value=r"year\s+(?P<report_year>\d{4})"
    )
    assert engine.evaluate_condition(cond_regex, variables) is True
    assert variables.get("report_year") == "2026"

def test_rule_execution_move_and_rename(temp_workspace):
    tmp_dir, db, engine = temp_workspace
    
    source_folder = os.path.join(tmp_dir, "source")
    dest_folder = os.path.join(tmp_dir, "archive")
    os.makedirs(source_folder, exist_ok=True)

    test_file = os.path.join(source_folder, "invoice_450.pdf")
    with open(test_file, "w") as f:
        f.write("Simulated invoice document")

    # Define a rule that moves invoice files into archive folder and prefixes date
    rule = Rule(
        name="Archive Invoices",
        monitored_folders=[source_folder],
        match_mode=MatchMode.ALL,
        conditions=[
            Condition(field="file.extension", operator=ConditionOperator.EQUALS, value="pdf")
        ],
        actions=[
            Action(
                type=ActionType.MOVE,
                destination=dest_folder,
                template="{file.created_year}_{file.name}",
                collision_policy=CollisionPolicy.RENAME_WITH_COUNTER
            )
        ]
    )

    logs = engine.process_file(test_file, rules=[rule])
    assert len(logs) == 1
    assert logs[0].status == LogStatus.SUCCESS

    # Verify file is moved to archive folder
    expected_name = f"{logs[0].destination_path}"
    assert os.path.exists(expected_name)
    assert not os.path.exists(test_file)

    # Verify audit logs in database
    db_logs = db.get_logs()
    assert len(db_logs) >= 1
    assert db_logs[0].rule_name == "Archive Invoices"
