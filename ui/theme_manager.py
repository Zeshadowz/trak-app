"""
ThemeManager
============
Loads per-widget .qss files, substitutes ${token} placeholders with
values from the active Theme dataclass, and applies the result to the
QApplication — enabling live dark <-> light switching with no restart.

Stylesheet pipeline
-------------------
  styles/variables.py          ->  Theme dataclass  (design tokens)
      |  dataclasses.asdict()
  styles/*.qss                 ->  QSS with ${token_name} placeholders
      |  string.Template.substitute()
  QApplication.setStyleSheet() ->  live, cascaded to all widgets

Why string.Template?
--------------------
QSS uses { } for rule blocks — those would confuse str.format_map.
string.Template uses ${identifier} which never appears in plain CSS/QSS.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from string import Template

from PyQt6.QtWidgets import QApplication

from ui.styles.variables import Theme, THEMES, DARK

# Directory that contains the .qss files (same package as variables.py)
_STYLES_DIR = Path(__file__).parent / "styles"

# Applied in this order; later files win on equal-specificity rules
_QSS_FILES = [
    "app.qss",
    "input.qss"
]


class ThemeManager:
    """Owns the active theme and re-applies stylesheets on every toggle."""

    def __init__(self, app: QApplication, initial: str = "dark") -> None:
        self._app = app
        self._theme: Theme = THEMES.get(initial, DARK)
        self._listeners: list[callable] = []

        # Read .qss files once at startup; substitution happens per toggle
        self._templates: list[Template] = self._load_templates()

        # Style the app immediately before the first paint
        self._apply_global()

    # ── Public API ────────────────────────────────────────────────

    @property
    def theme(self) -> Theme:
        return self._theme

    @property
    def is_dark(self) -> bool:
        return self._theme.name == "dark"

    def toggle(self) -> None:
        """Switch dark <-> light with no restart."""
        next_name = "light" if self.is_dark else "dark"
        self._theme = THEMES[next_name]
        self._apply_global()
        self._notify_listeners()

    def set_theme(self, name: str) -> None:
        if name not in THEMES:
            raise ValueError(f"Unknown theme '{name}'. Available: {list(THEMES)}")
        self._theme = THEMES[name]
        self._apply_global()
        self._notify_listeners()

    def register_listener(self, fn: callable) -> None:
        """Register fn(theme: Theme) — called after every theme change."""
        self._listeners.append(fn)

    # ── Internals ─────────────────────────────────────────────────

    def _load_templates(self) -> list[Template]:
        """Read each .qss file once and wrap in a string.Template."""
        templates = []
        for filename in _QSS_FILES:
            path = _STYLES_DIR / filename
            templates.append(Template(path.read_text(encoding="utf-8")))
        return templates

    def _build_sheet(self) -> str:
        """
        Substitute every ${token} in each QSS template using the active
        theme's fields, then join all sheets into one stylesheet string.
        """
        tokens = dataclasses.asdict(self._theme)
        parts = [tpl.substitute(tokens) for tpl in self._templates]
        return "\n\n".join(parts)

    def _apply_global(self) -> None:
        self._app.setStyleSheet(self._build_sheet())

    def _notify_listeners(self) -> None:
        for fn in self._listeners:
            fn(self._theme)
