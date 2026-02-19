# Auto-fix script to wrap COLOR constants with get_color()
import re

file_path = r"c:\Users\Admin\Desktop\ToolEdit\ToolEdit\UI\main_window.py"

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Patterns to replace (excluding definitions and get_color calls)
# Updated: Use word boundary \b and negative lookahead for =
patterns = [
    (r'\bCOLOR_TEXT_PRIMARY\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_TEXT_PRIMARY)'),
    (r'\bCOLOR_TEXT_SECONDARY\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_TEXT_SECONDARY)'),
    (r'\bCOLOR_ACCENT\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_ACCENT)'),
    (r'\bCOLOR_BG_SECONDARY\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_BG_SECONDARY)'),
    (r'\bCOLOR_BG_PANEL\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_BG_PANEL)'),
    (r'\bCOLOR_BG_HEADER\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_BG_HEADER)'),
    (r'\bCOLOR_BUTTON_BG\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_BUTTON_BG)'),
    (r'\bCOLOR_ERROR\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_ERROR)'),
    (r'\bCOLOR_SUCCESS\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_SUCCESS)'),
    (r'\bCOLOR_WARNING\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_WARNING)'),
    (r'\bCOLOR_BORDER\b(?!\s*=)(?!.*get_color)', r'get_color(COLOR_BORDER)'),
]

# Apply replacements
for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all COLOR constants!")
