import os
import json

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'db', 'settings.json')
DEFAULT_SETTINGS = {
    'read_only': True
}


def _load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def _save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)


def get_read_only() -> bool:
    settings = _load_settings()
    return bool(settings.get('read_only', True))


def set_read_only(value: bool) -> None:
    settings = _load_settings()
    settings['read_only'] = bool(value)
    _save_settings(settings)
