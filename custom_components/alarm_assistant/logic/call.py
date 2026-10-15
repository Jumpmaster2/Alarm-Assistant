"""Phone call chain through the ha-sip add-on."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CallSettings:
    addon: str
    targets: tuple[str, ...]
    acknowledge: bool = True
    wait: float = 50
    platform: str = ""
    language: str = "de"
    answer_timeout: float = 30


def normalise_target(target: str) -> str:
    """Accept 'sip:...' or a plain number/user."""
    target = target.strip()
    return target if ":" in target else f"sip:{target}"


def plan(settings: CallSettings) -> list[tuple[str, bool]]:
    """Targets in order and whether the callee is asked to acknowledge.

    Every target except the last one may acknowledge (then the next one is not
    called); the last one only hears the announcement.
    """
    targets = [t for t in settings.targets if t.strip()]
    return [
        (target, settings.acknowledge and index < len(targets) - 1)
        for index, target in enumerate(targets)
    ]


def dial_input(
    settings: CallSettings,
    target: str,
    message: str,
    *,
    ack_entity: str | None = None,
    ack_message: str | None = None,
    ack_reply: str | None = None,
) -> dict[str, Any]:
    """Data for ``hassio.addon_stdin`` with the ha-sip ``dial`` command.

    With ``ack_entity`` the callee can press 1; ha-sip then presses that button
    entity in Home Assistant, which stops the chain.
    """
    menu: dict[str, Any] = {"message": message, "language": settings.language}
    if settings.platform:
        menu["platform"] = settings.platform
    if ack_entity:
        reply: dict[str, Any] = {
            "action": {"domain": "button", "service": "press", "entity_id": ack_entity},
            "message": ack_reply or "",
            "language": settings.language,
            "post_action": "hangup",
        }
        if settings.platform:
            reply["platform"] = settings.platform
        menu.update(
            {
                "message": ack_message or message,
                "wait_for_audio": True,
                "timeout": settings.answer_timeout,
                "input": "digit",
                "choices": {"1": reply},
                "on_invalid": "repeat",
                "on_timeout": "hangup",
            }
        )
    else:
        menu.update({"wait_for_audio_to_finish": True, "post_action": "hangup"})
    return {
        "addon": settings.addon,
        "input": {"command": "dial", "number": normalise_target(target), "menu": menu},
    }
