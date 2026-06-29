"""Application logic for the e-ink timer."""
import time
import machine
from display import Display

# --- Configuration ---
WIDTH = 296
HEIGHT = 128
WORK_END_HOUR = 17
WORK_END_MIN = 30
A_PIN = 12
B_PIN = 13
C_PIN = 14


class Button:
    def __init__(self, pin_no):
        self.pin = machine.Pin(pin_no, machine.Pin.IN, machine.Pin.PULL_UP)

    def is_pressed(self):
        return self.pin.value() == 0


class App:
    def __init__(self):
        self.display = Display(width=WIDTH, height=HEIGHT)
        self.btn_a = Button(A_PIN)
        self.btn_b = Button(B_PIN)
        self.btn_c = Button(C_PIN)
        # onboard LED for feedback (Pico default)
        try:
            self.led = machine.Pin(25, machine.Pin.OUT)
            self.led.value(0)
        except Exception:
            self.led = None

        self.state = 'clock'
        self.prev_state = None
        self.last_b_time = 0
        self.b_press_count = 0
        self.custom_minutes = 5
        self.timer_end = None
        self.stopwatch_start = None
        self.stopwatch_elapsed = 0
        self.last_refresh_ms = time.ticks_ms()
        self.last_timer_refresh_ms = time.ticks_ms()
        self.last_button = None
        self.last_button_time = time.ticks_ms()

    def compute_work_remaining(self, now):
        h = now[3]
        m = now[4]
        end_minutes = WORK_END_HOUR * 60 + WORK_END_MIN
        now_minutes = h * 60 + m
        rem = max(0, end_minutes - now_minutes)
        return rem // 60, rem % 60

    def format_hm(self, h, m):
        return '{}h{}m'.format(h, m)

    def draw_clock_view(self):
        print('App.draw_clock_view')
        self.display.clear(15)
        # Use RTC for the clock display when available (fallback to localtime)
        now = None
        try:
            rtc = machine.RTC()
            dt = rtc.datetime()
            # dt -> (year, month, day, weekday, hours, minutes, seconds, subseconds)
            if isinstance(dt, (tuple, list)) and len(dt) >= 8:
                now = (dt[0], dt[1], dt[2], dt[4], dt[5], dt[6], dt[3], 0)
        except Exception:
            pass
        if now is None:
            now = time.localtime()
        try:
            # ensure gothic font for the clock
            self.display.set_font('gothic')
        except Exception:
            pass
        time_str = '{:02}:{:02}'.format(now[3], now[4])
        date_str = '{:02}/{:02}'.format(now[2], now[1])
        # Make time the dominant element
        self.display.draw_text(42, 35, time_str, 0, scale=2)
        self.display.draw_text(222, 20, date_str, 0, scale=0.5)

        if (9 <= now[3] < WORK_END_HOUR) or (now[3] == WORK_END_HOUR and now[4] <= WORK_END_MIN):
            hrs_rem, mins_rem = self.compute_work_remaining(now)
            # Smaller text for work hours to fit the screen
            try:
                self.display.set_font('sans')
            except Exception:
                pass
            self.display.draw_text(20, 80, 'Work left:', 0, scale=0.75)
            self.display.draw_text(80, 80, self.format_hm(hrs_rem, mins_rem), 0, scale=0.75)
        else:
            try:
                self.display.set_font('gothic')
            except Exception:
                pass
            self.display.draw_text(60, 80, 'Outside work hours', 0, scale=0.5)

        # Options in sans, small
        try:
            self.display.set_font('sans')
        except Exception:
            pass
        self.display.draw_text(8, 110, 'A:timer B:stopwatch C:splash', 0, scale=0.6)
        self.display.show()

    def draw_menu_timer(self):
        self.display.clear(15)
        line_y = 12
        # Larger menu title and slightly bigger entries
        try:
            self.display.set_font('sans')
        except Exception:
            pass
        self.display.draw_text(10, line_y, 'Timer menu:', 0, scale=1)
        line_y += 20
        self.display.draw_text(10, line_y, '~~~~~~~~~~~~~~~~~~~', 0, scale=0.6)
        line_y += 25
        self.display.draw_text(8, line_y, 'a: 5 minutes', 0, scale=0.5)
        line_y += 25
        self.display.draw_text(8, line_y, 'b: 25 minutes', 0, scale=0.5)
        line_y += 25
        self.display.draw_text(8, line_y, 'c: custom', 0, scale=0.5)
        # Use full refresh for menu transitions to reduce ghosting
        self.display.show(full=True)

    def draw_custom(self):
        self.display.clear(15)
        line_y = 10
        try:
            self.display.set_font('gothic')
        except Exception:
            pass
        self.display.draw_text(8, line_y, 'Custom timer', 0, scale=1)
        line_y += 20
        self.display.draw_text(10, line_y, '~~~~~~~~~~~~~~~~~~', 0, scale=0.6)
        line_y += 36
        self.display.draw_text(8, line_y, '{} minutes'.format(self.custom_minutes), 0, scale=1.3)
        line_y += 36
        self.display.draw_text(8, line_y, 'A:+1m   B:-1m   C:start', 0, scale=0.7)
        self.display.show(full=True)

    def draw_timer_running(self, full=True):
        self.display.clear(15)
        if self.timer_end is None:
            self.display.draw_text(8, 40, 'No timer', 0, scale=1.5)
            self.display.draw_text(8, 90, 'C: back', 0)
            self.display.show(full=True)
            return
        self.display.draw_text(8, 10, 'Timer running', 0, scale=0.7)
        self.display.draw_text(8, 20, '~~~~~~~~~~~~~~~~~~', 0, scale=0.6)
        self.display.draw_text(8, 95, 'B: cancel   C: back', 0, scale=0.75)
        remaining = max(0, int(self.timer_end - time.time()))
        self.display.fill_rect(8, 56, 180, 50, 15)
        self.display.draw_text(8, 60, '{}m {}s'.format(remaining // 60, remaining % 60), 0, scale=2)
        self.display.show(full=True)

    def draw_stopwatch(self, elapsed, full=True, paused=False):
        try:
            self.display.set_font('sans')
        except Exception:
            pass
        self.display.clear(15)
        self.display.draw_text(8, 14, 'Stopwatch', 0, scale=1)
        if paused:
            self.display.draw_text(8, 100, 'A: start   C: back', 0, scale=0.75)
        else:
            self.display.draw_text(8, 100, 'B: stop   C: back', 0, scale=0.75)
        self.display.fill_rect(15, 60, 190, 50, 15)
        self.display.draw_text(15, 60, '{}s'.format(int(elapsed)), 0, scale=2)
        self.display.show(full=True)

    def draw_splash_view(self):
        print('App.draw_splash_view')
        self.display.draw_splash()

    def _blink_led(self, ms=80):
        if getattr(self, 'led', None) is None:
            return
        try:
            self.led.value(1)
            time.sleep_ms(ms)
            self.led.value(0)
        except Exception:
            pass

    def button_a(self):
        print('button_a() pressed; state=', self.state)
        self._blink_led()
        self.prev_state = self.state
        if self.state == 'clock':
            self.state = 'menu_timer'
            self.draw_menu_timer()
        elif self.state == 'menu_timer':
            self.timer_end = time.time() + 5 * 60
            self.last_timer_refresh_ms = time.ticks_ms()
            print('Timer started: 5 minutes')
            self.state = 'timer_running'
            self.draw_timer_running()
        elif self.state == 'custom_adjust':
            self.custom_minutes += 1
            self.draw_custom()
        elif self.state == 'splash':
            self.state = 'menu_timer'
            self.draw_menu_timer()
        elif self.state == 'stopwatch_paused':
            self.stopwatch_start = time.time()
            self.state = 'stopwatch_running'
            self.draw_stopwatch(self.stopwatch_elapsed, full=True)
        elif self.state == 'stopwatch_running':
            # no-op when already running
            return

    def button_b(self):
        print('button_b() pressed; state=', self.state)
        self._blink_led()
        # simplified press handling for testing (no debounce/re-check)
        if self.state == 'clock':
            self.state = 'stopwatch_running'
            self.stopwatch_start = time.time()
            self.stopwatch_elapsed = 0
            self.draw_stopwatch(0, full=True)
            return
        elif self.state == 'stopwatch_running':
            # pause stopwatch
            self.stopwatch_elapsed += time.time() - self.stopwatch_start
            self.state = 'stopwatch_paused'
            self.draw_stopwatch(self.stopwatch_elapsed, full=True, paused=True)
            return
        elif self.state == 'menu_timer':
            self.timer_end = time.time() + 25 * 60
            self.last_timer_refresh_ms = time.ticks_ms()
            print('Timer started: 25 minutes')
            self.state = 'timer_running'
            self.draw_timer_running()
        elif self.state == 'timer_running':
            # cancel timer
            self.timer_end = None
            print('Timer cancelled')
            self.state = 'clock'
            self.draw_clock_view()
        elif self.state == 'custom_adjust':
            self.custom_minutes = max(1, self.custom_minutes - 1)
            self.draw_custom()
        elif self.state == 'splash':
            self.state = 'stopwatch_running'
            self.stopwatch_start = time.time()
            self.stopwatch_elapsed = 0
            self.draw_stopwatch(0, full=True)

    def button_c(self):
        print('button_c() pressed; state=', self.state)
        self._blink_led()
        self.prev_state = self.state
        if self.state == 'clock':
            self.state = 'splash'
            self.draw_splash_view()
        elif self.state == 'menu_timer':
            self.state = 'custom_adjust'
            self.custom_minutes = 5
            self.draw_custom()
        elif self.state == 'custom_adjust':
            self.state = 'timer_running'
            self.timer_end = time.time() + self.custom_minutes * 60
            self.last_timer_refresh_ms = time.ticks_ms()
            print('Timer started: {} minutes'.format(self.custom_minutes))
            self.draw_timer_running()
        elif self.state == 'timer_running':
            self.state = 'clock'
            self.draw_clock_view()
        elif self.state == 'stopwatch_running':
            self.state = 'clock'
            self.draw_clock_view()
        elif self.state == 'stopwatch_paused':
            self.state = 'clock'
            self.draw_clock_view()
        elif self.state == 'splash':
            self.state = 'clock'
            self.draw_clock_view()

    def handle_buttons(self):
        # Read raw button states and log for diagnostics (always print)
        a_pressed = self.btn_a.is_pressed()
        b_pressed = self.btn_b.is_pressed()
        c_pressed = self.btn_c.is_pressed()
        now_ms = time.ticks_ms()
        print('handle_buttons: A=%s B=%s C=%s' % (a_pressed, b_pressed, c_pressed))

        # Debounce: ignore repeated reads within 200ms
        if now_ms is not None and time.ticks_diff(now_ms, self.last_button_time) < 200:
            return

        # Prioritize C (splash/back), then B, then A to match expected navigation
        if c_pressed:
            self.last_button = 'C'
            self.last_button_time = now_ms
            self.button_c()
            return
        if b_pressed:
            self.last_button = 'B'
            self.last_button_time = now_ms
            self.button_b()
            return
        if a_pressed:
            self.last_button = 'A'
            self.last_button_time = now_ms
            self.button_a()
            return

    def run(self):
        self.draw_splash_view()
        time.sleep(4)
        self.draw_clock_view()
        while True:
            try:
                self.handle_buttons()
                # Timer completion check
                if self.state == 'timer_running' and self.timer_end is not None and time.time() >= self.timer_end:
                    self.display.flash_message('timer complete!')
                    self.timer_end = None
                    self.state = 'clock'
                    self.draw_clock_view()
                # Update running timer every second
                elif self.state == 'timer_running' and self.timer_end is not None:
                    if time.ticks_diff(time.ticks_ms(), self.last_timer_refresh_ms) >= 1000:
                        self.draw_timer_running()
                        self.last_timer_refresh_ms = time.ticks_ms()
                elif self.state == 'stopwatch_running':
                    elapsed = self.stopwatch_elapsed + (time.time() - self.stopwatch_start)
                    self.draw_stopwatch(elapsed)
                # Periodic clock refresh
                elif self.state == 'clock' and time.ticks_diff(time.ticks_ms(), self.last_refresh_ms) >= 1000:
                    self.draw_clock_view()
                    self.last_refresh_ms = time.ticks_ms()
                time.sleep(0.05)
            except Exception as e:
                try:
                    print('ERROR:', e)
                except Exception:
                    pass

    def test_display(self):
        self.draw_clock_view()
        time.sleep(2)
        self.draw_splash_view()
        time.sleep(2)
        self.draw_menu_timer()
        time.sleep(2)
        self.draw_stopwatch(10)
        time.sleep(4)
        self.draw_custom()
        time.sleep(2)
        self.draw_splash_view()

