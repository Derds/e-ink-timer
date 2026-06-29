# e-ink-timer

Simple MicroPython app for a Raspberry Pi Pico + Inky pack that acts as a clock and a timer.

Files:
- `main.py` — main application (state machine, buttons, timer/stopwatch)
- `display.py` — small FrameBuffer-based drawing helper (adapt `show()` to your Inky driver)

Notes:
- This code draws into a FrameBuffer and expects a compatible Inky MicroPython driver. You may need to adapt `display.show()` to call your specific driver's buffer/blit method.
- Update the button GPIO pins in `main.py` (`A_PIN`, `B_PIN`, `C_PIN`) to match your wiring.
- The Pico does not keep wall-clock time across reboots unless an RTC is present and set; `time.localtime()` will reflect whatever the device RTC has.

If you want, I can adapt `display.show()` to a specific Inky Pack MicroPython driver — tell me which driver you have.

Driver notes (Pico Inky Pack — 296x128 mono):
- `display.show()` now attempts to auto-detect Pimoroni's `pico_inky` driver and other common Inky modules. If you installed the Pimoroni Pico Inky UF2 and the example drivers from the `pimoroni-pico` repo, the code should find `pico_inky` automatically.
- If the display remains blank, adapt the call signatures in `display.show()` to match your installed driver. Typical steps to get the Pimoroni Pico Inky working:
  1. Install the Pimoroni Pico UF2 (see https://github.com/pimoroni/pimoroni-pico/releases/latest/) onto the Pico.
  2. Use the `pico_inky` examples in the `pimoroni-pico` repo to ensure the driver is available on your device.
  3. If needed, copy any driver `.py` files to the Pico's filesystem so `import pico_inky` works from `main.py`.

Quick troubleshooting:
- Ensure `WIDTH`/`HEIGHT` in `main.py` match your Inky pack (296x128). Example: set `WIDTH = 296` and `HEIGHT = 128`.
- Make sure your display buffer orientation matches the driver's expectations. If text appears inverted or garbled, try swapping bit-order or using a different FrameBuffer format (e.g., `framebuf.MONO_VLSB` vs `MONO_HLSB`).
- If you want, tell me the exact `pimoroni-pico` example filename you used (from their repo) and I will adapt `display.show()` to that API.

# e-ink-timer
pi pico &amp; inky pack (discontinued) 


# components
https://shop.pimoroni.com/products/pico-inky-pack
https://thepihut.com/blogs/raspberry-pi-tutorials/raspberry-pi-pico-getting-started-guide

# set-up steps for inky pack
1. https://github.com/pimoroni/pimoroni-pico/releases/latest/ download this
2. connect pi-pico to computer while holding down the bootsel button
3. drag download (.uf2) file onto pico
4. https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/pico_inky run one of these examples to test
 - use Thonny to run
 - (configure correct pi version in bottom right of IDE)

^ this is just because I know I'll forget if I have to do it from scratch and cba with the extensive scrolling/clicking to get this info

# design for the project
what can you do with pico and e-ink?
- hoping to connect this to a larger project later
- interested in creating seperation from "phone as single tool" because its so easy to then be distracted by it
- thinking of making it a timer for now
- the pack has three button so I'm imagining how I can branch with three functions

## ux design

home: clock (with screen saver function / only displays on button wake) / wheel display?
menu : option a/b/c
       timer / stopwatch/ eras
  timer : 5m / 25m / custom (on completion flash display)
      custom: increase / decrease / start
  stopwatch : start/stop / back / lap
  eras : wheel of year / time left in the work day

on all if double press "b" go back a menu option

thats all for now

### questions to ask
? does the menu make sense / are these the correct functions
? can we go to blank on disconnect
? splash screen
? can i power with a switch somehow?
? case 
