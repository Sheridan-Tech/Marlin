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
- Serial touchscreen using IA_CREALITY on UART3 at 115200; OctoPi on board USB/UART1 at 250000 (confirmed handshake from M503 session).
- Physical X/Y/Z endstops; NO probe. No BLTouch/CR Touch features.
- Creality CR Spider hotend: revision and installed thermistor type unknown. Temporary MAXTEMP 260 C, type-1 thermistor from official example; not approved for high temperature before thermistor verification.
- Insulated heated bed, PEI plate, metal extruder, upgraded Bowden tube.
- E-steps = 140 (running M503 and legacy Ender 6 default match). Recalibrate actual extrusion before speed testing.
- Official example filament-runout sensor enabled (running M591 S1 D10 P1); verify sensor electrical polarity/behavior.

## Motion and speed controls
- XY firmware velocity limit: 400 mm/s; this is a ceiling, NOT a measured printing capability.
- XY maximum acceleration: 7000 mm/s2 (matches running M503); extruder acceleration ceiling 75 mm/s2 (also matches running M503).
- Default print acceleration 3000 mm/s2; travel 5000 mm/s2, pending ringing/skip tests.
- Classic jerk 10 mm/s from official example; running M503 had 20 mm/s, but we deliberately begin more conservatively.
- Linear Advance included, default K=0 matching M503; tune M900 K after extrusion calibration.
- Input shaping is enabled on X and Y at F40.00 Hz / D0.15, preserving the LIVE M503 baseline; these are NOT proven resonance measurements. Benchmark and tune before increasing acceleration.
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
- Manual mesh leveling is enabled in a 5x5 grid, matching running M503. The old grid has only one nonzero point (0,0:0.2mm); do not assume it is calibrated and DO NOT import old EEPROM directly into a new Marlin major build.
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

## Captured running configuration (OctoPrint M503, 2026-10-28)
- Current controller firmware advertises DW7.4.7 TM3D E6SMDNN, built 2026-06-03; live printer reports Z_PROBE:0, AUTOLEVEL:0, ARCS:1, RUNOUT:1.
- Serial autoconnect initially attempted 115200 and connected at 250000.
- M92 X80 Y80 Z400 E140. M203 X750 Y750 Z10 E75. M201 X7000 Y7000 Z100 E75.
- M204 P2000 R1000 T300; **travel acceleration 300 is unusually slow** and the main initial opportunity to reduce travel time. This new build starts at P3000 T5000; test cautiously and reduce via M204 before using if motion is not yet proven.
- M205 B20000 X20 Y20 Z0.30 E5. New build intentionally starts at classic XY jerk 10, not 20.
- Mesh active, fade 10, 5x5 grid; 24 zeros and one 0.2mm offset. Recalibrate before first layer.
- M301 P18.69 I1.34 D65.00; M304 P690.34 I111.47 D1068.83. New compiled PID defaults follow live data but should still be retuned.
- M593 X F40 D0.15, M593 Y F40 D0.15. New compiled shaping defaults carry them forward as an unvalidated tuning baseline.
- M900 K0, M591 S1 D10 P1, M413 S0, M603 L75 U75.
- Legacy Git snapshot enabled ABL_BLTOUCH but the printer explicitly reports no Z probe. Live snapshot takes precedence for commissioning.
- Firmware info and M503 do NOT identify the physical Creality Spider part number, revision, thermistor actually installed, or DWIN display hardware generation; read packaging sticker and verify installed sensor.


## How to identify installed Spider kit from retail box
Creality manufacturer product numbers (check the barcode label on the physical box, not firmware source):
- 4001030091 — Spider High-temperature and High-speed Hotend (original series): https://mvip.creality.com/en/goods/goodsDetail/1195
- 4008030043 — Spider High Temperature Hotend (often described as V2): https://mvip.creality.com/en/goods/goodsDetail/1833
- 4008030044 — Spider High Temperature and High Flow Hotend Pro (commonly V3): https://mvip.creality.com/en/goods/goodsDetail/1847
- 4008030047 — Spider Speedy Ceramic Hotend: https://mvip.creality.com/en/goods/goodsDetail/1944
The exact heater and thermistor physically installed may differ from what originally shipped in the kit, so a box SKU alone does not establish TEMP_SENSOR_0 compatibility.

## Legacy bed thermistor mapping
- Legacy `Ender-6_DWIN/Marlin/Configuration.h` defaults to `BedDC` with `TEMP_SENSOR_BED 5` and `TEMP_SENSOR_0 1`; the generic upstream Ender 6 example used `TEMP_SENSOR_BED 1`. This draft restores the legacy bed table 5 as a source-informed provisional choice. Because the live M503 does NOT identify the installed bed sensor, compare actual bed temperature against an independent measurement and verify heater behavior before accepting it.

## Marlin 2.1.3-b3 shaping compile warning
- Marlin emits: `#warning Input Shaping for CORE / MARKFORGED kinematic axes is still experimental.` The feature is deliberately enabled to preserve running M503 X/Y 40 Hz, D0.15 baseline. It is not proof those settings improve vibration or that this implementation matches the legacy vendor code. Do not validate high-speed acceleration from this configuration alone; perform print comparisons and observe for missed steps / oscillation.

## Probable hotend identification, 2026-10-28
- Owner reports likely **Creality Spider V2.0**, not yet independently verified by box/part number.
- Likely matching Creality OEM item: **4008030043**, sold as "Spider High Temperature Hotend"; official listing describes a **300 C** hotend. Official product: https://mvip.creality.com/en/goods/goodsDetail/1833
- The OEM hardware rating does NOT identify the installed thermistor curve or heater. The Spider may have received the original Ender 6 sensor/heater during installation or kit-supplied replacements. Confirm which were installed.
- **Do not change** TEMP_SENSOR_0=1 or HEATER_0_MAXTEMP=260 based on a provisional identification. Thermistor table 1 is 100k EPCOS-style, used in the last working TinyMachines source, but accuracy at operating temperature is unverified.
- To authorize a temperature capability change, record packaging SKU, installed sensor/heater details, independent temperature validation, and thermal-safety tests first. Higher-temperature printing is not required to benchmark CoreXY acceleration.

## 2026-10-28 archival rollback and DGUS protocol review
- **Local verification:** ZLT `Ender6-Marlin-213/source` checkout is clean at `fd013a5`. The `f5419e5` M503-aligned experimental binary in `../output/Ender6-Marlin-213b3-DWIN-Arc-M503-aligned-UNVALIDATED.bin` has SHA-256 `CF3203BFE1E7852581FD1A04843933554DDE7A899B6B85D45FA0595A11A7C52A`.
- **CI evidence:** [GitHub Actions run 40639079414](https://github.com/Sheridan-Tech/Marlin/actions/runs/40639079414) passed static profile assertions, STM32F103RE compilation and unvalidated artifact upload at `fd013a5`. No hardware was exercised.
- **Rollback archive now saved on ZLT:** `../rollback/firmware_Ender6_DW7.4.7.bin.zip`, source `Ender-6_DWIN` commit `23b0154`, Git blob `0cec55f42f37f8ee097b51b5354e2975b11cd7f0`. The archive was verified by `git hash-object`; extracted non-BLT firmware is 158796 bytes, SHA-256 `D098A9C560D29240DA8462FBD25D5EB563D7BB025522BF7C1976995B22B1F537`.
- **DWIN rollback archive saved:** `../rollback/CombinedLandscapeDwin_TM3D_V8.7z`, same source commit, Git blob `1f345648373ca305e9309185ffd3a4b7fa6d7ba9` (verified). Full local manifest: `../rollback/README.md`. These archives are verified against **repository contents only**; they are not a flash dump of the currently installed MCU or DWIN screen.
- **Static DGUS screen protocol comparison:** `Marlin/src/lcd/extui/dgus/origin/DGUSDisplayDef.h` on `Ender-6_DWIN` vs this branch has 141 matching VP names at identical numeric addresses; `VP_MOTOR_LOCK_UNLOK` was renamed `VP_MOTOR_LOCK_UNLOCK`, retaining address `0x2130`. This is promising protocol continuity, **not** evidence that all TinyMachines V8 screen assets, pages, buttons or host-side behavior work with new firmware. The current upstream config references V7 resources; leave the physical screen untouched pending validation.
- **Flash gate unchanged:** verify actual MCU marking (RE vs RC), original screen model/resource generation, Spider kit SKU and installed thermistor/heater, and bed thermistor before loading firmware. Record full running M115/M503 and slicer profiles, test all endstops and heating safely, and retain a proven recoverable motherboard/display pairing. Do not treat the legacy archive as a guaranteed exact restoration image until hardware testing confirms it.
