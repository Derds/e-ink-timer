"""Minimal entry point for the e-ink timer app."""
import app

# Set RUN_MODE to 'run' to start the full app,
# or 'test' to show individual screens for troubleshooting.
RUN_MODE = 'run'

if __name__ == '__main__':
    application = app.App()
    if RUN_MODE == 'test':
        application.test_display()
    else:
        application.run()
