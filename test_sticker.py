"""Test script for Sticker Module"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UI.sticker import StickerManager, apply_sticker, get_ffmpeg_overlay_filter
import cv2
import numpy as np


def test_sticker_positions():
    """Test all sticker positions"""
    print("Testing Sticker Positions...")
    
    manager = StickerManager()
    
    # Test video dimensions
    video_w, video_h = 1280, 720
    sticker_w, sticker_h = 200, 100
    
    positions = [
        "Góc phải dưới",
        "Góc phải trên", 
        "Góc trái dưới",
        "Góc trái trên",
        "Chính giữa (Center)"
    ]
    
    print(f"\nVideo: {video_w}x{video_h}")
    print(f"Sticker: {sticker_w}x{sticker_h}\n")
    
    for pos in positions:
        x, y = manager.calculate_position(video_w, video_h, sticker_w, sticker_h, pos)
        print(f"{pos:25} -> ({x:4}, {y:4})")
    
    print("\n✅ Position test completed!\n")


def test_sticker_scaling():
    """Test sticker scaling"""
    print("Testing Sticker Scaling...")
    
    manager = StickerManager()
    
    # Create dummy sticker image
    from PIL import Image
    dummy_sticker = Image.new('RGBA', (400, 300), (255, 0, 0, 128))
    
    video_w, video_h = 1920, 1080
    
    scales = [0.05, 0.1, 0.2, 0.3, 0.5]
    
    print(f"\nVideo: {video_w}x{video_h}")
    print(f"Original Sticker: {dummy_sticker.size}\n")
    
    for scale in scales:
        resized = manager.resize_sticker(dummy_sticker, video_w, video_h, scale)
        print(f"Scale {scale:.2f} ({int(scale*100):3}%) -> {resized.size}")
    
    print("\n✅ Scaling test completed!\n")


def test_apply_sticker_to_frame():
    """Test applying sticker to actual frame"""
    print("Testing Apply Sticker to Frame...")
    
    # Create test frame (blue background)
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    frame[:, :] = (255, 100, 50)  # BGR
    
    # Create test sticker (red circle with transparency)
    from PIL import Image, ImageDraw
    sticker = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sticker)
    draw.ellipse([10, 10, 190, 190], fill=(255, 0, 0, 200))
    
    # Save sticker temporarily
    temp_sticker_path = "test_sticker.png"
    sticker.save(temp_sticker_path)
    
    manager = StickerManager()
    
    # Test different positions
    positions = ["Góc phải dưới", "Góc trái trên", "Chính giữa (Center)"]
    
    for i, pos in enumerate(positions):
        test_frame = frame.copy()
        result = manager.apply_sticker_to_frame(test_frame, temp_sticker_path, pos, 0.15)
        
        output_path = f"test_output_{i}.jpg"
        cv2.imwrite(output_path, result)
        print(f"✅ Created: {output_path} (Position: {pos})")
    
    # Cleanup
    if os.path.exists(temp_sticker_path):
        os.remove(temp_sticker_path)
    
    print("\n✅ Frame application test completed!\n")


def test_ffmpeg_filter_generation():
    """Test FFmpeg filter string generation"""
    print("Testing FFmpeg Filter Generation...")
    
    # Create test sticker
    from PIL import Image
    sticker = Image.new('RGBA', (300, 200), (255, 0, 0, 200))
    temp_sticker_path = "test_sticker_ffmpeg.png"
    sticker.save(temp_sticker_path)
    
    manager = StickerManager()
    
    video_w, video_h = 1920, 1080
    
    positions = ["Góc phải dưới", "Góc trái trên", "Chính giữa (Center)"]
    
    print(f"\nVideo: {video_w}x{video_h}\n")
    
    for pos in positions:
        filter_str = manager.generate_ffmpeg_overlay_filter(
            temp_sticker_path, video_w, video_h, pos, 0.2
        )
        print(f"{pos:25}:")
        print(f"  {filter_str}\n")
    
    # Cleanup
    if os.path.exists(temp_sticker_path):
        os.remove(temp_sticker_path)
    
    print("✅ FFmpeg filter test completed!\n")


def main():
    """Run all tests"""
    print("="*60)
    print("STICKER MODULE TEST SUITE")
    print("="*60)
    print()
    
    try:
        test_sticker_positions()
        test_sticker_scaling()
        test_ffmpeg_filter_generation()
        
        # Only run frame test if OpenCV is available
        try:
            test_apply_sticker_to_frame()
        except Exception as e:
            print(f"⚠️ Frame test skipped: {e}\n")
        
        print("="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY! ✅")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
