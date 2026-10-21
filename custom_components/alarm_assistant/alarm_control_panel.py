"""The alarm panel."""

from __future__ import annotations

from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
    CodeFormat,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .engine import AlarmConfigEntry, AlarmEngine
from .entity import AlarmEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AlarmConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([AlarmPanel(entry.runtime_data)])


class AlarmPanel(AlarmEntity, AlarmControlPanelEntity):
    """Alarm panel with the mode away."""

    _attr_name = None
    _attr_supported_features = AlarmControlPanelEntityFeature.ARM_AWAY

    def __init__(self, engine: AlarmEngine) -> None:
        super().__init__(engine, "panel")

    @property
    def alarm_state(self) -> AlarmControlPanelState:
        return AlarmControlPanelState(self.coordinator.state)

    @property
    def code_format(self) -> CodeFormat | None:
        return CodeFormat.NUMBER if self.coordinator.code_required else None

    @property
    def code_arm_required(self) -> bool:
        return self.coordinator.code_arm_required

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        engine = self.coordinator
        return {
            "open_sensors": [s.conf.name for s in engine.open_sensors()],
            "bypassed_sensors": list(engine.bypassed),
            "cause": engine.last_cause,
            "last_triggered": dt_util.as_local(engine.last_triggered).isoformat()
            if engine.last_triggered
            else None,
            "kids_home": engine.kids_home,
            "test_mode": engine.test_mode,
            "test_disabled": sorted(engine.test) if engine.test is not None else [],
        }

    async def _async_check(self, code: str | None, arming: bool) -> None:
        if not await self.coordinator.async_check_code(code, arming):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="wrong_code")

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        await self._async_check(code, True)
        check = self.coordinator.arm()
        if not check.ok:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="arm_failed",
                translation_placeholders={
                    "sensors": ", ".join(self.coordinator.sensor_name(e) for e in check.blocking)
                },
            )

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        await self._async_check(code, False)
        self.coordinator.disarm()
