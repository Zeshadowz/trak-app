"""
Design tokens / theme variables.
All colors, spacing, typography and radii live here.
Each stylesheet module receives one of these dicts, never raw values.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    # ── Identity ─────────────────────────────────────────────────
    name: str

    # ── Backgrounds ──────────────────────────────────────────────
    bg_app: str  # outermost window / scene
    bg_card: str  # login card surface
    bg_card_border: str  # card border / outline
    bg_input: str  # text-field fill
    bg_input_focus: str  # text-field fill when focused
    bg_input_border: str
    bg_input_focus_border: str
    bg_toggle_track: str  # theme-toggle pill (inactive)
    bg_toggle_track_active: str

    # ── Text ─────────────────────────────────────────────────────
    text_primary: str
    text_secondary: str
    text_placeholder: str
    text_link: str
    text_on_accent: str  # text rendered on the accent button

    # ── Accent / CTA ─────────────────────────────────────────────
    accent: str
    accent_hover: str
    accent_pressed: str

    # ── Feedback ─────────────────────────────────────────────────
    color_working: str
    color_warning: str
    color_error: str
    color_success: str

    # ── Spacing (px) ─────────────────────────────────────────────
    padding_xs: int = 4
    padding_sm: int = 8
    padding_md: int = 14
    padding_lg: int = 20
    padding_xl: int = 32

    # ── Radii (px) ───────────────────────────────────────────────
    radius_sm: int = 6
    radius_md: int = 10
    radius_lg: int = 16
    radius_full: int = 999

    # ── Typography ───────────────────────────────────────────────
    font_family: str = "Segoe UI"
    font_size_xs: int = 10
    font_size_sm: int = 12
    font_size_md: int = 14
    font_size_lg: int = 18
    font_size_xl: int = 26
    font_size_hero: int = 32


# ─────────────────────────────────────────────────────────────────
#  Built-in themes
# ─────────────────────────────────────────────────────────────────

DARK = Theme(
    name="dark",
    # backgrounds
    bg_app="#0f1117",
    bg_card="#1a1d27",
    bg_card_border="#2a2d3e",
    bg_input="#12141e",
    bg_input_focus="#16192a",
    bg_input_border="#2e3150",
    bg_input_focus_border="#5b6af0",
    bg_toggle_track="#2a2d3e",
    bg_toggle_track_active="#5b6af0",
    # text
    text_primary="#e8eaf6",
    text_secondary="#7c82a8",
    text_placeholder="#454869",
    text_link="#7c8fff",
    text_on_accent="#ffffff",
    # accent
    accent="#5b6af0",
    accent_hover="#6e7df5",
    accent_pressed="#4a58e0",
    # feedback
    color_working="174ea6",
    color_warning="e37400",
    color_error="#f07070",
    color_success="#6bcf9e",
)

LIGHT = Theme(
    name="light",
    # backgrounds
    bg_app="#eef0f7",
    bg_card="#ffffff",
    bg_card_border="#d8dbe8",
    bg_input="#f4f5fb",
    bg_input_focus="#ffffff",
    bg_input_border="#c8cce0",
    bg_input_focus_border="#3f51b5",
    bg_toggle_track="#c8cce0",
    bg_toggle_track_active="#5b6af0",
    # text
    text_primary="#1a1d2e",
    text_secondary="#5a5f7e",
    text_placeholder="#adb2cc",
    text_link="#4a58e0",
    text_on_accent="#ffffff",
    # accent
    accent="#5b6af0",
    accent_hover="#4a58e0",
    accent_pressed="#3947d0",
    # feedback
    color_working="174ea6",
    color_warning="e37400",
    color_error="#d94f4f",
    color_success="#2e9e68",
)

THEMES: dict[str, Theme] = {
    DARK.name: DARK,
    LIGHT.name: LIGHT,
}
