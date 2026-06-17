import sys
import time
import threading

sys.path.insert(0, 'src')

print('=== Diagnostic Start ===')
print()

try:
    from c_helper.core import Config
    cfg = Config.load('config.json')
    print('[OK] Config loaded')
    print(f'     Model: {cfg.model}')
    print(f'     Delay: {cfg.typing_delay_ms}ms')
except Exception as e:
    print(f'[FAIL] Config: {e}')

try:
    from c_helper.core import IconRenderer, State
    for s in State:
        img = IconRenderer.render(s)
    print('[OK] Icons rendered')
except Exception as e:
    print(f'[FAIL] Icons: {e}')

try:
    from c_helper.main import TrayManager
    tray = TrayManager(on_reset=lambda: None, on_quit=lambda: None)
    t = threading.Thread(target=tray.run, daemon=True)
    t.start()
    time.sleep(1)
    if tray.icon:
        print('[OK] Tray initialized')
        print(f'     Icon: {tray.icon}')
        for s in State:
            tray.set_state(s)
            time.sleep(0.3)
        print('[OK] State transitions passed')
        tray.stop()
    else:
        print('[FAIL] Tray icon not created')
except Exception as e:
    print(f'[FAIL] Tray: {e}')
    import traceback
    traceback.print_exc()

try:
    from pynput.keyboard import HotKey
    hk = HotKey(HotKey.parse('<ctrl>+g'), lambda: None)
    print('[OK] Hotkey parsed (Ctrl+Alt+G)')
except Exception as e:
    print(f'[FAIL] Hotkey: {e}')

try:
    import pyperclip
    text = pyperclip.paste()
    print(f'[OK] Clipboard read (len={len(text)})')
except Exception as e:
    print(f'[FAIL] Clipboard: {e}')

print()
print('=== Diagnostic Complete ===')
print('If all [OK] but tray not visible, check:')
print('1. Taskbar settings -> System tray -> Show hidden icons')
print('2. Run as administrator if security software blocks tray icons')
print('3. Explorer.exe must be running')
input('Press Enter to exit...')
