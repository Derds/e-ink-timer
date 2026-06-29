"""
Simple display abstraction for MicroPython + Inky pack.

This tries to keep drawing code independent of the specific Inky driver.
If a compatible Inky MicroPython driver is installed and exposes a
`display_buffer(buffer, width, height)`-style API, adapt the `show()` method.

This file focuses on drawing into a FrameBuffer so the logic in `main.py`
remains easy to read and change.
"""
import math
import framebuf


class Display:
    def __init__(self, width=212, height=104):
        self.width = width
        self.height = height
        # 1 bit per pixel buffer; bytes per row must round up
        self.bytes_per_row = (self.width + 7) // 8
        self.buffer = bytearray(self.bytes_per_row * self.height)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.clear()
        # driver placeholder and runtime-detected driver instance
        self.inky_obj = None
        self.driver_name = None
        self.driver_methods = []
        # Try to import common Pico/Inky drivers. We prefer Pimoroni's
        # `pico_inky` when available for the Pico Inky Pack (296x128).
        try:
            import pico_inky as _pico_inky
            self.driver_name = 'pico_inky'
            self.inky_obj = self._instantiate_driver_module(_pico_inky)
        except Exception as e:
            try:
                import inky as _inky
                self.driver_name = 'inky'
                self.inky_obj = self._instantiate_driver_module(_inky)
            except Exception as e2:
                self.inky_obj = None
                print('Display: no Pico Inky driver found', e, getattr(e2, 'args', None))
        if self.inky_obj is not None:
            self.driver_methods = [name for name in dir(self.inky_obj) if not name.startswith('_')]
            print('Display: using driver', self.driver_name, 'methods:', self.driver_methods)

    def _instantiate_driver_module(self, module):
        if hasattr(module, 'PicoInky'):
            try:
                return module.PicoInky()
            except Exception:
                pass
        if hasattr(module, 'Inky'):
            try:
                return module.Inky()
            except Exception:
                pass
        if hasattr(module, 'inky'):
            try:
                return module.inky()
            except Exception:
                pass
        return module

    def clear(self, color=1):
        # color: 0 for black, 1 for white
        self.fb.fill(color)

    def show(self):
        # Send buffer to display. This tries several common Pimoroni APIs and
        # falls back to no-op if none are present. Adapt to your installed
        # MicroPython driver if necessary.
        if self.inky_obj is None:
            print('Display.show: no driver loaded')
            return

        # Try a sequence of likely API names. Methods may accept either the
        # raw bytearray, or (buffer, width, height).
        methods = [
            'set_frame_buffer',
            'set_framebuffer',
            'display_buffer',
            'display',
            'show',
            'update',
        ]

        for m in methods:
            fn = getattr(self.inky_obj, m, None)
            if fn is None:
                continue
            try:
                fn(self.buffer)
                print('Display.show: wrote buffer via', m)
                return
            except TypeError:
                pass
            try:
                fn(self.buffer, self.width, self.height)
                print('Display.show: wrote buffer via', m, '(buffer,width,height)')
                return
            except TypeError:
                pass
            try:
                fn(self.width, self.height, self.buffer)
                print('Display.show: wrote buffer via', m, '(width,height,buffer)')
                return
            except TypeError:
                pass
            except Exception:
                print('Display.show: method', m, 'raised', sys.exc_info())
                pass

        # Some drivers require an internal framebuf property and update call.
        if hasattr(self.inky_obj, 'framebuf'):
            try:
                self.inky_obj.framebuf(self.buffer)
                if hasattr(self.inky_obj, 'update'):
                    self.inky_obj.update()
                    print('Display.show: used framebuf/update')
                else:
                    print('Display.show: used framebuf only')
                return
            except Exception as e:
                print('Display.show: framebuf update failed', e)

        print('Display.show: no working display method found for', self.driver_name, self.driver_methods)

    def flash_message(self, text, seconds=3):
        # Simple invert-then-text flash
        self.fb.fill(0)  # black background
        # white text
        x = max(0, (self.width - len(text) * 8) // 2)
        y = max(0, (self.height - 8) // 2)
        self.fb.text(text, x, y, 1)
        self.show()

    def draw_clock(self, cx, cy, radius, hours, minutes):
        # Outline circle
        self._draw_circle(cx, cy, radius, 0)
        # minute ticks
        for m in range(0, 60, 5):
            angle = (m / 60.0) * 2 * math.pi
            x1 = int(cx + (radius - 2) * math.cos(angle - math.pi/2))
            y1 = int(cy + (radius - 2) * math.sin(angle - math.pi/2))
            x2 = int(cx + radius * math.cos(angle - math.pi/2))
            y2 = int(cy + radius * math.sin(angle - math.pi/2))
            self.fb.line(x1, y1, x2, y2, 0)

        # minute hand
        minute_angle = (minutes / 60.0) * 2 * math.pi
        mx = int(cx + (radius - 6) * math.cos(minute_angle - math.pi/2))
        my = int(cy + (radius - 6) * math.sin(minute_angle - math.pi/2))
        self.fb.line(cx, cy, mx, my, 0)

        # hour hand
        hour_angle = ((hours % 12 + minutes / 60.0) / 12.0) * 2 * math.pi
        hx = int(cx + (radius - 14) * math.cos(hour_angle - math.pi/2))
        hy = int(cy + (radius - 14) * math.sin(hour_angle - math.pi/2))
        self.fb.line(cx, cy, hx, hy, 0)

    def draw_text(self, x, y, text, color=0):
        self.fb.text(text, x, y, color)

    def draw_splash(self):
        self.clear(1)
        text = 'cyberderds timer'
        y = self.height // 2 - 8
        # Prefer driver-provided graphics API if available.
        gfx = None
        if self.inky_obj is not None:
            gfx = getattr(self.inky_obj, 'graphics', None)
            if gfx is None:
                gfx = self.inky_obj

        if gfx is not None and hasattr(gfx, 'text'):
            try:
                if hasattr(gfx, 'set_font'):
                    gfx.set_font('gothic')

                # Try several possible text call signatures.
                for args in [
                    (text, 10, y, 0),
                    (10, y, text, 0),
                    (10, y, text),
                    (text, 10, y),
                ]:
                    try:
                        gfx.text(*args)
                        self.show()
                        return
                    except TypeError:
                        continue
                    except Exception:
                        # If any other exception occurs, try the next signature.
                        continue
            except Exception:
                pass

        self.fb.text(text, 8, y, 0)
        self.show()

    def _draw_circle(self, cx, cy, r, color=0):
        # simple circle rasterization (degrees step of 4 keeps it light)
        for deg in range(0, 360, 4):
            a = math.radians(deg)
            x = int(cx + r * math.cos(a))
            y = int(cy + r * math.sin(a))
            if 0 <= x < self.width and 0 <= y < self.height:
                self.fb.pixel(x, y, color)
