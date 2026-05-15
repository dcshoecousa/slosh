import logging

from app.core.logging import configure_logging
from app.core.settings.base import BaseAppSettings


def test_configure_logging_uses_text_format_by_default(monkeypatch) -> None:
    sink_calls: list[dict] = []
    original_get_logger = logging.getLogger

    monkeypatch.setattr("app.core.logging.logger.remove", lambda: None)
    monkeypatch.setattr("app.core.logging.logger.configure", lambda **kwargs: None)
    monkeypatch.setattr(
        "app.core.logging.logger.add",
        lambda sink, **kwargs: sink_calls.append({"sink": sink, **kwargs}),
    )
    monkeypatch.setattr("app.core.logging.logging.basicConfig", lambda **kwargs: None)
    monkeypatch.setattr(
        "app.core.logging.logging.getLogger",
        lambda name=None: original_get_logger(name),
    )

    configure_logging(BaseAppSettings(log_level="debug", log_json=False))

    assert len(sink_calls) == 1
    sink_call = sink_calls[0]
    assert sink_call["level"] == "DEBUG"
    assert sink_call["serialize"] is False
    assert sink_call["format"] != "{message}"
    assert "{extra[correlation_id]}" in sink_call["format"]


def test_configure_logging_can_enable_json_logs(monkeypatch) -> None:
    sink_calls: list[dict] = []
    original_get_logger = logging.getLogger

    monkeypatch.setattr("app.core.logging.logger.remove", lambda: None)
    monkeypatch.setattr("app.core.logging.logger.configure", lambda **kwargs: None)
    monkeypatch.setattr(
        "app.core.logging.logger.add",
        lambda sink, **kwargs: sink_calls.append({"sink": sink, **kwargs}),
    )
    monkeypatch.setattr("app.core.logging.logging.basicConfig", lambda **kwargs: None)
    monkeypatch.setattr(
        "app.core.logging.logging.getLogger",
        lambda name=None: original_get_logger(name),
    )

    configure_logging(BaseAppSettings(log_json=True))

    assert len(sink_calls) == 1
    sink_call = sink_calls[0]
    assert sink_call["serialize"] is True
    assert sink_call["format"] == "{message}"
