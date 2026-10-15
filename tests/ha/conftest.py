"""Fixtures for tests with a Home Assistant test instance."""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentryData
from homeassistant.const import EVENT_CALL_SERVICE
from homeassistant.core import Event, HomeAssistant, ServiceCall, callback
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    async_mock_service,
)

from custom_components.alarm_assistant.const import DEFAULTS, DOMAIN, SUBENTRY_SENSOR

WINDOW = "binary_sensor.kitchen_window"
DOOR = "binary_sensor.front_door"
MOTION = "binary_sensor.hall_motion"
BALCONY = "binary_sensor.balcony_door"
AIRCON = "climate.aircon"
BALCONY_COVER = "cover.balcony"
VACUUM = "vacuum.robot"
FAULT = "binary_sensor.robot_bridge_fault"
LOCK = "lock.front_door"
WIFI_A = "sensor.phone_a_wifi"
WIFI_B = "sensor.phone_b_wifi"
HOME = "HomeNet"
PANEL = "alarm_control_panel.alarm_assistant"

SENSORS = [
    ("s_window", "Kitchen window", {"entity": WINDOW, "type": "window"}),
    ("s_door", "Front door", {"entity": DOOR, "type": "door"}),
    ("s_motion", "Hall motion", {"entity": MOTION, "type": "motion", "camera_preset": "Hall"}),
    (
        "s_balcony",
        "Balcony door",
        {
            "entity": BALCONY,
            "type": "window",
            "only_when_unavailable": AIRCON,
            "arm_cover": BALCONY_COVER,
            "arm_cover_position": 20,
        },
    ),
]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of custom integrations."""
    return


@pytest.fixture(autouse=True)
def no_pauses():
    """Short pauses inside reaction sequences return immediately."""
    with patch("custom_components.alarm_assistant.engine._sleep", AsyncMock()) as mock:
        yield mock


@pytest.fixture
async def setup_location(hass: HomeAssistant) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    hass.config.language = "en"


@pytest.fixture
def calls(hass: HomeAssistant) -> dict[str, list[ServiceCall]]:
    """Record the service calls of the reactions."""
    return {
        "notify": async_mock_service(hass, "notify", "phone"),
        "pushover": async_mock_service(hass, "notify", "pushover"),
        "admin": async_mock_service(hass, "notify", "admin"),
        "speak": async_mock_service(hass, "notify", "speaker"),
        "send_message": async_mock_service(hass, "notify", "send_message"),
        "volume": async_mock_service(hass, "media_player", "volume_set"),
        "sound": async_mock_service(hass, "alexa_devices", "send_sound"),
        "turn_on": async_mock_service(hass, "homeassistant", "turn_on"),
        "turn_off": async_mock_service(hass, "homeassistant", "turn_off"),
        "light_on": async_mock_service(hass, "light", "turn_on"),
        "close_cover": async_mock_service(hass, "cover", "close_cover"),
        "set_cover_position": async_mock_service(hass, "cover", "set_cover_position"),
        "lock": async_mock_service(hass, "lock", "lock"),
        "stdin": async_mock_service(hass, "hassio", "addon_stdin"),
        "select": async_mock_service(hass, "select", "select_option"),
    }


@pytest.fixture
def service_events(hass: HomeAssistant) -> list[tuple[str, str, dict[str, Any]]]:
    """All service calls (also of domains our platforms load, whose services are real)."""
    events: list[tuple[str, str, dict[str, Any]]] = []

    @callback
    def record(event: Event) -> None:
        events.append(
            (event.data["domain"], event.data["service"], dict(event.data["service_data"]))
        )

    hass.bus.async_listen(EVENT_CALL_SERVICE, record)
    return events


def calls_of(
    events: list[tuple[str, str, dict[str, Any]]], domain: str, service: str
) -> list[dict[str, Any]]:
    return [data for d, s, data in events if d == domain and s == service]


START = "2026-10-15 12:00:00+02:00"


@pytest.fixture
async def base_states(hass: HomeAssistant, setup_location, freezer: FrozenDateTimeFactory) -> None:
    """All sensors closed, set 30 minutes before the test starts."""
    freezer.move_to("2026-10-15 11:30:00+02:00")
    for entity_id in (WINDOW, DOOR, MOTION, BALCONY, FAULT):
        hass.states.async_set(entity_id, "off")
    hass.states.async_set(AIRCON, "unavailable")
    hass.states.async_set(BALCONY_COVER, "open", {"current_position": 100})
    hass.states.async_set(VACUUM, "docked", {"is_docked": True})
    hass.states.async_set(LOCK, "unlocked")
    hass.states.async_set(WIFI_A, HOME)
    hass.states.async_set(WIFI_B, HOME)
    await hass.async_block_till_done()
    freezer.move_to(START)


def make_entry(
    sensors: list[tuple[str, str, dict[str, Any]]] | None = None,
    extra_subentries: list[ConfigSubentryData] | None = None,
    **options: Any,
) -> MockConfigEntry:
    subentries = [
        ConfigSubentryData(
            data=data,
            subentry_id=sub_id,
            subentry_type=SUBENTRY_SENSOR,
            title=title,
            unique_id=None,
        )
        for sub_id, title, data in (SENSORS if sensors is None else sensors)
    ]
    return MockConfigEntry(
        domain=DOMAIN,
        title="Alarm Assistant",
        data={},
        options={
            **DEFAULTS,
            "notify_services": ["notify.phone"],
            "notify_alarm_services": ["notify.pushover"],
            "notify_admin_services": ["notify.admin"],
            "vacuum": VACUUM,
            "fault_sensor": FAULT,
            **options,
        },
        subentries_data=subentries + (extra_subentries or []),
    )


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def advance(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, seconds: float, step: float = 30
) -> None:
    """Move time forward in steps and fire the time listeners."""
    remaining = seconds
    while remaining > 0:
        delta = min(step, remaining)
        freezer.tick(timedelta(seconds=delta))
        async_fire_time_changed(hass)
        await hass.async_block_till_done(wait_background_tasks=True)
        remaining -= delta


async def set_state(hass: HomeAssistant, entity_id: str, state: str, attrs=None) -> None:
    hass.states.async_set(entity_id, state, attrs or {})
    await hass.async_block_till_done(wait_background_tasks=True)
