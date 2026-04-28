"""
VSCode Mystic Dark - Neon Noir Theme Installer
----------------------------------------------
Creates a self-contained local extension directly in VSCode's extensions folder.
No internet, no marketplace, no extension install permissions required.

Run: python setup_neon_noir_theme.py
Then reload VSCode (Ctrl+Shift+P -> "Reload Window") and pick the theme
via Ctrl+K Ctrl+T -> "Mystic Dark - Neon Noir".
"""

import json
import os
import platform
import shutil


# ---------- Paths ----------------------------------------------------------

def get_vscode_paths():
    system = platform.system()
    home = os.path.expanduser("~")

    # Check for portable VS Code installation (has a "data" folder next to Code.exe)
    portable_data = _find_portable_data_dir()
    if portable_data:
        settings = os.path.join(portable_data, "user-data", "User", "settings.json")
        extensions = os.path.join(portable_data, "extensions")
        return settings, extensions

    # Standard installation paths
    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
        settings = os.path.join(base, "Code", "User", "settings.json")
        extensions = os.path.join(home, ".vscode", "extensions")
    elif system == "Darwin":
        settings = os.path.join(home, "Library", "Application Support", "Code", "User", "settings.json")
        extensions = os.path.join(home, ".vscode", "extensions")
    else:  # Linux
        settings = os.path.join(home, ".config", "Code", "User", "settings.json")
        extensions = os.path.join(home, ".vscode", "extensions")
    return settings, extensions


def _find_portable_data_dir():
    """Locate a portable VS Code by looking for a running Code.exe with a sibling 'data' folder."""
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

EXTENSION_ID = "local.mystic-dark-neon-noir"
EXTENSION_VERSION = "1.0.0"
EXTENSION_FOLDER = f"{EXTENSION_ID}-{EXTENSION_VERSION}"
THEME_NAME = "Mystic Dark - Neon Noir"

PACKAGE_JSON = {
    "name": "mystic-dark-neon-noir",
    "displayName": "Mystic Dark - Neon Noir (Local)",
    "description": "Locally installed Mystic Dark Neon Noir theme.",
    "version": EXTENSION_VERSION,
    "publisher": "local",
    "engines": {"vscode": "^1.0.0"},
    "categories": ["Themes"],
    "contributes": {
        "themes": [
            {
                "label": THEME_NAME,
                "uiTheme": "vs-dark",
                "path": "./themes/neon-noir.json",
            }
        ]
    },
}

THEME_JSON = {
    "name": "Neon Noir",
    "type": "dark",
    "colors": {
        "activityBar.background": "#000000",
        "activityBar.foreground": "#00ffff",
        "activityBar.inactiveForeground": "#666666",
        "activityBarBadge.background": "#ff00ff",
        "activityBarBadge.foreground": "#000000",
        "sideBar.background": "#0a0a0a",
        "sideBar.foreground": "#e0e0e0",
        "sideBarTitle.foreground": "#00ffff",
        "sideBarSectionHeader.background": "#1a1a1a",
        "sideBarSectionHeader.foreground": "#ff00ff",
        "editor.background": "#000000",
        "editor.foreground": "#ffffff",
        "editor.lineHighlightBackground": "#1a1a1a",
        "editor.selectionBackground": "#2a2a2a",
        "editor.inactiveSelectionBackground": "#1a1a1a",
        "editorCursor.foreground": "#00ffff",
        "editorWhitespace.foreground": "#333333",
        "editorIndentGuide.background": "#1a1a1a",
        "editorIndentGuide.activeBackground": "#00ffff",
        "statusBar.background": "#1a1a1a",
        "statusBar.foreground": "#00ffff",
        "statusBar.debuggingBackground": "#ff00ff",
        "statusBar.debuggingForeground": "#000000",
        "titleBar.activeBackground": "#0a0a0a",
        "titleBar.activeForeground": "#00ffff",
        "titleBar.inactiveBackground": "#000000",
        "titleBar.inactiveForeground": "#666666",
        "editorGroupHeader.tabsBackground": "#000000",
        "editorGroupHeader.tabsBorder": "#1a1a1a",
        "editorGroupHeader.noTabsBackground": "#000000",
        "panel.background": "#0a0a0a",
        "panel.border": "#1a1a1a",
        "panelTitle.activeForeground": "#00ffff",
        "panelTitle.inactiveForeground": "#666666",
        "terminal.background": "#000000",
        "terminal.foreground": "#00ff00",
        "terminal.ansiBlack": "#000000",
        "terminal.ansiBlue": "#0080ff",
        "terminal.ansiCyan": "#00ffff",
        "terminal.ansiGreen": "#00ff00",
        "terminal.ansiMagenta": "#ff00ff",
        "terminal.ansiRed": "#ff0000",
        "terminal.ansiWhite": "#ffffff",
        "terminal.ansiYellow": "#ffff00",
        "terminal.ansiBrightBlack": "#666666",
        "terminal.ansiBrightBlue": "#0080ff",
        "terminal.ansiBrightCyan": "#00ffff",
        "terminal.ansiBrightGreen": "#00ff00",
        "terminal.ansiBrightMagenta": "#ff00ff",
        "terminal.ansiBrightRed": "#ff0000",
        "terminal.ansiBrightWhite": "#ffffff",
        "terminal.ansiBrightYellow": "#ffff00",
        "scrollbarSlider.background": "#2a2a2a",
        "scrollbarSlider.hoverBackground": "#00ffff",
        "scrollbarSlider.activeBackground": "#ff00ff",
        "input.background": "#1a1a1a",
        "input.foreground": "#ffffff",
        "input.border": "#00ffff",
        "input.placeholderForeground": "#666666",
        "dropdown.background": "#1a1a1a",
        "dropdown.foreground": "#ffffff",
        "dropdown.border": "#00ffff",
        "button.background": "#ff00ff",
        "button.foreground": "#000000",
        "button.hoverBackground": "#ff40ff",
        "tab.activeBackground": "#000000",
        "tab.activeForeground": "#00ffff",
        "tab.inactiveBackground": "#000000",
        "tab.inactiveForeground": "#666666",
        "tab.border": "#1a1a1a",
        "notification.background": "#1a1a1a",
        "notification.foreground": "#ffffff",
        "notification.border": "#00ffff",
        "progressBar.background": "#00ffff",
        "list.activeSelectionBackground": "#2a2a2a",
        "list.activeSelectionForeground": "#00ffff",
        "list.inactiveSelectionBackground": "#1a1a1a",
        "list.inactiveSelectionForeground": "#666666",
        "list.hoverBackground": "#1a1a1a",
        "list.hoverForeground": "#ffffff",
        "tree.indentGuidesStroke": "#1a1a1a",
        "diffEditor.insertedTextBackground": "#1a2a1a",
        "diffEditor.removedTextBackground": "#2a1a1a",
        "quickInput.background": "#000000",
        "quickInput.foreground": "#ffffff",
        "quickInputList.focusBackground": "#1a1a1a",
        "quickInputList.focusForeground": "#00ffff",
        "menu.background": "#000000",
        "menu.foreground": "#ffffff",
        "menu.selectionBackground": "#1a1a1a",
        "menu.selectionForeground": "#00ffff",
        "menubar.selectionBackground": "#1a1a1a",
        "menubar.selectionForeground": "#00ffff",
        "pickerGroup.background": "#000000",
        "pickerGroup.foreground": "#00ffff",
        "pickerGroup.border": "#1a1a1a",
        "editorSuggestWidget.background": "#000000",
        "editorSuggestWidget.border": "#1a1a1a",
        "editorSuggestWidget.selectedBackground": "#1a1a1a",
        "editorSuggestWidget.highlightForeground": "#00ffff",
        "editorHoverWidget.background": "#000000",
        "editorHoverWidget.border": "#1a1a1a",
        "debugToolBar.background": "#000000",
        "debugToolBar.border": "#1a1a1a",
        "editorWidget.background": "#000000",
        "editorWidget.border": "#1a1a1a",
        "peekView.border": "#00ffff",
        "peekViewEditor.background": "#000000",
        "peekViewResult.background": "#000000",
        "peekViewTitle.background": "#000000",
        "peekViewTitleLabel.foreground": "#00ffff",
        "peekViewTitleDescription.foreground": "#666666",
        "widget.shadow": "#00000080",
        "textBlockQuote.background": "#1a1a1a",
        "textBlockQuote.border": "#00ffff",
        "textCodeBlock.background": "#1a1a1a",
        "textLink.foreground": "#00ffff",
        "textLink.activeForeground": "#ff00ff",
        "textPreformat.foreground": "#00ff00",
        "textSeparator.foreground": "#1a1a1a",
    },
    "tokenColors": [
        {"name": "Comments", "scope": ["comment", "punctuation.definition.comment"],
         "settings": {"foreground": "#666666", "fontStyle": "italic"}},
        {"name": "Strings", "scope": ["string", "string.quoted"],
         "settings": {"foreground": "#00ff00"}},
        {"name": "Keywords", "scope": ["keyword", "storage.type", "storage.modifier"],
         "settings": {"foreground": "#ff00ff", "fontStyle": "bold"}},
        {"name": "Functions", "scope": ["entity.name.function", "support.function"],
         "settings": {"foreground": "#00ffff"}},
        {"name": "Variables", "scope": ["variable", "variable.other"],
         "settings": {"foreground": "#ffffff"}},
        {"name": "Numbers", "scope": ["constant.numeric"],
         "settings": {"foreground": "#ffff00"}},
        {"name": "Classes", "scope": ["entity.name.class", "support.class"],
         "settings": {"foreground": "#0080ff", "fontStyle": "bold"}},
        {"name": "Constants", "scope": ["constant", "constant.other"],
         "settings": {"foreground": "#ff8000"}},
        {"name": "Operators", "scope": ["keyword.operator"],
         "settings": {"foreground": "#00ffff"}},
        {"name": "Punctuation", "scope": ["punctuation"],
         "settings": {"foreground": "#e0e0e0"}},
        {"name": "HTML Tags", "scope": ["entity.name.tag"],
         "settings": {"foreground": "#00ffff"}},
        {"name": "CSS Properties", "scope": ["support.type.property-name.css"],
         "settings": {"foreground": "#0080ff"}},
        {"name": "CSS Values", "scope": ["support.constant.property-value.css"],
         "settings": {"foreground": "#ffff00"}},
        {"name": "JSON Keys", "scope": ["support.type.property-name.json"],
         "settings": {"foreground": "#ff00ff"}},
        {"name": "JSON Values", "scope": ["meta.structure.dictionary.json"],
         "settings": {"foreground": "#00ff00"}},
        {"name": "JavaScript Keywords", "scope": ["keyword.control", "keyword.operator.logical"],
         "settings": {"foreground": "#ff00ff", "fontStyle": "bold"}},
        {"name": "TypeScript Types", "scope": ["support.type.primitive", "entity.name.type"],
         "settings": {"foreground": "#0080ff", "fontStyle": "italic"}},
        {"name": "Regular Expressions", "scope": ["string.regexp"],
         "settings": {"foreground": "#ff8000"}},
        {"name": "Template Literals", "scope": ["string.template"],
         "settings": {"foreground": "#00ff00"}},
        {"name": "Import/Export", "scope": ["keyword.control.import", "keyword.control.export"],
         "settings": {"foreground": "#ff00ff", "fontStyle": "bold"}},
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

    theme_path = os.path.join(themes_dir, "neon-noir.json")
    with open(theme_path, "w", encoding="utf-8") as f:
        json.dump(THEME_JSON, f, indent=2)
    print(f"Wrote {theme_path}")

    print("\nDone.")
    print(f"1. Reload VSCode: Ctrl+Shift+P -> 'Developer: Reload Window'")
    print(f"2. Pick the theme: Ctrl+K Ctrl+T -> '{THEME_NAME}'")


if __name__ == "__main__":
    install()
