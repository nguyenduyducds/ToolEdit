"""
Text Outro Preview - Realtime preview generator
"""

from PIL import Image, ImageDraw, ImageFont
import os


def generate_text_outro_preview(
    text,
    width=400,
    height=600,
    font_size=30,
    font_color="white",
    bg_color="black",
    position="center",
    draw_box=False,
    box_padding=20,
    font_name="Arial (Mặc định)"
):
    """
    Generate a preview image of text outro
    """
    try:
        # Create image (RGBA for transparency support)
        # Background logic for Preview:
        # If box is enabled, the main background should be transparent or a placeholder video bg.
        # But for visibility, let's keep it dark gray or checkered if transparent.
        
        main_bg_color = (0, 0, 0, 255) # Default black opaque
        
        if bg_color == "transparent":
            main_bg_color = (50, 50, 50, 255) # Placeholder gray
        elif bg_color == "black":
             main_bg_color = (0, 0, 0, 255)
        elif bg_color == "white":
             main_bg_color = (255, 255, 255, 255)
             
        # If user wants a BOX, the "Background" setting likely refers to the BOX color, 
        # not the full screen background (which is video).
        # So for preview, we simulate video background as Gray, and Box as bg_color.
        
        box_color_rgb = (0, 0, 0, 150) # Default semi-transparent black
        if draw_box:
             # Map bg_color to box color
             # Main background becomes Video Placeholder
             main_bg_color = (100, 100, 100, 255) 
             
             color_map = {
                'black': (0, 0, 0, 180),
                'white': (255, 255, 255, 180),
                'transparent': (0, 0, 0, 0),
                '#1a1a1a': (26, 26, 26, 200),
                '#333333': (51, 51, 51, 200)
             }
             box_color_rgb = color_map.get(bg_color, (0, 0, 0, 180))
        else:
             # No box, use bg_color as main background if it is not transparent
             if bg_color != 'transparent':
                 # Convert simple names to RGBA
                 pass # kept simplified logic for now
        
        img = Image.new('RGBA', (width, height), main_bg_color)
        draw = ImageDraw.Draw(img)
        
        # Load font
        try:
            # Map names to Windows Font Paths
            font_map = {
                "arial": "arial.ttf",
                "segoe ui": "segoeui.ttf", 
                "times new roman": "times.ttf",
                "tahoma": "tahoma.ttf",
                "verdana": "verdana.ttf",
                "impact": "impact.ttf"
            }
            
            font_file = "arial.ttf" # Default
            for key, fname in font_map.items():
                if key in font_name.lower():
                    font_file = fname
                    break
            
            # Try loading directly (if in system path) or from C:/Windows/Fonts
            try:
                font = ImageFont.truetype(font_file, font_size)
            except:
                font = ImageFont.truetype(f"C:/Windows/Fonts/{font_file}", font_size)
                
        except Exception as e:
            print(f"Font load error: {e}")
            font = ImageFont.load_default()
        
        # Convert text color
        color_map = {
            'white': (255, 255, 255, 255),
            'black': (0, 0, 0, 255),
            'red': (255, 0, 0, 255),
            'blue': (0, 0, 255, 255),
            'green': (0, 255, 0, 255),
            'yellow': (255, 255, 0, 255),
            'cyan': (0, 255, 255, 255),
            'magenta': (255, 0, 255, 255)
        }
        text_rgb = color_map.get(font_color, (255, 255, 255, 255))
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if position == "center":
            x = (width - text_width) // 2
            y = (height - text_height) // 2
        elif position == "top":
            x = (width - text_width) // 2
            y = int(height * 0.2)
        elif position == "bottom":
            x = (width - text_width) // 2
            y = int(height * 0.8) - text_height
        else:
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
        # Draw Box if enabled
        if draw_box:
            # Draw rectangle with padding
            # shape: [x0, y0, x1, y1]
            box_coords = [x - box_padding, y - box_padding, x + text_width + box_padding, y + text_height + box_padding]
            draw.rectangle(box_coords, fill=box_color_rgb)
        
        # Draw text
        draw.text((x, y), text, fill=text_rgb, font=font)
        
        return img
        
    except Exception as e:
        print(f"Preview generation error: {e}")
        # Return error image
        img = Image.new('RGB', (width, height), (50, 50, 50))
        draw = ImageDraw.Draw(img)
        draw.text((10, height//2), f"Error: {str(e)[:30]}", fill=(255, 0, 0))
        return img


# Test
if __name__ == "__main__":
    img = generate_text_outro_preview(
        text="Thanks for watching!\nSubscribe!",
        font_size=40,
        font_color="white",
        bg_color="black",
        position="center"
    )
    img.save("preview_test.png")
    print("✅ Preview saved: preview_test.png")
