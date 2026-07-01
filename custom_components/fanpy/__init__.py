import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_MODE
from homeassistant.core import HomeAssistant

from .const import *

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fanpy"

PLATFORMS = ["binary_sensor", "button"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    mode = entry.data.get(CONF_MODE, CONF_MODE_HELPERS)
    if mode == CONF_MODE_HELPERS:
        await _generate_helpers_yaml(hass, entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _generate_helpers_yaml(hass: HomeAssistant, entry: ConfigEntry) -> None:
    data = entry.data
    prefix = data.get(CONF_PREFIX, "ventilador")
    name = data.get(CONF_NAME, prefix)
    num_speeds = data.get(CONF_NUM_SPEEDS, 6)
    has_light = data.get(CONF_HAS_LIGHT, True)
    has_temp = data.get(CONF_HAS_LIGHT_TEMPERATURE, True)
    has_intensity = data.get(CONF_HAS_LIGHT_INTENSITY, True)

    if num_speeds <= 1:
        num_speeds = 0

    broadlink_device_id = data.get(CONF_BROADLINK_DEVICE_ID, "YOUR_BROADLINK_DEVICE_ID")
    broadlink_entity_id = data.get(CONF_BROADLINK_ENTITY_ID, "")
    remote_device = data.get(CONF_REMOTE_DEVICE, prefix)

    cmd_on = data.get(CONF_COMMAND_ON, DEFAULT_COMMAND_ON)
    cmd_off = data.get(CONF_COMMAND_OFF, DEFAULT_COMMAND_OFF)
    cmd_luz = data.get(CONF_COMMAND_LUZ, DEFAULT_COMMAND_LUZ)
    cmd_luz_calida = data.get(CONF_COMMAND_LUZ_CALIDA, DEFAULT_COMMAND_LUZ_CALIDA)
    cmd_luz_fria = data.get(CONF_COMMAND_LUZ_FRIA, DEFAULT_COMMAND_LUZ_FRIA)
    cmd_int_alta = data.get(CONF_COMMAND_INTENSIDAD_ALTA, DEFAULT_COMMAND_INTENSIDAD_ALTA)
    cmd_int_baja = data.get(CONF_COMMAND_INTENSIDAD_BAJA, DEFAULT_COMMAND_INTENSIDAD_BAJA)

    velocidad_commands = {}
    for i in range(1, num_speeds + 1):
        key = f"{CONF_COMMAND_VELOCIDAD_PREFIX}_{i}"
        velocidad_commands[i] = data.get(key, f"{DEFAULT_COMMAND_VELOCIDAD_PREFIX}{i}")

    output_dir = hass.config.path("fanpy", "generated")
    os.makedirs(output_dir, exist_ok=True)

    entities_yaml = _build_entities_yaml(prefix, name, num_speeds, has_light, has_temp, has_intensity)
    scripts_yaml = _build_scripts_yaml(
        prefix, name, num_speeds, has_light, has_temp, has_intensity,
        broadlink_device_id, broadlink_entity_id, remote_device,
        cmd_on, cmd_off, cmd_luz, cmd_luz_calida, cmd_luz_fria,
        cmd_int_alta, cmd_int_baja, velocidad_commands,
    )

    entities_path = os.path.join(output_dir, "entities.yaml")
    scripts_path = os.path.join(output_dir, "scripts.yaml")

    def _write():
        with open(entities_path, "w", encoding="utf-8") as f:
            f.write(entities_yaml)
        with open(scripts_path, "w", encoding="utf-8") as f:
            f.write(scripts_yaml)

    await hass.async_add_executor_job(_write)

    _LOGGER.info("Fanpy: generated files for '%s' at %s", name, output_dir)


def _build_entities_yaml(prefix: str, name: str, num_speeds: int, has_light: bool, has_temp: bool, has_intensity: bool) -> str:
    lines = []
    lines.append("# Fanpy â€” Generated Helper Entities")
    lines.append(f"# Prefix: {prefix}")
    lines.append(f"# Name: {name}")
    lines.append("#")
    lines.append("# Copy the blocks below into your configuration.yaml")
    lines.append("#")

    lines.append("")
    lines.append("# === input_boolean ===")
    lines.append("input_boolean:")
    lines.append(f"  {prefix}_power:")
    lines.append(f'    name: "{name} Power"')
    lines.append("    icon: mdi:fan")
    lines.append(f"  {prefix}_luz:")
    lines.append(f'    name: "{name} Luz"')
    lines.append("    icon: mdi:lightbulb")
    lines.append("")

    lines.append("# === input_select ===")
    lines.append("input_select:")
    lines.append(f"  {prefix}_velocidad:")
    lines.append(f'    name: "{name} Velocidad"')
    options = [str(i) for i in range(1, num_speeds + 1)]
    lines.append(f"    options: {options}")
    lines.append("    icon: mdi:fan-speed")
    lines.append("")

    if num_speeds > 1:
        lines.append("# === input_select ===")
        lines.append("input_select:")
        lines.append(f"  {prefix}_velocidad:")
        lines.append(f'    name: "{name} Velocidad"')
        options = [str(i) for i in range(1, num_speeds + 1)]
        lines.append(f"    options: {options}")
        lines.append("    icon: mdi:fan-speed")
        lines.append("")

    lines.append("# === input_button (optional, for manual testing) ===")
    lines.append("input_button:")
    lines.append(f"  {prefix}_power_on:")
    lines.append(f'    name: "{name} Power On"')
    lines.append(f"  {prefix}_power_off:")
    lines.append(f'    name: "{name} Power Off"')
    if has_light:
        lines.append(f"  {prefix}_luz_on:")
        lines.append(f'    name: "{name} Luz On"')
        lines.append(f"  {prefix}_luz_off:")
        lines.append(f'    name: "{name} Luz Off"')
        if has_temp:
            lines.append(f"  {prefix}_luz_calida:")
            lines.append(f'    name: "{name} Luz CÃ¡lida"')
            lines.append(f"  {prefix}_luz_fria:")
            lines.append(f'    name: "{name} Luz FrÃ­a"')
        if has_intensity:
            lines.append(f"  {prefix}_intensidad_alta:")
            lines.append(f'    name: "{name} Intensidad Alta"')
            lines.append(f"  {prefix}_intensidad_baja:")
            lines.append(f'    name: "{name} Intensidad Baja"')
    if num_speeds > 1:
        for i in range(1, num_speeds + 1):
            lines.append(f"  {prefix}_velocidad_{i}:")
            lines.append(f'    name: "{name} Velocidad {i}"')
    lines.append("")

    lines.append("# === template binary_sensor (for card more-info) ===")
    lines.append("# Note: if you already have template: in your config, merge this block")
    lines.append("template:")
    lines.append("  - binary_sensor:")
    lines.append(f"      - name: \"{name} Power\"")
    lines.append(f"        state: \"{{{{ states('input_boolean.{prefix}_power') }}}}\"")
    lines.append("        icon: mdi:fan")
    lines.append(f"      - name: \"{name} Luz\"")
    lines.append(f"        state: \"{{{{ states('input_boolean.{prefix}_luz') }}}}\"")
    lines.append("        icon: mdi:lightbulb")
    lines.append("")

    return "\n".join(lines)


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
    lines.append("# Fanpy â€” Generated Scripts")
    lines.append(f"# Prefix: {prefix}")
    lines.append(f"# Name: {name}")
    lines.append(f"# Device ID: {broadlink_device_id}")
    lines.append("#")
    lines.append("# Copy into your scripts.yaml")
    lines.append("#")

    lines.append("")
    lines.append("script:")

    def _target_block():
        if broadlink_device_id and broadlink_device_id != "YOUR_BROADLINK_DEVICE_ID":
            return f"        device_id: {broadlink_device_id}"
        if broadlink_entity_id:
            return f"        entity_id: {broadlink_entity_id}"
        return "        device_id: YOUR_BROADLINK_DEVICE_ID"

    def _write_script(action_name, display_name, *args):
        lines.append(f"  {prefix}_{action_name}:")
        lines.append("    sequence:")
        lines.append("    - action: remote.send_command")
        lines.append("      metadata: {}")
        lines.append("      data:")
        lines.append("        num_repeats: 1")
        lines.append("        delay_secs: 0.4")
        lines.append("        hold_secs: 0")
        lines.append(f"        device: {remote_device}")
        if args:
            lines.append(f"        command: '{args[0]}'")
        lines.append("      target:")
        lines.append(_target_block())
        for extra in args[1:]:
            lines.append(f"    - action: {extra[0]}")
            lines.append("      metadata: {}")
            lines.append("      data: {}")
            lines.append("      target:")
            lines.append(f"        entity_id: {extra[1]}")
        lines.append(f"    alias: \"{display_name}\"")
        lines.append("    description: ''")
        lines.append("")

    _write_script("power_on", f"{name} Power ON", cmd_on,
                  ("input_boolean.turn_on", f"input_boolean.{prefix}_power"))

    _write_script("power_off", f"{name} Power OFF", cmd_off,
                  ("input_boolean.turn_off", f"input_boolean.{prefix}_power"))

    if has_light:
        _write_script("luz_on", f"{name} Luz ON", cmd_luz,
                      ("input_boolean.turn_on", f"input_boolean.{prefix}_luz"))

        _write_script("luz_off", f"{name} Luz OFF", cmd_luz,
                      ("input_boolean.turn_off", f"input_boolean.{prefix}_luz"))

        if has_temp:
            _write_script("luz_calida", f"{name} Luz CÃ¡lida", cmd_luz_calida)
            _write_script("luz_fria", f"{name} Luz FrÃ­a", cmd_luz_fria)

        if has_intensity:
            _write_script("intensidad_alta", f"{name} Intensidad Alta", cmd_int_alta)
            _write_script("intensidad_baja", f"{name} Intensidad Baja", cmd_int_baja)

    if num_speeds > 1:
        for i in range(1, num_speeds + 1):
            cmd = velocidad_commands.get(i, f"velocidad{i}")
            _write_script(f"velocidad_{i}", f"{name} Velocidad {i}", cmd,
                          ("input_select.select_option", f"input_select.{prefix}_velocidad"),
                          ("input_boolean.turn_on", f"input_boolean.{prefix}_power"))

    return "\n".join(lines)
