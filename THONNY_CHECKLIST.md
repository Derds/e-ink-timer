# Thonny checklist for Raspberry Pi Pico + Inky Pack

1. Connect the Pico
   - Plug the Pico into USB normally. Do not hold BOOTSEL while plugging in unless you want to enter bootloader mode.
   - Use a known-good USB data cable (not a power-only cable).

2. Verify the Pico is not in BOOTSEL mode
   - If the Pico appears as a USB storage device, it is in BOOTSEL mode.
   - Press RESET or unplug and replug to boot the Pico normally.

3. Open Thonny and select the interpreter
   - In Thonny, go to `Run` → `Select interpreter`.
   - Choose `MicroPython (Raspberry Pi Pico)`.
   - If a port selector appears, choose the Pico port.
     - On Windows this is typically `COMx`.
     - On macOS it is typically `/dev/tty.usbmodem*`.

4. If Thonny says the port is not found
   - Unplug and plug the Pico back in.
   - Try a different USB port on the computer.
   - Try a different USB cable.
   - If you are on Windows, open Device Manager and look for a `COM` port under `Ports (COM & LPT)`.
   - If no Pico port appears, the issue is usually the USB cable or a bad connection.

5. If the Pico still does not appear
   - Reboot your computer, then reconnect the Pico.
   - Put the Pico in BOOTSEL mode once to verify that the bootloader storage device appears.
   - If it does, copy the correct `pimoroni-pico` UF2 file again to the Pico.
   - After flashing, unplug and plug the Pico back in normally.

6. Save the code to the Pico
   - In Thonny, choose `File` → `Save as...` and save to the device as `main.py`.
   - This ensures the program runs after power is removed and reconnected.

7. Restart the Pico
   - Unplug and replug the Pico after saving `main.py`.
   - The Pico should automatically run `main.py` if it is saved on the device.

8. Notes for Pimoroni Pico Inky Pack
   - The Pico Inky UF2 provides the display driver; you still select the normal Pico MicroPython interpreter in Thonny.
   - The display is e-ink, so the last image stays visible after power off.
   - To clear the screen, the program must draw an all-white frame and refresh the display.
