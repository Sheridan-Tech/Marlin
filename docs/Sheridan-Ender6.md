# Sheridan Ender 6 — Marlin 2.1.3-b3, DWIN, OctoPrint and arcs

## Sources and rollback
- Exact upstream Marlin source: MarlinFirmware/Marlin tag 2.1.3-b3 (58a4358).
- Exact upstream Ender 6 example: MarlinFirmware/Configurations tag 2.1.3-b3.
- Legacy known-good source: Sheridan-Tech/Marlin Ender-6_DWIN, commit 23b0154. Keep unchanged.
- This is an experimental release candidate, NOT flash-ready until hardware and DWIN screens are validated.
- Legacy screen resources are CombinedLandscapeDwin_TM3D_V8.7z, but upstream IA_CREALITY references V7 assets. DO NOT flash a mismatched resource package without proving compatibility.
- Restore the exact known-good motherboard+display pair on failed display testing.

## Confirmed and provisional hardware
- Ender 6 CoreXY, 260 x 260 x 400 mm.
- Original Creality V4.3.1 board, assumed STM32F103RE: confirm actual package marking.
- Serial touchscreen using IA_CREALITY on UART3 at 115200; OctoPi on board USB/UART1 at 115200.
- Physical X/Y/Z endstops; NO probe. No BLTouch/CR Touch features.
- Creality CR Spider hotend: revision and installed thermistor type unknown. Temporary MAXTEMP 260 C, type-1 thermistor from official example; not approved for high temperature before thermistor verification.
- Insulated heated bed, PEI plate, metal extruder, upgraded Bowden tube.
- Provisional E-steps = 95 as in prior stock-like setup. Verify extruder gear ratio and recalibrate.
- Official example filament-runout sensor enabled: verify that sensor is fitted, connected, and polarity correct.

## Motion and speed controls
- XY firmware velocity limit: 400 mm/s; this is a ceiling, NOT a measured printing capability.
- XY maximum acceleration: 7000 mm/s2 (matches legacy high Ender-6 limit).
- Default print acceleration 3000 mm/s2; travel 5000 mm/s2, pending ringing/skip tests.
- Classic jerk 10 mm/s from official example.
- Linear Advance included, default K=0; tune M900 K after extrusion calibration.
- Input shaping is NOT enabled until resonance is measured (no guessed frequency).
- Example extrusion volume: 0.45mm x 0.2mm x 200mm/s = 18mm3/s. Verify real Spider/nozzle volumetric-flow and cooling before commanding high print speeds.
- Slicer speed and acceleration commands must be reviewed: increasing firmware limits alone will not increase print speed.
- Keep acceleration lower when print artifacts or skipped steps appear.

## OctoPrint / Arc Welder
- ARC_SUPPORT enabled in the upstream Ender-6 example, supporting G2/G3 from Arc Welder.
- HOST_ACTION_COMMANDS, EMERGENCY_PARSER, SERIAL_OVERRUN_PROTECTION enabled.
- Do not run duplicate arc-conversion processes in both slicer and OctoPrint.
- Power-loss recovery cannot resume a host-streamed OctoPrint job reliably.
- Use M115 to confirm arc feature and check OctoPrint terminal for serial errors.

## Manual bed leveling
- No probe: disable USE_PROBE_FOR_Z_HOMING, use mechanical Z-min endstop.
- Manual mesh leveling is enabled in a 3x3 grid; the stock DWIN may not provide a dedicated mesh GUI.
- After endstop polarity confirmed by M119 and after safe homing: G28, G29 S1, manual feeler-gauge adjustment, G29 S2 at each next point, M500 save, M420 V inspect.
- A valid mesh should be enabled after homing in slicer start G-code via M420 S1 after G28.
- Measure hot, verify physically trammed bed, calibrate first-layer Z.

## Commissioning and release gates
1. Export current EEPROM M503, slicer profiles, original controller binary if available, and DWIN asset archive. Source in Git is not proof of flash contents.
2. Confirm the MCU package, hotend thermistor/heater, original DWIN screen generation and resource compatibility.
3. Build and check firmware size, warnings, and target environment.
4. Before G28, manually trigger each X/Y/Z switch while querying M119. Check hotend and bed room-temperature readings, fans, heating behavior and thermal protection.
5. Test low-distance moves, CoreXY directions, Z home, DWIN touch controls, OctoPrint communication, G2/G3, manual mesh, pause/resume, runout.
6. PID tune bed (now insulated) and hotend; E-step and flow tune, then perform first-layer, ringing and volumetric-flow benchmarks.
7. Keep the old firmware until all controls and safety behaviors pass. Do not merge to legacy default branch solely on a successful compile.

## Local build
Run: pio run -e STM32F103RE_creality
Configuration: Marlin/Configuration.h and Marlin/Configuration_adv.h
