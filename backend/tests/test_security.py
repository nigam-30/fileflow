import os
import sys
import tempfile
import shutil
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(TEST_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from src.api.server import app, get_or_create_api_token, set_api_token
from src.core.models import Action, ActionType, Condition, ConditionOperator, Rule, MatchMode
from src.core.database import Database
from src.core.engine import RuleEngine
from src.core.duplicate_finder import DuplicateFinder
from src.actions.dispatcher import ActionDispatcher

@pytest.fixture
def api_client():
    token = "test_secret_token_1234567890abcdef"
    set_api_token(token)
    os.environ["FILEFLOW_DISABLE_AUTH"] = "0"
    client = TestClient(app)
    yield client, token
    set_api_token("")

def test_auth_token_enforcement(api_client):
    client, token = api_client

    # 1. Request without token must be rejected with 401 Unauthorized
    res_no_token = client.get("/api/rules")
    assert res_no_token.status_code == 401
    assert "Unauthorized" in res_no_token.json()["detail"]

    # 2. Request with invalid token must be rejected with 401 Unauthorized
    res_bad_token = client.get("/api/rules", headers={"X-FileFlow-Token": "wrong_token"})
    assert res_bad_token.status_code == 401

    # 3. Request with valid token must succeed
    res_good_token = client.get("/api/rules", headers={"X-FileFlow-Token": token})
    assert res_good_token.status_code == 200

def test_cors_restriction(api_client):
    client, token = api_client

    # 1. CORS Preflight from malicious external origin must NOT allow access
    res_evil = client.options(
        "/api/rules",
        headers={
            "Origin": "https://malicious-driveby-website.com",
            "Access-Control-Request-Method": "POST",
        }
    )
    assert res_evil.headers.get("access-control-allow-origin") != "https://malicious-driveby-website.com"
    assert res_evil.headers.get("access-control-allow-origin") != "*"

    # 2. CORS Preflight from localhost origin is allowed
    res_local = client.options(
        "/api/rules",
        headers={
            "Origin": "http://127.0.0.1:8765",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert res_local.headers.get("access-control-allow-origin") == "http://127.0.0.1:8765"

def test_path_traversal_prevention(api_client):
    client, token = api_client

    # Path traversal attempting to read windows system file
    res = client.get("/C:/Windows/win.ini")
    # Must NOT serve win.ini (either 200 serving index.html fallback or 404, but NOT win.ini contents)
    assert "[fonts]" not in res.text.lower()
    assert "[extensions]" not in res.text.lower()

    # Relative directory traversal
    res_traversal = client.get("/../../../../Windows/win.ini")
    assert "[fonts]" not in res_traversal.text.lower()

def test_command_injection_prevention():
    # Test that dangerous shell metacharacters in variables are treated as literal arguments
    variables = {
        "file.name": "sample & calc.exe & test.txt",
        "file.stem": "sample & calc.exe & test"
    }
    
    # Run a safe command using sys.executable that prints sys.argv[1]
    cmd = f'"{sys.executable}" -c "import sys; print(sys.argv[1])" {{file.name}}'
    action = Action(type=ActionType.RUN_COMMAND, command=cmd)

    status, dest, details = ActionDispatcher.execute(action, source_path=sys.executable, variables=variables)
    assert status.value == "success"
    # The printed argument is literally "sample & calc.exe & test.txt", NOT executed separately!
    assert "sample & calc.exe & test.txt" in details

def test_arbitrary_file_deletion_prevention(api_client):
    client, token = api_client

    tmp = tempfile.mkdtemp(prefix="ff_sec_test_")
    try:
        secret_file = os.path.join(tmp, "unauthorized_file.txt")
        with open(secret_file, "w") as f:
            f.write("Important private file")

        # Deleting a file that is not in scanned duplicates and not in monitored folders must fail with 403 Forbidden
        res = client.post(
            "/api/duplicates/delete",
            json={"file_path": secret_file, "recycle": False},
            headers={"X-FileFlow-Token": token}
        )
        assert res.status_code == 403
        assert os.path.exists(secret_file)

        # Now simulate file being an authorized duplicate discovered in scan
        DuplicateFinder.record_scanned_duplicates([secret_file])
        res_auth = client.post(
            "/api/duplicates/delete",
            json={"file_path": secret_file, "recycle": False},
            headers={"X-FileFlow-Token": token}
        )
        assert res_auth.status_code == 200
        assert not os.path.exists(secret_file)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def test_open_external_scheme_validation(api_client):
    client, token = api_client

    # 1. file:// URI scheme must be rejected
    res_file = client.post(
        "/api/open-external",
        json={"url": "file:///C:/Windows/System32/calc.exe"},
        headers={"X-FileFlow-Token": token}
    )
    assert res_file.status_code == 400
    assert "Only HTTP and HTTPS" in res_file.json()["detail"]

    # 2. Dangerous custom URI scheme must be rejected
    res_custom = client.post(
        "/api/open-external",
        json={"url": "ms-msdt:/id PCWDiagnostic"},
        headers={"X-FileFlow-Token": token}
    )
    assert res_custom.status_code == 400

    # 3. Invalid host must be rejected
    res_bad_host = client.post(
        "/api/open-external",
        json={"url": "https://"},
        headers={"X-FileFlow-Token": token}
    )
    assert res_bad_host.status_code == 400

def test_regex_variable_pollution_and_limits():
    tmp_dir = tempfile.mkdtemp()
    try:
        db = Database(os.path.join(tmp_dir, "test.db"))
        engine = RuleEngine(db)

        variables = {
            "file.name": "invoice_1234.pdf",
            "file.path": "C:\\safe\\path\\invoice_1234.pdf",
            "content.text": "Invoice # 9988 for order"
        }

        # Attempt to overwrite reserved system variable 'file.path' via named capture group
        cond_pollute = Condition(
            field="file.name",
            operator=ConditionOperator.MATCHES_REGEX,
            value=r"(?P<file_path>C:\\hacked\\destination)"
        )
        # Condition will match if filename contains path pattern or if group is named file_path
        # Let's test with a match
        cond_pollute_match = Condition(
            field="file.name",
            operator=ConditionOperator.MATCHES_REGEX,
            value=r"(?P<file_name>hacked_name)"
        )
        # Even if someone names a group 'file.name' or 'file_name':
        # Let's test named group 'file.path' if allowed by python regex (note: python regex allows valid identifiers)
        cond_custom = Condition(
            field="content.text",
            operator=ConditionOperator.MATCHES_REGEX,
            value=r"Invoice #\s+(?P<invoice_id>\d+)"
        )
        assert engine.evaluate_condition(cond_custom, variables) is True
        assert variables.get("invoice_id") == "9988"
        assert variables.get("custom.invoice_id") == "9988"

        # Regex length cap: excessively long pattern (>1000 chars) must return False safely
        long_pattern = "a" * 1500
        cond_long = Condition(field="file.name", operator=ConditionOperator.MATCHES_REGEX, value=long_pattern)
        assert engine.evaluate_condition(cond_long, variables) is False
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
