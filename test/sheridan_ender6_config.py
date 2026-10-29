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
assert re.search(r"(?m)^#define TEMP_SENSOR_0 1(?:\s|$)",cfg), "Unreviewed hotend thermistor change: identity still unverified"
assert re.search(r"(?m)^#define HEATER_0_MAXTEMP 260\s*$",cfg), "Temperature limit changed"
assert re.search(r"(?m)^#define HOTEND_OVERSHOOT 15(?:\s|$)",cfg), "Hotend overshoot guard changed"
assert re.search(r"(?m)^#define DEFAULT_MAX_ACCELERATION\s+\{\s*7000,\s*7000,\s*100,\s*75\s*\}",cfg)
assert re.search(r"(?m)^#define DEFAULT_ACCELERATION\s+2000\b",cfg), "Approved default print acceleration changed"
assert re.search(r"(?m)^#define DEFAULT_TRAVEL_ACCELERATION\s+3000\b",cfg), "Approved default travel acceleration changed"
assert re.search(r"(?m)^#define DEFAULT_MAX_FEEDRATE\s+\{\s*500,\s*500,\s*10,\s*75\s*\}",cfg), "Approved XY speed ceiling changed"
assert re.search(r"(?m)^\s*#define DEFAULT_XJERK\s+10\.0\b",cfg) and re.search(r"(?m)^\s*#define DEFAULT_YJERK\s+10\.0\b",cfg), "Rejected XY jerk edit must not be applied"
assert re.search(r"(?m)^#define BAUDRATE 250000",cfg)
assert re.search(r"(?m)^\s*#define GRID_MAX_POINTS_X 5",cfg)
assert re.search(r"(?m)^#define DEFAULT_AXIS_STEPS_PER_UNIT\s+\{\s*80,\s*80,\s*400,\s*142\.86\s*\}",cfg), "Calibrated dual-drive E steps not configured"
assert re.search(r"(?m)^#define DEFAULT_MAX_ACCELERATION\s+\{\s*7000,\s*7000,\s*100,\s*75\s*\}",cfg), "E-axis acceleration remains untested: do not increase it yet"
assert re.search(r"(?m)^#define NOZZLE_TO_PROBE_OFFSET\s+\{\s*-20\.7,\s*-7,\s*-2\.5\s*\}",cfg), "Unapproved unused probe offset change"
assert re.search(r"(?m)^\s*#define FIL_RUNOUT_ENABLED_DEFAULT\s+true\b",cfg), "Unapproved runout default change"
assert re.search(r"(?m)^\s*#define DEFAULT_KP\s+18\.69\b",cfg), "Hotend PID pending physical tune"
assert re.search(r"(?m)^\s*#define DEFAULT_BED_KP\s+690\.34\b",cfg), "Bed PID pending physical tune"
# Geometry-based provisional Bowden change: no change to unverified thermistors or to runout behavior.
# User measured 965.2 mm from drive gears to hotend entrance, +55.0 mm to nozzle tip.
def define_num(text, key):
    m=re.search(r"(?m)^\s*#define\s+"+re.escape(key)+r"\s+([0-9]+(?:\.[0-9]+)?)\b", text)
    assert m, f"Missing numeric {key}"
    return float(m.group(1))
path_mm=965.2 + 55.0
slow=define_num(adv,"FILAMENT_CHANGE_SLOW_LOAD_LENGTH")
fast=define_num(adv,"FILAMENT_CHANGE_FAST_LOAD_LENGTH")
purge=define_num(adv,"ADVANCED_PAUSE_PURGE_LENGTH")
unload=define_num(adv,"FILAMENT_CHANGE_UNLOAD_LENGTH")
maxmove=define_num(cfg,"EXTRUDE_MAXLENGTH")
assert (slow,fast,purge,unload,maxmove)==(20.0,940.0,80.0,1050.0,1100.0), "Altered provisional Bowden settings"
assert (965.2 - 15.0) <= slow + fast <= 965.2, "Fast loading must stop before hotend entrance"
assert 10.0 <= slow + fast + purge - path_mm <= 35.0, "Purge after loading must reach nozzle with modest surplus"
assert 15.0 <= unload - path_mm <= 40.0, "Unloading requires measured path plus clearance"
assert unload <= maxmove <= 1150.0, "Retain bounded single-move extrusion protection"
assert re.search(r"(?m)^\s*#define SHAPING_FREQ_X\s+0\.0\b",adv) and re.search(r"(?m)^\s*#define SHAPING_FREQ_Y\s+0\.0\b",adv), "Uncalibrated shaping must default off"
assert re.search(r"(?m)^\s*#define SHAPING_MIN_FREQ\s+20\.0\b",adv), "F0 shaping defaults require a positive buffer floor"
assert re.search(r"(?m)^\s*#define ADVANCE_K\s+0\.0\b",adv), "Uncalibrated Linear Advance must default off"
assert re.search(r"(?m)^\s*#define ADVANCE_K\s+\{\s*0\.0\s*\}",adv), "Distinct extruder Linear Advance must default off"
assert re.search(r"(?m)^#define TEMP_SENSOR_BED 5\b",cfg), "Unexpected bed thermistor table"

# Regression: upstream IA_CREALITY formerly had an unconditional break immediately
# before position-entry code, making X/Y/Z display commands unreachable while Home worked.
rts=(base/"Marlin"/"src"/"lcd"/"extui"/"ia_creality"/"ia_creality_rts.cpp").read_text(encoding="utf-8")
assert "case XYZEaxis: {" in rts and "case Filament: {" in rts, "IA_CREALITY position handler missing"
jog=rts.split("case XYZEaxis: {",1)[1].split("case Filament: {",1)[0]
assert all(key in jog for key in ("DisplayXaxis","DisplayYaxis","DisplayZaxis","AutoZero","setAxisPosition_mm(targetPos, axis)")), "IA_CREALITY touch motion handlers missing"
assert not re.search(r"}\s*break;\s*\n\s*(?://[^\n]*\n\s*)*float targetPos",jog), "Unconditional break prevents DWIN X/Y/Z target movement"
assert re.search(r"else if \(recdat\.addr == AutoZero\) \{.*?\n\s*break;[^\n]*\n\s*\}",jog,re.S), "Autohome must retain its own early exit"

print("Ender 6 static profile assertions: PASS (physical hardware still unverified)")
