import importlib
import os


def test_env_config_defaults():
    import dxf_generator.config.env_config as env_config
    assert env_config.config.API_PORT == int(os.getenv("API_PORT", 8000))
    assert env_config.config.API_WORKERS == int(os.getenv("API_WORKERS", 4))
    assert env_config.config.MAX_BATCH_SIZE == int(os.getenv("MAX_BATCH_SIZE", 50))
    assert env_config.config.ALLOWED_UPLOAD_EXTENSIONS == {".dxf"}


def test_env_config_overrides(monkeypatch):
    import dxf_generator.config.env_config as env_config

    monkeypatch.setenv("API_PORT", "9001")
    monkeypatch.setenv("API_RELOAD", "true")
    monkeypatch.setenv("MAX_BATCH_SIZE", "12")
    monkeypatch.setenv("MAX_IBEAM_DEPTH_MM", "1234.5")
    monkeypatch.setenv("MIN_IBEAM_WEB_THICKNESS_MM", "4.25")

    reloaded = importlib.reload(env_config)
    try:
        assert reloaded.config.API_PORT == 9001
        assert reloaded.config.API_RELOAD is True
        assert reloaded.config.MAX_BATCH_SIZE == 12
        assert reloaded.config.MAX_IBEAM_DEPTH_MM == 1234.5
        assert reloaded.config.MIN_IBEAM_WEB_THICKNESS_MM == 4.25
    finally:
        for key in [
            "API_PORT",
            "API_RELOAD",
            "MAX_BATCH_SIZE",
            "MAX_IBEAM_DEPTH_MM",
            "MIN_IBEAM_WEB_THICKNESS_MM",
        ]:
            monkeypatch.delenv(key, raising=False)
        importlib.reload(env_config)


def test_system_limits_respects_env_config(monkeypatch):
    import dxf_generator.config.env_config as env_config

    monkeypatch.setenv("MAX_BATCH_SIZE", "7")
    importlib.reload(env_config)
    try:
        import dxf_generator.config.system_limits as system_limits
        system_limits_reloaded = importlib.reload(system_limits)
        assert system_limits_reloaded.MAX_BATCH_SIZE == 7
    finally:
        monkeypatch.delenv("MAX_BATCH_SIZE", raising=False)
        importlib.reload(env_config)


def test_tolerances_respects_env_config(monkeypatch):
    import dxf_generator.config.env_config as env_config

    monkeypatch.setenv("MAX_IBEAM_DEPTH_MM", "2222")
    monkeypatch.setenv("MIN_IBEAM_WEB_THICKNESS_MM", "6.5")
    importlib.reload(env_config)
    try:
        import dxf_generator.config.tolerances as tolerances
        tolerances_reloaded = importlib.reload(tolerances)
        assert tolerances_reloaded.MAX_IBEAM_DEPTH_MM == 2222
        assert tolerances_reloaded.MIN_IBEAM_WEB_THICKNESS_MM == 6.5
    finally:
        monkeypatch.delenv("MAX_IBEAM_DEPTH_MM", raising=False)
        monkeypatch.delenv("MIN_IBEAM_WEB_THICKNESS_MM", raising=False)
        importlib.reload(env_config)


def test_logging_formatter_outputs_json():
    import json
    import logging
    from dxf_generator.config.logging_config import StructuredFormatter

    formatter = StructuredFormatter()
    record = logging.LogRecord(
        name="dxf_generator",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.duration_ms = 12.3
    record.status_code = 200

    parsed = json.loads(formatter.format(record))
    assert parsed["level"] == "INFO"
    assert parsed["message"] == "hello"
    assert parsed["duration_ms"] == 12.3
    assert parsed["status_code"] == 200
