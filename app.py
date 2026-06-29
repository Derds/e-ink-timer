"""Application logic for the e-ink timer."""
import time
import machine
from display import Display

# --- Configuration ---
WIDTH = 296
HEIGHT = 128
WORK_END_HOUR = 17
WORK_END_MIN = 30
A_PIN = 14
B_PIN = 15
C_PIN = 16


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

        self.state = 'clock'
        self.prev_state = None
        self.last_b_time = 0
        self.b_press_count = 0
        self.custom_minutes = 5
        self.timer_end = None
        self.stopwatch_start = None
        self.last_refresh_ms = time.ticks_ms()

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
        self.display.clear(1)
        cx = WIDTH // 4
        cy = HEIGHT // 2
        radius = min(WIDTH, HEIGHT) // 4 - 2
        now = time.localtime()
        self.display.draw_clock(cx, cy, radius, now[3], now[4])
        rhs_x = WIDTH // 2 + 4
        hrs_rem, mins_rem = self.compute_work_remaining(now)
        self.display.draw_text(rhs_x, 8, 'Work left:')
        self.display.draw_text(rhs_x, 20, self.format_hm(hrs_rem, mins_rem))
        self.display.draw_text(rhs_x, 44, 'a: timer')
        self.display.draw_text(rhs_x, 56, 'b: stopwatch')
        self.display.draw_text(rhs_x, 68, 'c: splash')
        self.display.show()

    def draw_menu_timer(self):
        self.display.clear(1)
        self.display.draw_text(8, 8, 'Timer menu:')
        self.display.draw_text(8, 28, 'a: 5 minutes')
        self.display.draw_text(8, 44, 'b: 25 minutes')
        self.display.draw_text(8, 60, 'c: custom')
        self.display.show()

    def draw_custom(self):
        self.display.clear(1)
        self.display.draw_text(8, 8, 'Custom timer')
        self.display.draw_text(8, 28, '{} minutes'.format(self.custom_minutes))
        self.display.draw_text(8, 52, 'A:+1m  B:-1m  C:start')
        self.display.show()

    def draw_timer_running(self):
        self.display.clear(1)
        if self.timer_end is None:
            self.display.draw_text(8, 8, 'No timer')
        else:
            remaining = max(0, int(self.timer_end - time.time()))
            self.display.draw_text(8, 8, 'Timer running')
            self.display.draw_text(8, 28, '{}m{}s'.format(remaining // 60, remaining % 60))
        self.display.show()

    def draw_stopwatch(self, elapsed):
        self.display.clear(1)
        self.display.draw_text(8, 8, 'Stopwatch')
        self.display.draw_text(8, 28, '{}s'.format(int(elapsed)))
        self.display.draw_text(8, 52, 'B double-press: back')
        self.display.show()

    def draw_splash_view(self):
        print('App.draw_splash_view')
        self.display.draw_splash()

    def button_a(self):
        self.prev_state = self.state
        if self.state == 'clock':
            self.state = 'menu_timer'
            self.draw_menu_timer()
        elif self.state == 'menu_timer':
            self.timer_end = time.time() + 5 * 60
            self.state = 'timer_running'
            self.draw_timer_running()
        elif self.state == 'custom_adjust':
            self.custom_minutes += 1
            self.draw_custom()
        elif self.state == 'splash':
            self.state = 'menu_timer'
            self.draw_menu_timer()
        elif self.state == 'stopwatch_running':
            self.state = 'stopwatch_running'
            self.stopwatch_start = time.time()
            self.draw_stopwatch(0)

    def button_b(self):
        now_ms = time.ticks_ms()
        if time.ticks_diff(now_ms, self.last_b_time) < 400:
            self.b_press_count += 1
        else:
            self.b_press_count = 1
        self.last_b_time = now_ms

        if self.state == 'clock':
            if self.b_press_count >= 2:
                self.state = 'clock'
                self.draw_clock_view()
            else:
                self.state = 'stopwatch_running'
                self.stopwatch_start = time.time()
                self.draw_stopwatch(0)
        elif self.state == 'stopwatch_running' and self.b_press_count >= 2:
            self.state = 'clock'
            self.draw_clock_view()
        elif self.state == 'menu_timer':
            self.timer_end = time.time() + 25 * 60
            self.state = 'timer_running'
            self.draw_timer_running()
        elif self.state == 'custom_adjust':
            self.custom_minutes = max(1, self.custom_minutes - 1)
            self.draw_custom()
        elif self.state == 'splash':
            self.state = 'stopwatch_running'
            self.stopwatch_start = time.time()
            self.draw_stopwatch(0)

    def button_c(self):
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
            self.draw_timer_running()
        elif self.state == 'splash':
            self.state = 'clock'
            self.draw_clock_view()

    def handle_buttons(self):
        if self.btn_a.is_pressed():
            time.sleep_ms(20)
            if self.btn_a.is_pressed():
                while self.btn_a.is_pressed():
                    time.sleep_ms(10)
                self.button_a()
                return

        if self.btn_b.is_pressed():
            time.sleep_ms(20)
            if self.btn_b.is_pressed():
                while self.btn_b.is_pressed():
                    time.sleep_ms(10)
                self.button_b()
                return

        if self.btn_c.is_pressed():
            time.sleep_ms(20)
            if self.btn_c.is_pressed():
                while self.btn_c.is_pressed():
                    time.sleep_ms(10)
                self.button_c()
                return

    def run(self):
        self.draw_clock_view()
        while True:
            try:
                self.handle_buttons()
                if self.state == 'timer_running' and self.timer_end is not None and time.time() >= self.timer_end:
                    self.display.flash_message('timer complete!')
                    self.timer_end = None
                    self.state = 'clock'
                    self.draw_clock_view()
                elif self.state == 'stopwatch_running':
                    self.draw_stopwatch(time.time() - self.stopwatch_start)
                elif self.state == 'clock' and time.ticks_diff(time.ticks_ms(), self.last_refresh_ms) >= 30000:
                    self.draw_clock_view()
                    self.last_refresh_ms = time.ticks_ms()
                time.sleep(0.5)
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
        self.draw_custom()
        time.sleep(2)
