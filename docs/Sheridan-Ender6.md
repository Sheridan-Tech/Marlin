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
- Linear Advance included; actual compiled default is **K=0.22**, verified by first post-flash M503. Previous TinyMachines running default was K=0. For initial commissioning, temporarily use `M900 K0` (RAM only, don't save until tuned), then calibrate K with measured extrusion.
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

## Hotend identification, updated 2026-10-28
- **Owner confirms a Creality Spider V2.0 hotend.** The precise kit SKU remains inferred rather than independently read from the box.
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

## Confirmed Spider V2.0; HT-NTC100K cartridge suspected (2026-10-28)
- **User confirmation:** Creality Spider V2.0 is installed. User suspects the installed thermistor *may* be an HT-NTC100K cartridge; this is not confirmed by sensor marking, wiring history or measured resistance curve.
- Creality OEM listing for the apparent V2 hotend: product 4008030043, rated 300°C: https://mvip.creality.com/en/goods/goodsDetail/1833. A Creality Spider 2.0 installation manual calls for reusing the printer's existing thermistor and heater, and a retailer describes a supplied cartridge with an adapter for the original glass-bead thermistor. Therefore, hotend identity **does not identify the installed sensor**.
- **Source-code thermistor-table check for this exact Marlin 2.1.3-b3 checkout:**
  - `thermistor_1.h`: 100kΩ at 25°C, B4092, 4.7kΩ pull-up; existing `TEMP_SENSOR_0 1`.
  - `thermistor_11.h`: 100kΩ B3950, but a low-resolution bed-oriented table and not preferred for a high-temperature hotend.
  - `thermistor_13.h`: 100kΩ B4100, 4.7kΩ pull-up and a table to 300°C. **Important:** despite online guides identifying option 13 as B3950, this checkout's actual table is B4100.
  - `thermistor_61.h`: 100kΩ B3950 high-temperature hotend table extending to 350°C. Potential choice **only if installed cartridge is verified B3950** and thermal accuracy is checked.
  - `TEMP_SENSOR_0 1000`: supports custom R25/Beta/Steinhart-Hart settings in `Configuration_adv.h`; current example has R25=100000Ω and Beta=3950, but is inactive and not a sensor identification.
- **Do not switch to 13, 61 or 1000 solely based on an HT-NTC100K label.** Different HT-NTC100K products can share R25=100kΩ yet use distinct resistance-temperature curves. Both at-room-temperature M105 and a single 25°C resistance measurement can look correct while high-temperature readings are significantly inaccurate.
- Keep current `TEMP_SENSOR_0 1` and `HEATER_0_MAXTEMP 260` unchanged in this unvalidated candidate. With `HOTEND_OVERSHOOT 15`, the nominal highest commanded hotend target under this configuration is 245°C, **not** 260°C.
- **Non-heating identification procedure:** with the printer unplugged and cool, photograph the actual sensing element (3×15 mm metal cartridge versus glass bead/sleeve) and its leads/connectors. Record the original or replacement part number and whether original heater/thermistor were reused. If labeling is absent, disconnect the thermistor from controller power and measure its resistance at accurately measured ambient and a controlled second temperature (~60–80°C) using a suitable safe setup; a 25°C-only resistance check cannot distinguish B3950 from B4092/B4100. Do not immerse wired electronics. Never measure resistance on powered circuitry.
- **Before energizing either heater under changed firmware:** verify ambient M105 readings for both hotend and bed, independently compare elevated temperatures (with qualified instrumentation), ensure sensor and wiring remain stable under movement, and verify thermal protection, heater shutoff and PID control under close supervision. Do not increase 245°C command ceiling without verifying the installed thermistor, heater, hotend assembly, PTFE/heat-break arrangement and thermal safety.
- Sources: https://marlinfw.org/docs/appendix/thermistors.html ; https://marlinfw.org/docs/features/thermal_protection.html ; https://biqu.equipment/products/biqu-ht-ntc100k-high-temp-thermistor .

## First post-flash OctoPrint serial/M503 capture (2026-10-28)
- **Hardware installation happened before release-gate checks:** owner reports flashing the candidate mainboard firmware. This section records the owner-provided terminal output only; it is **not** physical commissioning or permission to start printing.
- **New firmware confirmed running**: M115 `Marlin 2.1.3-beta3 (Oct 27 2026 22:25:23)`, `KINEMATICS:COREXYCartesian`, one extruder. Capabilities `ARCS:1`, `RUNOUT:1`, `AUTOLEVEL:0`, `Z_PROBE:0`, `LEVELING_DATA:1`, `EMERGENCY_PARSER:1`, `THERMAL_PROTECTION:1`, `EEPROM:1`, `BABYSTEPPING:1`.
- **Ambient sensors appear plausible (unheated only):** `T:23.5–26.1°C`, `B:~22°C`, `@:0 B@:0`. This does **not** validate hotend type-1 resistance curve or heated-bed thermistor mapping at operating temperatures.
- **M503 actual running values**: `M92 X80 Y80 Z400 E140`; `M203 X400 Y400 Z10 E75`; `M201 X7000 Y7000 Z100 E75`; `M204 P3000 R1000 T5000`; `M205 B20000 X10 Y10 Z0.40 E5`; `M206 X0 Y0 Z0`; `M420 S0 Z10` (mesh OFF, no measured grid shown); `M301 P18.69 I1.34 D65`; `M304 P690.34 I111.47 D1068.83`; `M413 S0`; `M593 X/Y F40 D0.15`; **`M900 K0.22`**; **`M603 L830 U830`**; `M412 S1`.
- **Corrections to earlier assumptions:** actual Marlin source default `ADVANCE_K 0.22` is live, not K0 as incorrectly stated in the earlier motion-plan prose; old live firmware was K0. Likewise `M603 L830 U830` differs from old live `L75 U75`; these are full Bowden-length filament-change settings, not routine retracts, and require physical path measurement before using M600/M701/M702.
- **Mesh state:** `M420 S0` means leveling is disabled, not proof mesh data exists. No mesh point values appear in the provided M503 output. Run nonmoving `M420 V` / `G29 S0` to inspect; verify all endstops with `M119` before any G28; rebuild hot 5×5 manual mesh safely, then save. A valid mesh is required before `M420 S1`.
- **Acceleration commissioning:** initial 3000 print/5000 travel defaults are untested; temporary, unsaved `M204 P1000 T1500` recommended as a conservative starting point after confirming mechanical/endstop safety. `M201 E75` was copied from old firmware and is a possible extrusion/acceleration limiter for later measured speed tuning.
- **Serial stability observation:** OctoPrint `SerialException: device reports readiness to read but returned no data` caused one disconnect; port `/dev/ttyUSB0` reconnected at **250000** after an unsuccessful 115200 attempt. It could be power, USB cable, printer reset or port contention; cause unconfirmed. Investigate `octoprint.log` and Pi kernel USB events if repeated, before any long host-streamed print. `Recv: wait` and `Not SD printing` alone are not errors; `M21` reports no printer SD card.
- **Screen**: owner reports it still shows Insanity branding after mainboard flash. This may simply reflect independent TinyMachines DWIN screen resources. Do **not** flash new DWIN assets unless functionality fails and a matched screen/recovery resource is confirmed.
- **No hardware actions performed by assistant:** no heater, motor, homing, filament-change, EEPROM-save or firmware flashing command issued. No new firmware source settings modified in this commit.

## Post-flash DWIN control failure diagnosis (2026-10-28)
- Owner reports DWIN display powers on and reads plausible ambient temperatures, but cannot control the machine. Independent OctoPrint M115/M503 confirms new Marlin 2.1.3-beta3 running. **Do not home/heat using the screen** until functionality and endstops are verified.
- **Correction to earlier source audit:** Comparing `src/lcd/extui/dgus/origin/DGUSDisplayDef.h` across branches was not a valid comparison of the **active** TinyMachines driver to the **active** new Marlin driver. The old Ender-6_DWIN profile enables `EXTENSIBLE_UI` with `FORCE10SPRODISPLAY`, using `src/lcd/extui/Creality/Creality_DWIN.cpp/.h`. The new upstream `DGUS_LCD_UI IA_CREALITY` enables `src/lcd/extui/ia_creality/ia_creality_rts.cpp/.h`, not the generic `dgus/origin` implementation.
- The **actual active** old/new DWIN interface headers have **98 shared numeric definitions and 95 identical numeric values**, including all relevant nozzle/bed temperatures and feedrate: `NozzleTemp 0x1036`, `Bedtemp 0x103C`, `NozzlePreheat 0x1034`, `BedPreheat 0x103A`, `FeedrateDisplay 0x1006`. The only three differences among shared numeric definitions are T2 dual-extruder offsets, inapplicable to this single-extruder Ender 6. Both drivers use DGUS frames `0x5A 0xA5`, 115200 baud, `DWIN_SERIAL LCD_SERIAL`, and handle incoming `0x83` variable updates. Thus **a wholesale screen resource/protocol mismatch is not proven**; the earlier generic driver comparison overstated the risk.
- **Next safe discriminator:** Without homing, heating or printing, see whether DWIN local menus navigate. If the panel offers a Speed/Feedrate control, set 100% -> 95% with printer idle. Query from OctoPrint using parameterless `M220`; a reported 95% indicates DWIN->mainboard input works. Restore via `M220 S100` (runtime only). If it remains 100% or touches fail, inspect the panel's touch calibration, screen generation/resources, serial TX/RX wiring, and current IA_CREALITY driver's receive dispatch before choosing a replacement resource package.
- Missing SD card explains the previous `M21: No SD card` and possibly an SD status popup, not a failed motherboard flash. Source code and flash binary remain unchanged.

## 2026-10-28 IA_CREALITY touchscreen axis jog repair (new candidate)
- **Reproduced behavior from owner's report:** mainboard Marlin 2.1.3-beta3 operational via OctoPrint; DWIN main UI receives position and temperature data; touchscreen Home reportedly works, but touchscreen X/Y/Z coordinate entries did not move and repeated `M114` remained X260 Y260 Z10 after testing.
- **Root cause found in active driver, NOT generic DGUS ORIGIN code:** `Marlin/src/lcd/extui/ia_creality/ia_creality_rts.cpp` `RTS::handleData()`, `case XYZEaxis`, contained `} break;` outside the `else if (recdat.addr == AutoZero)` block. That unconditional `break` exited the `switch` before `targetPos` was calculated and `setAxisPosition_mm(targetPos, axis)` could run. AutoZero/Home was handled before the break, explaining why Home worked while position entry failed. Compared against the actual legacy TinyMachines screen implementation `Marlin/src/lcd/extui/Creality/Creality_DWIN.cpp`, whose `break` is inside the AutoZero branch and whose X/Y/Z target handler is reachable. The `origin/DGUSScreenHandler.cpp` handler reviewed earlier is **not** the active `IA_CREALITY` implementation.
- **Fix:** move `break` inside the AutoZero branch and keep all movement targets unchanged; X/Y/Z target positions now reach the existing limit-clamp and `setAxisPosition_mm` code. Added fail-closed source regression assertion in `test/sheridan_ender6_config.py` for this class of unreachable handler. No hotend sensor, heaters, acceleration, shaping, extruder or display-side resources were changed.
- **Release status:** source fix is a new experimental mainboard candidate, not a hardware-validated release. Complete local static checks and PlatformIO compile, then GitHub CI; preserve old binary SHA-256 `CF3203BFE1E7852581FD1A04843933554DDE7A899B6B85D45FA0595A11A7C52A` plus legacy recovery pair. On installation, confirm M115 build identifier and test one **small inward move** after endstop tests and safe homing, followed by `M400` and `M114`. Do not assume touchscreen firmware needs flashing, nor print until safe commissioning gates pass.

## 2026-10-28 post-flash DWIN touch jog fix owner confirmation and calibration checkpoint
- **Owner confirms touchscreen movement works after flashing the corrected mainboard firmware** from `1d51f60`. This closes the observed "Home works but X/Y/Z positioning does nothing" functional regression at the owner-reported level; there is no reason to replace the Insanity/TinyMachines display assets solely for the resolved jog issue.
- Dedicated [GitHub Actions run 40647489485](https://github.com/Sheridan-Tech/Marlin/actions/runs/40647489485) for source revision `1d51f60fe7be6fdfbbd96862647e63cd7cdd1356` completed successfully. Local binary: `../output/firmware-e6-ia-jogfix-v2.bin`, SHA-256 `3AED11465E0304680A4C60C04BF7FEC27902D71BE7808DB229C799E95CB9FC16`. The owner's exact flashed binary hash and final post-flash M115 build timestamp have not been independently read back.
- **Do not classify the printer as fully calibrated:** last recorded `M503` showed `M420 S0 Z10` (bed mesh disabled), `M900 K0.22` (untuned), `M603 L830 U830` (unverified long Bowden load/unload), `M204 P3000 T5000` (untested accelerations), `M593 X/Y F40 D0.15` (uncalibrated shaper), and old PID/steps copied across. Prior thermistor uncertainty (possible HT-NTC100K vs previous sensor) remains unresolved.
- **Commissioning sequence:** read-only `M420 V` and `G29 S0` first; confirm physical temperature-sensor identity and thermal measurements before heated PID tuning; tram bed and rebuild hot 5×5 manual mesh `G29 S1`/repeated `G29 S2` then `M500`, enable after `G28` using `M420 S1`; verify extrusion steps, calibrate flow and `M900`, then tune resonance/speed and slicer settings. Do not permanently save unverified settings.

## 2026-10-28 mesh-empty and OctoPrint timeout diagnostic (owner log)
- Non-moving commands succeeded: `M420 V` returned `Invalid mesh.` and `Bed Leveling OFF`; `G29 S0` returned `Mesh Bed Leveling has no data.`, followed by `ok`. This definitively shows no usable stored/manual 5x5 mesh in RAM; rebuilding is required. The `G29 S0` handler is read-only and was **already acknowledged** before the subsequent OctoPrint disconnect.
- OctoPrint subsequently logged three consecutive communication timeouts and disconnected, then automatically reconnected to `/dev/ttyUSB0` at 250000. This does not establish an MCU reset or a direct `G29` firmware fault. **Treat serial stability as a prerequisite to running `G29 S1`**, because a partially completed manual mesh relaxes Z software endstops and requires carefully finishing the sequence or restarting the printer. Get `octoprint.log`/`serial.log` and Pi kernel USB events around the failure; check power, USB cable and port contention before increasing timeouts.
- On reconnect, OctoPrint sent `M500`, receiving `Settings Stored (734 bytes; crc 29432)`. The sender/trigger for `M500` is not confirmed from this excerpt. The command saved current EEPROM settings, **not** a valid mesh. Later `M503` showed hotend PID `M301 P18.48 I1.32 D64.69` (earlier `P18.69 I1.34 D65.00`), runout `M412 S0` (earlier `S1`), mesh still OFF, `M204 P3000 R1000 T5000`, shaping 40Hz, and `M900 K0.22`. Preserve these observed deltas and do not issue blanket `M502`/`M500` before understanding their source.
- **Build identification caveat discovered by byte inspection on ZLT:** the preserved old candidate SHA256 `CF3203BFE1E7852581FD1A04843933554DDE7A899B6B85D45FA0595A11A7C52A` and jog-fix candidate SHA256 `3AED11465E0304680A4C60C04BF7FEC27902D71BE7808DB229C799E95CB9FC16` **both embed** `Oct 27 2026 22:25:23`. Thus `M115` showing this exact timestamp **cannot** distinguish the installed candidate. Owner reported that touchscreen jogs work after applying the patch, which is encouraging functional evidence but not a byte-level image readback.
- Next gates: stabilize OctoPrint serial connection, independently validate actual hotend/bed thermistor readings at temperature before heating, inspect physical filament-runout switch if used, then run manual tramming and full 25-point `G29 S1/S2` with deliberate completion, verify with `G29 S0` and `M420 V`, and only then save confirmed settings and add `M420 S1` after `G28` in slicer start G-code.
