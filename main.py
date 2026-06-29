"""
Simple MicroPython app for a Pico + Inky pack.

Features:
- Default view: clock with radial dial on the left
- Right: workday remaining (workday ends at 17:30) and compact button legend
- Button A: timer (menu: 5, 25, custom)
- Button B: stopwatch (double-press B to return)
- Custom timer: A increase minutes, B decrease, C start
- On timer complete: flash "timer complete!"

Notes:
- This code draws into a FrameBuffer and expects a compatible Inky driver
  to be adapted in `display.show()` if necessary.
- Pin numbers for buttons may need changing for your wiring.
"""
import time
import machine
import math
import sys
from display import Display

# --- Configuration (change as needed) ---
WIDTH = 296
HEIGHT = 128
WORK_END_HOUR = 17
WORK_END_MIN = 30

# Button GPIO pins (example pins; update for your wiring)
A_PIN = 14
B_PIN = 15
C_PIN = 16

# Buttons are assumed wired to pull the pin to ground when pressed


class Button:
    def __init__(self, pin_no):
        self.pin = machine.Pin(pin_no, machine.Pin.IN, machine.Pin.PULL_UP)

    def is_pressed(self):
        return self.pin.value() == 0


def compute_work_remaining(now):
    # now is a struct_time or tuple (year,mon,day,h,m,s,...)
    h = now[3]
    m = now[4]
    end_minutes = WORK_END_HOUR * 60 + WORK_END_MIN
    now_minutes = h * 60 + m
    rem = max(0, end_minutes - now_minutes)
    hrs = rem // 60
    mins = rem % 60
    return hrs, mins


def format_hm(h, m):
    return '{}h{}m'.format(h, m)


def wait_for_release(btn, timeout=1.0):
    # wait until button released or timeout
    start = time.ticks_ms()
    while btn.is_pressed() and (time.ticks_diff(time.ticks_ms(), start) < timeout * 1000):
        time.sleep_ms(10)


def main():
    display = Display(width=WIDTH, height=HEIGHT)
    btn_a = Button(A_PIN)
    btn_b = Button(B_PIN)
    btn_c = Button(C_PIN)

    state = 'clock'
    prev_state = None

    # For double-press detection on B
    last_b_time = 0
    b_press_count = 0

    custom_minutes = 5
    timer_end = None
    stopwatch_start = None
    last_refresh_ms = time.ticks_ms()

    def draw_clock_view():
        display.clear(1)
        # left radial clock
        cx = WIDTH // 4
        cy = HEIGHT // 2
        radius = min(WIDTH, HEIGHT) // 4 - 2
        # Get time; note: Pico needs RTC set for correct localtime
        now = time.localtime()
        hours = now[3]
        minutes = now[4]
        display.draw_clock(cx, cy, radius, hours, minutes)

        # right side info
        rhs_x = WIDTH // 2 + 4
        hrs_rem, mins_rem = compute_work_remaining(now)
        display.draw_text(rhs_x, 8, 'Work left:')
        display.draw_text(rhs_x, 20, format_hm(hrs_rem, mins_rem))

        # compact button legend
        display.draw_text(rhs_x, 44, 'a: timer')
        display.draw_text(rhs_x, 56, 'b: stopwatch')

        display.show()

    def draw_menu_timer():
        display.clear(1)
        display.draw_text(8, 8, 'Timer menu:')
        display.draw_text(8, 28, 'a: 5 minutes')
        display.draw_text(8, 44, 'b: 25 minutes')
        display.draw_text(8, 60, 'c: custom')
        display.show()

    def draw_custom(minutes):
        display.clear(1)
        display.draw_text(8, 8, 'Custom timer')
        display.draw_text(8, 28, '{} minutes'.format(minutes))
        display.draw_text(8, 52, 'A:+1m  B:-1m  C:start')
        display.show()

    def start_timer(minutes):
        nonlocal timer_end
        timer_end = time.time() + minutes * 60

    def draw_timer_running():
        display.clear(1)
        if timer_end is None:
            display.draw_text(8, 8, 'No timer')
        else:
            remaining = max(0, int(timer_end - time.time()))
            m = remaining // 60
            s = remaining % 60
            display.draw_text(8, 8, 'Timer running')
            display.draw_text(8, 28, '{}m{}s'.format(m, s))
        display.show()

    def draw_stopwatch(elapsed):
        display.clear(1)
        display.draw_text(8, 8, 'Stopwatch')
        display.draw_text(8, 28, '{}s'.format(int(elapsed)))
        display.draw_text(8, 52, 'B double-press: back')
        display.show()

    def draw_splash_view():
        display.draw_splash()

    # initial draw
    draw_clock_view()

    while True:
        try:
            # Poll buttons
            if btn_a.is_pressed():
                wait_for_release(btn_a)
                prev_state = state
                state = 'menu_timer'
                draw_menu_timer()

            if btn_b.is_pressed():
                # handle double-press detection
                now_ms = time.ticks_ms()
                if time.ticks_diff(now_ms, last_b_time) < 400:
                    b_press_count += 1
                else:
                    b_press_count = 1
                last_b_time = now_ms
                wait_for_release(btn_b)
                # double press -> go back
                if b_press_count >= 2:
                    # if in stopwatch, return to previous menu choice
                    if state.startswith('stopwatch'):
                        state = 'clock'
                        draw_clock_view()
                        b_press_count = 0
                        continue
                # single press -> start stopwatch
                prev_state = state
                state = 'stopwatch_running'
                stopwatch_start = time.time()
                draw_stopwatch(0)

            if btn_c.is_pressed():
                wait_for_release(btn_c)
                prev_state = state
                state = 'splash'
                draw_splash_view()

            # if in timer menu, wait for selection
            if state == 'menu_timer':
                if btn_a.is_pressed():
                    wait_for_release(btn_a)
                    start_timer(5)
                    state = 'timer_running'
                    draw_timer_running()
                elif btn_b.is_pressed():
                    wait_for_release(btn_b)
                    start_timer(25)
                    state = 'timer_running'
                    draw_timer_running()
                elif btn_c.is_pressed():
                    wait_for_release(btn_c)
                    state = 'custom_adjust'
                    custom_minutes = 5
                    draw_custom(custom_minutes)

            elif state == 'custom_adjust':
                if btn_a.is_pressed():
                    wait_for_release(btn_a)
                    custom_minutes += 1
                    draw_custom(custom_minutes)
                elif btn_b.is_pressed():
                    wait_for_release(btn_b)
                    custom_minutes = max(1, custom_minutes - 1)
                    draw_custom(custom_minutes)
                elif btn_c.is_pressed():
                    wait_for_release(btn_c)
                    start_timer(custom_minutes)
                    state = 'timer_running'
                    draw_timer_running()

            elif state == 'timer_running':
                if timer_end is not None and time.time() >= timer_end:
                    display.flash_message('timer complete!')
                    timer_end = None
                    state = 'clock'
                    draw_clock_view()

            elif state == 'stopwatch_running':
                elapsed = time.time() - stopwatch_start if stopwatch_start else 0
                draw_stopwatch(elapsed)

            elif state == 'splash':
                if btn_a.is_pressed():
                    wait_for_release(btn_a)
                    prev_state = state
                    state = 'menu_timer'
                    draw_menu_timer()
                elif btn_b.is_pressed():
                    wait_for_release(btn_b)
                    prev_state = state
                    state = 'stopwatch_running'
                    stopwatch_start = time.time()
                    draw_stopwatch(0)
                elif btn_c.is_pressed():
                    wait_for_release(btn_c)
                    state = 'clock'
                    draw_clock_view()

            # Only refresh the clock view when needed in idle state to avoid
            # redrawing the e-ink display continuously.
            if state == 'clock':
                if time.ticks_diff(time.ticks_ms(), last_refresh_ms) >= 30000:
                    draw_clock_view()
                    last_refresh_ms = time.ticks_ms()

            time.sleep(0.5)
        except Exception as e:
            try:
                sys.print_exception(e)
            except Exception:
                pass
            break


if __name__ == '__main__':
    main()
