"""
VSCode "Neon Green - Liquid Glass" Theme Installer
--------------------------------------------------
Creates a self-contained local extension directly in VSCode's extensions folder.
No internet, no marketplace, no extension install permissions required.

Custom touches:
  - Terminal text is PURPLE
  - Copilot chat (right-side / auxiliary bar) text is PURPLE
  - Everything else: neon green accents on a deep, semi-transparent dark
    background to give a "liquid glass" feel

Run: python setup_neon_green_liquid_glass_theme.py
Then reload VSCode (Ctrl+Shift+P -> "Developer: Reload Window") and pick
the theme via Ctrl+K Ctrl+T -> "Neon Green - Liquid Glass".
"""

import json
import os
import platform
import shutil


# ---------- Paths ----------------------------------------------------------

def get_vscode_paths():
    system = platform.system()
    home = os.path.expanduser("~")

    portable_data = _find_portable_data_dir()
    if portable_data:
        settings = os.path.join(portable_data, "user-data", "User", "settings.json")
        extensions = os.path.join(portable_data, "extensions")
        return settings, extensions

    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
        settings = os.path.join(base, "Code", "User", "settings.json")
        extensions = os.path.join(home, ".vscode", "extensions")
    elif system == "Darwin":
        settings = os.path.join(home, "Library", "Application Support", "Code", "User", "settings.json")
        extensions = os.path.join(home, ".vscode", "extensions")
    else:
        settings = os.path.join(home, ".config", "Code", "User", "settings.json")
        extensions = os.path.join(home, ".vscode", "extensions")
    return settings, extensions


def _find_portable_data_dir():
    if platform.system() != "Windows":
        return None
    try:
        import subprocess
        result = subprocess.run(
            ["wmic", "process", "where", "name='Code.exe'", "get", "ExecutablePath", "/value"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines():
            if line.startswith("ExecutablePath="):
                exe_path = line.split("=", 1)[1].strip()
                data_dir = os.path.join(os.path.dirname(exe_path), "data")
                if os.path.isdir(data_dir):
                    return data_dir
    except Exception:
        pass
    return None


# ---------- Theme data -----------------------------------------------------

EXTENSION_ID = "local.neon-green-liquid-glass"
EXTENSION_VERSION = "1.0.0"
EXTENSION_FOLDER = f"{EXTENSION_ID}-{EXTENSION_VERSION}"
THEME_NAME = "Neon Green - Liquid Glass"

# Palette
NEON_GREEN = "#00ff41"
NEON_GREEN_SOFT = "#39ff14"
NEON_GREEN_DIM = "#1f6f3f"
GREEN_TEXT = "#b8ffd0"
PURPLE = "#c77dff"        # terminal + copilot chat text
PURPLE_BRIGHT = "#e0aaff"
GLASS_BG = "#0a120c"      # near-black with green tint
GLASS_BG_DEEP = "#06090a"
GLASS_PANEL = "#0d160f"
GLASS_HIGHLIGHT = "#00ff4115"  # semi-transparent green wash
GLASS_SELECTION = "#00ff4133"
DIM = "#5a6b5a"

PACKAGE_JSON = {
    "name": "neon-green-liquid-glass",
    "displayName": "Neon Green - Liquid Glass (Local)",
    "description": "Locally installed Neon Green Liquid Glass theme with purple terminal and chat text.",
    "version": EXTENSION_VERSION,
    "publisher": "local",
    "engines": {"vscode": "^1.0.0"},
    "categories": ["Themes"],
    "contributes": {
        "themes": [
            {
                "label": THEME_NAME,
                "uiTheme": "vs-dark",
                "path": "./themes/neon-green-liquid-glass.json",
            }
        ]
    },
}

THEME_JSON = {
    "name": THEME_NAME,
    "type": "dark",
    "colors": {
        # --- Activity bar ---
        "activityBar.background": GLASS_BG_DEEP,
        "activityBar.foreground": NEON_GREEN,
        "activityBar.inactiveForeground": DIM,
        "activityBarBadge.background": NEON_GREEN,
        "activityBarBadge.foreground": "#000000",

        # --- Side bar (file explorer) ---
        "sideBar.background": GLASS_PANEL,
        "sideBar.foreground": GREEN_TEXT,
        "sideBarTitle.foreground": NEON_GREEN,
        "sideBarSectionHeader.background": GLASS_BG,
        "sideBarSectionHeader.foreground": NEON_GREEN_SOFT,

        # --- Auxiliary bar (RIGHT side - hosts Copilot Chat) ---
        # Per user request: text here is PURPLE
        "auxiliaryBar.background": GLASS_PANEL,
        "auxiliaryBar.foreground": PURPLE,
        "auxiliaryBar.border": NEON_GREEN_DIM,
        "auxiliaryBarTitle.foreground": PURPLE_BRIGHT,

        # --- Editor ---
        "editor.background": GLASS_BG,
        "editor.foreground": GREEN_TEXT,
        "editor.lineHighlightBackground": GLASS_HIGHLIGHT,
        "editor.selectionBackground": GLASS_SELECTION,
        "editor.inactiveSelectionBackground": "#00ff4115",
        "editorCursor.foreground": NEON_GREEN,
        "editorWhitespace.foreground": "#1a2a1a",
        "editorIndentGuide.background": "#162016",
        "editorIndentGuide.activeBackground": NEON_GREEN,
        "editorLineNumber.foreground": "#3a4a3a",
        "editorLineNumber.activeForeground": NEON_GREEN,

        # --- Status bar ---
        "statusBar.background": GLASS_BG_DEEP,
        "statusBar.foreground": NEON_GREEN,
        "statusBar.debuggingBackground": PURPLE,
        "statusBar.debuggingForeground": "#000000",
        "statusBar.border": NEON_GREEN_DIM,

        # --- Title bar ---
        "titleBar.activeBackground": GLASS_BG_DEEP,
        "titleBar.activeForeground": NEON_GREEN,
        "titleBar.inactiveBackground": "#000000",
        "titleBar.inactiveForeground": DIM,

        # --- Tabs ---
        "editorGroupHeader.tabsBackground": GLASS_BG_DEEP,
        "editorGroupHeader.tabsBorder": NEON_GREEN_DIM,
        "editorGroupHeader.noTabsBackground": GLASS_BG_DEEP,
        "tab.activeBackground": GLASS_BG,
        "tab.activeForeground": NEON_GREEN,
        "tab.activeBorderTop": NEON_GREEN,
        "tab.inactiveBackground": GLASS_BG_DEEP,
        "tab.inactiveForeground": DIM,
        "tab.border": "#0a120c",

        # --- Bottom panel (output, debug, problems) ---
        "panel.background": GLASS_PANEL,
        "panel.border": NEON_GREEN_DIM,
        "panelTitle.activeForeground": NEON_GREEN,
        "panelTitle.inactiveForeground": DIM,

        # --- Terminal ---
        # Per user request: terminal text is PURPLE
        "terminal.background": GLASS_BG_DEEP,
        "terminal.foreground": PURPLE,
        "terminalCursor.foreground": PURPLE_BRIGHT,
        "terminal.selectionBackground": "#c77dff33",
        "terminal.ansiBlack": "#000000",
        "terminal.ansiBlue": "#5a9eff",
        "terminal.ansiCyan": "#00ffff",
        "terminal.ansiGreen": NEON_GREEN,
        "terminal.ansiMagenta": PURPLE,
        "terminal.ansiRed": "#ff5577",
        "terminal.ansiWhite": "#e0e0e0",
        "terminal.ansiYellow": "#ffe066",
        "terminal.ansiBrightBlack": "#666666",
        "terminal.ansiBrightBlue": "#80b8ff",
        "terminal.ansiBrightCyan": "#80ffff",
        "terminal.ansiBrightGreen": NEON_GREEN_SOFT,
        "terminal.ansiBrightMagenta": PURPLE_BRIGHT,
        "terminal.ansiBrightRed": "#ff8080",
        "terminal.ansiBrightWhite": "#ffffff",
        "terminal.ansiBrightYellow": "#ffff80",

        # --- Scrollbars ---
        "scrollbarSlider.background": "#1a2a1a80",
        "scrollbarSlider.hoverBackground": "#00ff4180",
        "scrollbarSlider.activeBackground": NEON_GREEN,

        # --- Inputs / dropdowns ---
        "input.background": GLASS_BG,
        "input.foreground": GREEN_TEXT,
        "input.border": NEON_GREEN_DIM,
        "input.placeholderForeground": DIM,
        "dropdown.background": GLASS_BG,
        "dropdown.foreground": GREEN_TEXT,
        "dropdown.border": NEON_GREEN_DIM,

        # --- Buttons ---
        "button.background": NEON_GREEN,
        "button.foreground": "#000000",
        "button.hoverBackground": NEON_GREEN_SOFT,
        "button.secondaryBackground": GLASS_PANEL,
        "button.secondaryForeground": NEON_GREEN,

        # --- Notifications ---
        "notification.background": GLASS_PANEL,
        "notification.foreground": GREEN_TEXT,
        "notification.border": NEON_GREEN_DIM,
        "notificationCenterHeader.background": GLASS_BG_DEEP,
        "notificationCenterHeader.foreground": NEON_GREEN,

        # --- Progress / lists ---
        "progressBar.background": NEON_GREEN,
        "list.activeSelectionBackground": GLASS_SELECTION,
        "list.activeSelectionForeground": NEON_GREEN,
        "list.inactiveSelectionBackground": GLASS_HIGHLIGHT,
        "list.inactiveSelectionForeground": GREEN_TEXT,
        "list.hoverBackground": GLASS_HIGHLIGHT,
        "list.hoverForeground": NEON_GREEN_SOFT,
        "list.focusBackground": GLASS_SELECTION,
        "tree.indentGuidesStroke": "#1a2a1a",

        # --- Diff editor ---
        "diffEditor.insertedTextBackground": "#00ff4120",
        "diffEditor.removedTextBackground": "#ff558020",

        # --- Quick input / pickers ---
        "quickInput.background": GLASS_BG_DEEP,
        "quickInput.foreground": GREEN_TEXT,
        "quickInputList.focusBackground": GLASS_SELECTION,
        "quickInputList.focusForeground": NEON_GREEN,
        "pickerGroup.background": GLASS_BG_DEEP,
        "pickerGroup.foreground": NEON_GREEN,
        "pickerGroup.border": NEON_GREEN_DIM,

        # --- Menus ---
        "menu.background": GLASS_BG_DEEP,
        "menu.foreground": GREEN_TEXT,
        "menu.selectionBackground": GLASS_SELECTION,
        "menu.selectionForeground": NEON_GREEN,
        "menubar.selectionBackground": GLASS_HIGHLIGHT,
        "menubar.selectionForeground": NEON_GREEN,

        # --- Suggest / hover widgets ---
        "editorSuggestWidget.background": GLASS_BG_DEEP,
        "editorSuggestWidget.border": NEON_GREEN_DIM,
        "editorSuggestWidget.selectedBackground": GLASS_SELECTION,
        "editorSuggestWidget.highlightForeground": NEON_GREEN,
        "editorHoverWidget.background": GLASS_BG_DEEP,
        "editorHoverWidget.border": NEON_GREEN_DIM,

        # --- Debug / peek / widgets ---
        "debugToolBar.background": GLASS_BG_DEEP,
        "debugToolBar.border": NEON_GREEN_DIM,
        "editorWidget.background": GLASS_BG_DEEP,
        "editorWidget.border": NEON_GREEN_DIM,
        "peekView.border": NEON_GREEN,
        "peekViewEditor.background": GLASS_BG,
        "peekViewResult.background": GLASS_BG_DEEP,
        "peekViewTitle.background": GLASS_BG_DEEP,
        "peekViewTitleLabel.foreground": NEON_GREEN,
        "peekViewTitleDescription.foreground": DIM,

        # --- Chat (Copilot) panel-specific tokens ---
        # These help paint Copilot Chat content. The auxiliaryBar.foreground
        # above is the main lever; these are extra coverage.
        "chat.requestBackground": GLASS_PANEL,
        "chat.requestBorder": NEON_GREEN_DIM,
        "chat.slashCommandBackground": GLASS_HIGHLIGHT,
        "chat.slashCommandForeground": PURPLE,
        "chat.avatarBackground": NEON_GREEN_DIM,
        "chat.avatarForeground": PURPLE_BRIGHT,
        "interactive.activeCodeBorder": NEON_GREEN,
        "interactive.inactiveCodeBorder": NEON_GREEN_DIM,

        # --- Misc ---
        "widget.shadow": "#00000099",
        "textBlockQuote.background": GLASS_PANEL,
        "textBlockQuote.border": NEON_GREEN,
        "textCodeBlock.background": GLASS_PANEL,
        "textLink.foreground": NEON_GREEN_SOFT,
        "textLink.activeForeground": PURPLE_BRIGHT,
        "textPreformat.foreground": NEON_GREEN,
        "textSeparator.foreground": NEON_GREEN_DIM,
        "focusBorder": NEON_GREEN,
        "foreground": GREEN_TEXT,
        "errorForeground": "#ff5577",
    },
    "tokenColors": [
        {"name": "Comments", "scope": ["comment", "punctuation.definition.comment"],
         "settings": {"foreground": "#4d6d4d", "fontStyle": "italic"}},
        {"name": "Strings", "scope": ["string", "string.quoted"],
         "settings": {"foreground": "#80ffaa"}},
        {"name": "Keywords", "scope": ["keyword", "storage.type", "storage.modifier"],
         "settings": {"foreground": NEON_GREEN, "fontStyle": "bold"}},
        {"name": "Functions", "scope": ["entity.name.function", "support.function"],
         "settings": {"foreground": "#00ffaa"}},
        {"name": "Variables", "scope": ["variable", "variable.other"],
         "settings": {"foreground": GREEN_TEXT}},
        {"name": "Numbers", "scope": ["constant.numeric"],
         "settings": {"foreground": "#ffe066"}},
        {"name": "Classes", "scope": ["entity.name.class", "support.class"],
         "settings": {"foreground": PURPLE_BRIGHT, "fontStyle": "bold"}},
        {"name": "Constants", "scope": ["constant", "constant.other"],
         "settings": {"foreground": "#ffaa55"}},
        {"name": "Operators", "scope": ["keyword.operator"],
         "settings": {"foreground": NEON_GREEN_SOFT}},
        {"name": "Punctuation", "scope": ["punctuation"],
         "settings": {"foreground": GREEN_TEXT}},
        {"name": "HTML Tags", "scope": ["entity.name.tag"],
         "settings": {"foreground": NEON_GREEN}},
        {"name": "CSS Properties", "scope": ["support.type.property-name.css"],
         "settings": {"foreground": "#80ffaa"}},
        {"name": "CSS Values", "scope": ["support.constant.property-value.css"],
         "settings": {"foreground": "#ffe066"}},
        {"name": "JSON Keys", "scope": ["support.type.property-name.json"],
         "settings": {"foreground": NEON_GREEN}},
        {"name": "JSON Values", "scope": ["meta.structure.dictionary.json"],
         "settings": {"foreground": "#80ffaa"}},
        {"name": "JavaScript Keywords", "scope": ["keyword.control", "keyword.operator.logical"],
         "settings": {"foreground": NEON_GREEN, "fontStyle": "bold"}},
        {"name": "TypeScript Types", "scope": ["support.type.primitive", "entity.name.type"],
         "settings": {"foreground": PURPLE, "fontStyle": "italic"}},
        {"name": "Regular Expressions", "scope": ["string.regexp"],
         "settings": {"foreground": "#ffaa55"}},
        {"name": "Template Literals", "scope": ["string.template"],
         "settings": {"foreground": "#80ffaa"}},
        {"name": "Import/Export", "scope": ["keyword.control.import", "keyword.control.export"],
         "settings": {"foreground": NEON_GREEN, "fontStyle": "bold"}},
    ],
}


# ---------- Install --------------------------------------------------------

def install():
    settings_path, extensions_root = get_vscode_paths()
    print(f"Extensions folder: {extensions_root}")

    ext_dir = os.path.join(extensions_root, EXTENSION_FOLDER)
    themes_dir = os.path.join(ext_dir, "themes")

    if os.path.isdir(ext_dir):
        print(f"Removing existing folder: {ext_dir}")
        shutil.rmtree(ext_dir)

    os.makedirs(themes_dir, exist_ok=True)

    pkg_path = os.path.join(ext_dir, "package.json")
    with open(pkg_path, "w", encoding="utf-8") as f:
        json.dump(PACKAGE_JSON, f, indent=2)
    print(f"Wrote {pkg_path}")

    theme_path = os.path.join(themes_dir, "neon-green-liquid-glass.json")
    with open(theme_path, "w", encoding="utf-8") as f:
        json.dump(THEME_JSON, f, indent=2)
    print(f"Wrote {theme_path}")

    print("\nDone.")
    print(f"1. Reload VSCode: Ctrl+Shift+P -> 'Developer: Reload Window'")
    print(f"2. Pick the theme: Ctrl+K Ctrl+T -> '{THEME_NAME}'")


if __name__ == "__main__":
    install()
