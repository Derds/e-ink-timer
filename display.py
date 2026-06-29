"""
Simple display abstraction for MicroPython + Inky Pack using PicoGraphics.

This version is intentionally minimal and assumes `picographics` is
available, because your hardware works with the direct PicoGraphics pattern
shown in your example.
"""
import math


class Display:
    def __init__(self, width=296, height=128):
        self.width = width
        self.height = height
        self.inky_obj = None
        self.drawer = None
        self.native_canvas = False
        self.debug = True

        self._init_driver()
        if self.debug:
            print('Display.__init__: width=', self.width, 'height=', self.height, 'native_canvas=', self.native_canvas)
        self.clear(15)

    def _init_driver(self):
        try:
            import picographics
            self.inky_obj = picographics.PicoGraphics(picographics.DISPLAY_INKY_PACK)
            self.width, self.height = self.inky_obj.get_bounds()
            if hasattr(self.inky_obj, 'set_update_speed'):
                try:
                    self.inky_obj.set_update_speed(3)
                except Exception:
                    pass
            if hasattr(self.inky_obj, 'set_font'):
                try:
                    self.inky_obj.set_font('gothic')
                except Exception:
                    pass
            self.drawer = self.inky_obj
            self.native_canvas = True
            print('Display: picographics native driver', self.width, self.height)
            return
        except Exception as e:
            print('Display: picographics unavailable', e)

        print('Display: no working native display driver')

    def clear(self, color=1):
        if self.drawer is None:
            return
        if self.debug:
            print('Display.clear: color=', color, 'native=', self.native_canvas)
        if self.native_canvas:
            self.set_pen(color)
            try:
                self.drawer.clear()
                if self.debug:
                    print('Display.clear: native clear() succeeded')
                return
            except Exception as e:
                if self.debug:
                    print('Display.clear: native clear() failed', e)
        try:
            self.drawer.clear(color)
            if self.debug:
                print('Display.clear: clear(color) succeeded')
            return
        except Exception as e:
            if self.debug:
                print('Display.clear: clear(color) failed', e)
            try:
                self.drawer.fill(color)
                if self.debug:
                    print('Display.clear: fill(color) succeeded')
                return
            except Exception as e2:
                if self.debug:
                    print('Display.clear: fill(color) failed', e2)
                pass

    def set_pen(self, color):
        if self.drawer is None:
            return
        if self.debug:
            print('Display.set_pen:', color, 'native=', self.native_canvas)
        if hasattr(self.drawer, 'set_pen'):
            try:
                self.drawer.set_pen(color)
            except Exception as e:
                if self.debug:
                    print('Display.set_pen failed', e)

    def draw_line(self, x1, y1, x2, y2, color=0):
        self.set_pen(color)
        try:
            self.drawer.line(x1, y1, x2, y2)
        except Exception:
            pass

    def draw_pixel(self, x, y, color=0):
        self.set_pen(color)
        try:
            self.drawer.pixel(x, y)
        except Exception:
            pass

    def draw_text(self, x, y, text, color=0, scale=1):
        if self.debug:
            print('Display.draw_text:', text, 'x=', x, 'y=', y, 'color=', color, 'scale=', scale)
        self.set_pen(color)
        try:
            self.drawer.text(text, x, y, scale=scale)
            if self.debug:
                print('Display.draw_text: text(text,x,y,scale=) succeeded')
            return
        except TypeError as e:
            if self.debug:
                print('Display.draw_text: text(text,x,y,scale=) failed', e)
        except Exception as e:
            if self.debug:
                print('Display.draw_text: text(text,x,y,scale=) failed', e)
        try:
            self.drawer.text(text, x, y, scale)
            if self.debug:
                print('Display.draw_text: text(text,x,y,scale) succeeded')
            return
        except Exception as e:
            if self.debug:
                print('Display.draw_text: text(text,x,y,scale) failed', e)
        try:
            self.drawer.text(text, x, y)
            if self.debug:
                print('Display.draw_text: fallback text(text,x,y) succeeded')
            return
        except Exception as e:
            if self.debug:
                print('Display.draw_text: fallback text(text,x,y) failed', e)
        if self.debug:
            print('Display.draw_text: all text signatures failed')

    def show(self):
        if self.debug:
            print('Display.show: native_canvas=', self.native_canvas)
        if self.inky_obj is None:
            print('Display.show: no driver loaded')
            return
        if hasattr(self.inky_obj, 'update'):
            try:
                self.inky_obj.update()
                print('Display.show: native update')
                return
            except Exception as e:
                print('Display.show: native update failed', e)
        if hasattr(self.inky_obj, 'show'):
            try:
                self.inky_obj.show()
                print('Display.show: native show')
                return
            except Exception as e:
                print('Display.show: native show failed', e)
        print('Display.show: no update/show method')

    def flash_message(self, text, seconds=3):
        self.clear(15)
        self.draw_text((self.width - len(text) * 8) // 2, (self.height - 8) // 2, text, 0)
        self.show()

    def draw_clock(self, cx, cy, radius, hours, minutes):
        self.draw_circle(cx, cy, radius, 0)
        for m in range(0, 60, 5):
            angle = (m / 60.0) * 2 * math.pi
            x1 = int(cx + (radius - 2) * math.cos(angle - math.pi / 2))
            y1 = int(cy + (radius - 2) * math.sin(angle - math.pi / 2))
            x2 = int(cx + radius * math.cos(angle - math.pi / 2))
            y2 = int(cy + radius * math.sin(angle - math.pi / 2))
            self.draw_line(x1, y1, x2, y2, 0)

        minute_angle = (minutes / 60.0) * 2 * math.pi
        mx = int(cx + (radius - 6) * math.cos(minute_angle - math.pi / 2))
        my = int(cy + (radius - 6) * math.sin(minute_angle - math.pi / 2))
        self.draw_line(cx, cy, mx, my, 0)

        hour_angle = ((hours % 12 + minutes / 60.0) / 12.0) * 2 * math.pi
        hx = int(cx + (radius - 14) * math.cos(hour_angle - math.pi / 2))
        hy = int(cy + (radius - 14) * math.sin(hour_angle - math.pi / 2))
        self.draw_line(cx, cy, hx, hy, 0)

    def draw_splash(self):
        if self.debug:
            print('Display.draw_splash: clearing and drawing splash')
        self.clear(15)
        self.draw_text(8, self.height // 2 - 8, 'cyberderds timer', 0, scale=1.5)
        self.show()

    def draw_circle(self, cx, cy, r, color=0):
        self.set_pen(color)
        for deg in range(0, 360, 4):
            a = math.radians(deg)
            x = int(cx + r * math.cos(a))
            y = int(cy + r * math.sin(a))
            if 0 <= x < self.width and 0 <= y < self.height:
                self.draw_pixel(x, y, color)
