import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    mode = entry.data.get(CONF_MODE, CONF_MODE_REMOTE)
    if mode == CONF_MODE_DIRECT:
        return

    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    name = entry.data.get(CONF_NAME, prefix)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("switches", {})

    async_add_entities([
        FanPowerSwitch(hass, entry, prefix, name),
        FanLightSwitch(hass, entry, prefix, name),
    ])


class FanPowerSwitch(SwitchEntity):

    _attr_icon = "mdi:fan"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str) -> None:
        self._hass = hass
        self._entry = entry
        self._prefix = prefix
        self._attr_name = f"Fanpy {name} Power"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_power"
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()
        await self._hass.services.async_call(
            "script", f"{self._prefix}_power_on", {}, blocking=True
        )

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()
        await self._hass.services.async_call(
            "script", f"{self._prefix}_power_off", {}, blocking=True
        )


class FanLightSwitch(SwitchEntity):

    _attr_icon = "mdi:lightbulb"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str) -> None:
        self._hass = hass
        self._entry = entry
        self._prefix = prefix
        self._attr_name = f"Fanpy {name} Luz"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_luz"
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()
        await self._hass.services.async_call(
            "script", f"{self._prefix}_luz_on", {}, blocking=True
        )

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()
        await self._hass.services.async_call(
            "script", f"{self._prefix}_luz_off", {}, blocking=True
        )
