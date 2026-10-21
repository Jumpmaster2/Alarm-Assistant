"""Diagnostics do not contain private values."""

from __future__ import annotations

from homeassistant.config_entries import ConfigSubentryData
from homeassistant.core import HomeAssistant

from custom_components.alarm_assistant.const import SUBENTRY_PERSON
from custom_components.alarm_assistant.diagnostics import async_get_config_entry_diagnostics
from custom_components.alarm_assistant.logic.code import hash_code

from .conftest import WIFI_A, make_entry, setup_entry

REDACTED = "**REDACTED**"


async def test_diagnostics_are_redacted(hass: HomeAssistant, base_states) -> None:
    person = ConfigSubentryData(
        data={"wifi_sensor": WIFI_A},
        subentry_id="p1",
        subentry_type=SUBENTRY_PERSON,
        title="Alex",
        unique_id=None,
    )
    entry = make_entry(
        extra_subentries=[person],
        code=hash_code("1234"),
        call_addon="abcd_ha-sip",
        call_targets=["+49170111222"],
        home_networks=["MyWifi"],
        night_tag="tag-secret",
    )
    await setup_entry(hass, entry)
    diag = await async_get_config_entry_diagnostics(hass, entry)
    options = diag["entry"]["options"]
    for key in ("code", "call_addon", "call_targets", "home_networks", "night_tag"):
        assert options[key] == REDACTED
    text = str(diag)
    for secret in ("+49170111222", "MyWifi", "tag-secret", "Alex", hash_code("1234")):
        assert secret not in text
    assert options["entry_delay"] == 30
    assert diag["state"]["state"] == "disarmed"
