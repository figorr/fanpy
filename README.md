# Fanpy

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

Custom integration for Home Assistant to configure ceiling fans for use with the [Fan Custom Card](https://github.com/figorr/fan-custom-card) Lovelace card.

## Purpose

Fanpy is the **backend companion** for the Fan Custom Card. While the card provides the frontend UI, this integration provides the configuration wizard and generates all the necessary Home Assistant helpers, entities, and scripts.

## Features

- ✅ **Multi-step setup wizard** — area selection, mode choice, feature toggles, Broadlink configuration
- ✅ **Two modes**: Helpers (Broadlink RF scripts) and Direct (native `switch.*` / `light.*`)
- ✅ **Automatic entity creation**: `binary_sensor.*` for card more-info, `button.*` for manual triggers
- ✅ **YAML generation** — creates `entities.yaml` and `scripts.yaml` ready to use
- ✅ **Broadlink RF script generation** — power, light, temperature, intensity, and speed scripts
- ✅ **Multi-language support**: English, Spanish, Catalan
- ✅ **HACS compatible**

## Installation

### HACS (Recommended)

1. Open HACS.
2. Search for **Fanpy** and install it.
3. Restart Home Assistant.

### Manual

1. Download the `fanpy.zip` from the latest release.
2. Unzip and copy `custom_components/fanpy/` to your Home Assistant `custom_components` directory:
   ```
   /config/custom_components/fanpy/
   ```
3. Restart Home Assistant.

## Usage

1. After restart, go to **Settings > Devices & Services > Add Integration**.
2. Search for **Fanpy** and select it.
3. Follow the wizard steps:

   **All modes:**
   - **Step 1 — Mode**: Choose Helpers (Broadlink RF) or Direct (switch.* / light.*)
   - **Step 2 — Area**: Select the area where the fan is located

   **Direct mode:**
   - **Step 3 — Fan & Speeds**: Select the fan entity (`switch.*`) and set the number of speeds (1-10; set to 1 to hide speed buttons)
   - **Step 4 — Light**: Toggle light, color temperature, and brightness controls

   **Helpers mode:**
   - **Step 3 — Speeds**: Set the number of speeds (1-10; set to 1 to hide speed buttons)
   - **Step 4 — Light**: Toggle light, color temperature, and brightness controls
   - **Step 5 — Broadlink**: Select the Broadlink device, set the remote device name, and configure each learned RF command name
   - **Step 6 — Speed Commands**: Configure the RF command name for each speed level

4. The integration creates the entities and saves generated YAML files.

### Generated Files

After setup, check `/config/fanpy/generated/` for:
- `entities.yaml` — Ready-to-use `input_boolean`, `input_select`, `input_button`, and `template` binary_sensor definitions
- `scripts.yaml` — Complete Broadlink RF scripts for all fan actions

Copy the relevant blocks into your `configuration.yaml` and `scripts.yaml` files.

## Configuration Options

After setup, you can modify options via **Settings > Devices & Services > Fanpy > Configure**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `has_light` | boolean | `true` | Show/hide the light section |
| `has_light_temperature` | boolean | `true` (helpers) / `false` (direct) | Show/hide color temperature buttons |
| `has_light_intensity` | boolean | `true` (helpers) / `false` (direct) | Show/hide brightness buttons |

## Requirements

- Home Assistant 2025.12.5 or newer
- [Fan Custom Card](https://github.com/figorr/fan-custom-card) (for the Lovelace UI)

## Development

```bash
git clone https://github.com/figorr/fanpy.git
cd fanpy
```

## Translations

To add a new language:

1. Create `custom_components/fanpy/translations/{lang}.json` with the same keys as `en.json`.
2. Submit a PR.

## License

Apache-2.0. See [LICENSE](LICENSE).
