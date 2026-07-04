import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MODE
from homeassistant.core import HomeAssistant

from .const import *

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fanpy"

PLATFORMS = ["binary_sensor", "switch", "select"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await _generate_scripts_yaml(hass, entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    integration_dir = os.path.dirname(__file__)

    def _remove_file(filename):
        path = os.path.join(integration_dir, "generated", filename)
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        marker = f"# Prefix: {prefix}"
        if marker not in content:
            return
        lines = content.split("\n")
        result = []
        i = 0
        while i < len(lines):
            if lines[i].strip() == marker:
                i += 1
                while i < len(lines) and not lines[i].startswith("# Prefix:"):
                    i += 1
            else:
                result.append(lines[i])
                i += 1
        cleaned = "\n".join(result)
        if cleaned.strip():
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned + "\n")
        else:
            os.remove(path)

    await hass.async_add_executor_job(_remove_file, "scripts.yaml")



async def _generate_scripts_yaml(hass: HomeAssistant, entry: ConfigEntry) -> None:
    integration_dir = os.path.dirname(__file__)
    output_dir = os.path.join(integration_dir, "generated")
    os.makedirs(output_dir, exist_ok=True)
    scripts_path = os.path.join(output_dir, "scripts.yaml")

    entries = hass.config_entries.async_entries(DOMAIN)

    def _write():
        blocks = []
        for e in entries:
            d = e.data
            mode = d.get(CONF_MODE, CONF_MODE_REMOTE)
            p = d.get(CONF_PREFIX, "ventilador")
            n = d.get(CONF_NAME, p)

            if mode == CONF_MODE_REMOTE:
                ns = d.get(CONF_NUM_SPEEDS, 6)
                if ns <= 1:
                    ns = 0

                bd_id = d.get(CONF_BROADLINK_DEVICE_ID, "YOUR_BROADLINK_DEVICE_ID")
                be_id = d.get(CONF_BROADLINK_ENTITY_ID, "")
                rd = d.get(CONF_REMOTE_DEVICE, p)

                cmd_on = d.get(CONF_COMMAND_ON, DEFAULT_COMMAND_ON)
                cmd_off = d.get(CONF_COMMAND_OFF, DEFAULT_COMMAND_OFF)
                cmd_luz = d.get(CONF_COMMAND_LUZ, DEFAULT_COMMAND_LUZ)
                cmd_luz_calida = d.get(CONF_COMMAND_LUZ_CALIDA, DEFAULT_COMMAND_LUZ_CALIDA)
                cmd_luz_fria = d.get(CONF_COMMAND_LUZ_FRIA, DEFAULT_COMMAND_LUZ_FRIA)
                cmd_int_alta = d.get(CONF_COMMAND_INTENSIDAD_ALTA, DEFAULT_COMMAND_INTENSIDAD_ALTA)
                cmd_int_baja = d.get(CONF_COMMAND_INTENSIDAD_BAJA, DEFAULT_COMMAND_INTENSIDAD_BAJA)

                vcmd = {}
                for i in range(1, ns + 1):
                    key = f"{CONF_COMMAND_VELOCIDAD_PREFIX}_{i}"
                    vcmd[i] = d.get(key, f"{DEFAULT_COMMAND_VELOCIDAD_PREFIX}{i}")

                block = _build_scripts_yaml(
                    p, n, ns, d.get(CONF_HAS_LIGHT, False),
                    d.get(CONF_HAS_LIGHT_TEMPERATURE, False),
                    d.get(CONF_HAS_LIGHT_INTENSITY, False),
                    bd_id, be_id, rd,
                    cmd_on, cmd_off, cmd_luz, cmd_luz_calida, cmd_luz_fria,
                    cmd_int_alta, cmd_int_baja, vcmd,
                )
            else:
                block = ""

            if block.strip():
                blocks.append(block)

        content = "\n\n".join(blocks)
        if content.strip():
            with open(scripts_path, "w", encoding="utf-8") as f:
                f.write(content + "\n")
        else:
            if os.path.exists(scripts_path):
                os.remove(scripts_path)

    await hass.async_add_executor_job(_write)

    name = entry.data.get(CONF_NAME, entry.data.get(CONF_PREFIX, "ventilador"))
    _LOGGER.info("Fanpy: regenerated scripts.yaml for all entries")


def _build_scripts_yaml(
    prefix: str, name: str, num_speeds: int,
    has_light: bool, has_temp: bool, has_intensity: bool,
    broadlink_device_id: str, broadlink_entity_id: str, remote_device: str,
    cmd_on: str, cmd_off: str, cmd_luz: str,
    cmd_luz_calida: str, cmd_luz_fria: str,
    cmd_int_alta: str, cmd_int_baja: str,
    velocidad_commands: dict,
) -> str:
    lines = []

    def _target_block():
        if broadlink_entity_id:
            return f"      entity_id: {broadlink_entity_id}"
        if broadlink_device_id and broadlink_device_id != "YOUR_BROADLINK_DEVICE_ID":
            return f"      entity_id: {broadlink_device_id}"
        return "      entity_id: YOUR_BROADLINK_ENTITY_ID"

    def _append_script(action_name, display_name, command):
        lines.append(f"{prefix}_{action_name}:")
        lines.append("  sequence:")
        lines.append("  - action: remote.send_command")
        lines.append("    metadata: {}")
        lines.append("    data:")
        lines.append("      num_repeats: 1")
        lines.append("      delay_secs: 0.4")
        lines.append("      hold_secs: 0")
        lines.append(f"      device: {remote_device}")
        lines.append(f"      command: '{command}'")
        lines.append("    target:")
        lines.append(_target_block())
        lines.append(f"  alias: \"{display_name}\"")
        lines.append("  description: ''")
        lines.append("")

    lines.append(f"# Prefix: {prefix}")
    lines.append(f"# Name: {name}")
    lines.append(f"# Device ID: {broadlink_device_id}")
    lines.append("")

    _append_script("power_on", f"{name} Power ON", cmd_on)
    _append_script("power_off", f"{name} Power OFF", cmd_off)

    if has_light:
        _append_script("luz_on", f"{name} Luz ON", cmd_luz)
        _append_script("luz_off", f"{name} Luz OFF", cmd_luz)

        if has_temp:
            _append_script("luz_calida", f"{name} Luz Cálida", cmd_luz_calida)
            _append_script("luz_fria", f"{name} Luz Fría", cmd_luz_fria)

        if has_intensity:
            _append_script("intensidad_alta", f"{name} Intensidad Alta", cmd_int_alta)
            _append_script("intensidad_baja", f"{name} Intensidad Baja", cmd_int_baja)

    if num_speeds > 1:
        for i in range(1, num_speeds + 1):
            cmd = velocidad_commands.get(i, f"velocidad{i}")
            _append_script(f"velocidad_{i}", f"{name} Velocidad {i}", cmd)

    return "\n".join(lines)



