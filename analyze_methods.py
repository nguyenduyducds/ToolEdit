"""Script to further split UI/main_window.py into smaller modules"""

import re

def extract_methods_by_category():
    """Extract and categorize methods from main_window.py"""
    
    with open('UI/main_window.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all method definitions
    method_pattern = r'    def (\w+)\(self.*?\):'
    methods = re.findall(method_pattern, content)
    
    print(f"📊 Tìm thấy {len(methods)} methods")
    
    # Categorize methods
    video_processing_methods = [
        'process_video', 'process_all_videos', 'process_video_with_ffmpeg',
        'generate_subtitles_whisper', 'generate_subtitles',
        'load_speech_recognizer', 'edit_video'
    ]
    
    ui_setup_methods = [
        'setup_ui', 'setup_edit_video_tab', 'create_settings_panel',
        'create_console_panel', 'create_slider', 'create_path_selector',
        'create_dropdown'
    ]
    
    file_management_methods = [
        'browse_input_dir', 'browse_output_dir', 'browse_video_files',
        'browse_intro_video', 'browse_outro_video', 'on_drop',
        'add_video_to_tree', 'remove_selected_videos', 'remove_all_videos',
        'load_existing_videos', 'refresh_video_list'
    ]
    
    console_methods = [
        'log_console', 'update_video_status', 'show_brief_notification'
    ]
    
    # Count methods in each category
    print(f"\n📁 Phân loại methods:")
    print(f"  🎬 Video Processing: {len([m for m in methods if m in video_processing_methods])} methods")
    print(f"  🎨 UI Setup: {len([m for m in methods if m in ui_setup_methods])} methods")
    print(f"  📂 File Management: {len([m for m in methods if m in file_management_methods])} methods")
    print(f"  📝 Console: {len([m for m in methods if m in console_methods])} methods")
    print(f"  ❓ Other: {len(methods) - len([m for m in methods if m in video_processing_methods + ui_setup_methods + file_management_methods + console_methods])} methods")

if __name__ == "__main__":
    extract_methods_by_category()
