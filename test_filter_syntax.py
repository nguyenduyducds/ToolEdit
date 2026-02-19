"""Test FFmpeg filter syntax for sticker + blur background"""

# Test case 1: Simple filter + Sticker
simple_filter = "scale=iw*1.0:ih*1.0"
has_complex = ';' in simple_filter or 'split[' in simple_filter
print(f"Test 1 - Simple filter: {simple_filter}")
print(f"  Has complex: {has_complex}")
print(f"  Expected: False")
print()

# Test case 2: Complex filter (blur background) + Sticker
complex_filter = "split[bg][fg];[bg]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=5.0:2.5[bg_blur];[fg]scale=720:1280:force_original_aspect_ratio=decrease[fg_sized];[bg_blur][fg_sized]overlay=(W-w)/2:(H-h)/2"
has_complex = ';' in complex_filter or 'split[' in complex_filter
print(f"Test 2 - Complex filter (blur bg): {complex_filter[:80]}...")
print(f"  Has complex: {has_complex}")
print(f"  Expected: True")
print()

# Simulate sticker addition
s_pct = 0.2
x_expr = "W-w-20"
y_expr = "H-h-20"

if has_complex:
    # Append to complex filter
    result = f"{complex_filter}[v_main];[1:v][v_main]scale2ref=w=iw*{s_pct}:h=-1[stk][bg];[bg][stk]overlay={x_expr}:{y_expr}"
    print("Result (complex + sticker):")
    print(f"  {result[:100]}...")
    print()
    
    # Check syntax
    parts = result.split(';')
    print(f"Filter has {len(parts)} parts (should be 4):")
    for i, part in enumerate(parts):
        print(f"  Part {i+1}: {part[:60]}...")
    print()

# Test case 3: No filter + Sticker
no_filter = None
has_complex = no_filter and (';' in no_filter or 'split[' in no_filter)
print(f"Test 3 - No filter + Sticker")
print(f"  Has complex: {has_complex}")
print(f"  Expected: False")

if not has_complex and not no_filter:
    result = f"[1:v][0:v]scale2ref=w=iw*{s_pct}:h=-1[stk][bg];[bg][stk]overlay={x_expr}:{y_expr}"
    print(f"  Result: {result}")
    print()

print("✅ All tests completed!")
