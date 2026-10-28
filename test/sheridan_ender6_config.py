#!/usr/bin/env python3
"""Fail-closed static assertions for the Sheridan Ender 6 firmware profile."""
from pathlib import Path
import re
base=Path(__file__).resolve().parents[1]
cfg=(base/"Marlin"/"Configuration.h").read_text(encoding="utf-8")
adv=(base/"Marlin"/"Configuration_adv.h").read_text(encoding="utf-8")
def active(name):
    pattern=r"(?m)^\s*#define\s+"+re.escape(name)+r"(?:\s+|$)"
    return bool(re.search(pattern,cfg+"\n"+adv))
for token in ["COREXY","MESH_BED_LEVELING","LCD_BED_TRAMMING",
              "ARC_SUPPORT","EMERGENCY_PARSER","HOST_ACTION_COMMANDS",
              "INPUT_SHAPING_X","INPUT_SHAPING_Y",
              "LIN_ADVANCE","THERMAL_PROTECTION_HOTENDS","THERMAL_PROTECTION_BED"]:
    assert active(token), f"Required firmware option disabled: {token}"
for token in ["E6_USE_BLTOUCH","USE_PROBE_FOR_Z_HOMING",
              "Z_MIN_PROBE_USES_Z_MIN_ENDSTOP_PIN","AUTO_BED_LEVELING_BILINEAR",
              "AUTO_BED_LEVELING_UBL"]:
    assert not active(token), f"Unsafe probe setting for this no-probe machine: {token}"
assert re.search(r"(?m)^#define DGUS_LCD_UI IA_CREALITY\s*$",cfg), "Wrong DWIN UI"
assert re.search(r"(?m)^#define MOTHERBOARD BOARD_CREALITY_V431\s*$",cfg) or re.search(
    r"(?m)^\s+#define MOTHERBOARD BOARD_CREALITY_V431\s*$",cfg), "Wrong controller"
assert re.search(r"(?m)^#define HEATER_0_MAXTEMP 260\s*$",cfg), "Temperature limit changed"
assert re.search(r"(?m)^#define DEFAULT_MAX_ACCELERATION\s+\{\s*7000,\s*7000,\s*100,\s*75\s*\}",cfg)
assert re.search(r"(?m)^#define DEFAULT_ACCELERATION\s+3000",cfg)
assert re.search(r"(?m)^#define DEFAULT_TRAVEL_ACCELERATION\s+5000",cfg)
assert re.search(r"(?m)^#define BAUDRATE 250000",cfg)
assert re.search(r"(?m)^\s*#define GRID_MAX_POINTS_X 5",cfg)
assert re.search(r"(?m)^#define DEFAULT_AXIS_STEPS_PER_UNIT\s+\{\s*80,\s*80,\s*400,\s*140\s*\}",cfg)
assert re.search(r"(?m)^#define TEMP_SENSOR_BED 5\b",cfg), "Unexpected bed thermistor table"
print("Ender 6 static profile assertions: PASS (physical hardware still unverified)")
