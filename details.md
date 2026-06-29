# e-ink-timer details

Simple MicroPython app for a Raspberry Pi Pico + Inky pack that acts as a clock and a timer.

Files:
- `main.py` — main application (state machine, buttons, timer/stopwatch)
- `display.py` — small FrameBuffer-based drawing helper (adapt `show()` to your Inky driver)

Current behavior:
- Default view is a clock with a radial dial on the left and remaining workday time on the right.
- `A` enters the timer menu.
- `B` starts the stopwatch.
- `C` on the main clock view enters a splash mode with `cyberderds timer`.
- In splash mode, `A` goes to the timer menu, `B` starts the stopwatch, and `C` returns to the clock.
- Timer states include 5-minute, 25-minute, and custom timer entry.
- On timer completion the display shows `timer complete!`.

Notes:
- This code draws into a FrameBuffer and expects a compatible Inky MicroPython driver. You may need to adapt `display.show()` to call your specific driver's buffer/blit method.
- Update the button GPIO pins in `main.py` (`A_PIN`, `B_PIN`, `C_PIN`) to match your wiring.
- The Pico does not keep wall-clock time across reboots unless an RTC is present and set; `time.localtime()` will reflect whatever the device RTC has.

Driver notes (Pico Inky Pack — 296x128 mono):
- `display.show()` now attempts to auto-detect Pimoroni's `pico_inky` driver and other common Inky modules. If you installed the Pimoroni Pico Inky UF2 and the example drivers from the `pimoroni-pico` repo, the code should find `pico_inky` automatically.
- If the display remains blank, adapt the call signatures in `display.show()` to match your installed driver. Typical steps to get the Pimoroni Pico Inky working:
  1. Install the Pimoroni Pico UF2 (see https://github.com/pimoroni/pimoroni-pico/releases/latest/) onto the Pico.
  2. Use the `pico_inky` examples in the `pimoroni-pico` repo to ensure the driver is available on your device.
  3. If needed, copy any driver `.py` files to the Pico's filesystem so `import pico_inky` works from `main.py`.

Menu map:
- See `menu-map.md` for the current state flow diagram.

Quick troubleshooting:
- Ensure `WIDTH`/`HEIGHT` in `main.py` match your Inky pack (296x128). Example: set `WIDTH = 296` and `HEIGHT = 128`.
- Make sure your display buffer orientation matches the driver's expectations. If text appears inverted or garbled, try swapping bit-order or using a different FrameBuffer format (e.g., `framebuf.MONO_VLSB` vs `MONO_HLSB`).
- If you want, tell me the exact `pimoroni-pico` example filename you used (from their repo) and I will adapt `display.show()` to that API.