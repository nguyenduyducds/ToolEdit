"""Test the new filter chain logic with pre-filters"""

# Simulate the scenario
filters = []

# Add some pre-filters (like scale, brightness, etc.)
filters.append("scale=iw*0.6:ih*1.4")
filters.append("eq=brightness=0.2")
filters.append("hflip")

print("Pre-filters:")
for i, f in enumerate(filters):
    print(f"  {i+1}. {f}")
print()

# Now apply blur background logic
target_w, target_h = 720, 1280
blur_amount = 5.674418604651162

# Build pre-filter chain
pre_filters = ','.join(filters) if filters else None
print(f"Pre-filter chain: {pre_filters}\n")

b_val = blur_amount

if pre_filters:
    # Apply pre-filters first, then split
    complex_part = (
        f"[0:v]{pre_filters}[pre];"
        f"[pre]split[bg][fg];"
        f"[bg]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},boxblur={b_val*2}:{b_val}[bg_blur];"
        f"[fg]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease[fg_sized];"
        f"[bg_blur][fg_sized]overlay=(W-w)/2:(H-h)/2"
    )
else:
    # No pre-filters, just split directly
    complex_part = (
        f"split[bg][fg];"
        f"[bg]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},boxblur={b_val*2}:{b_val}[bg_blur];"
        f"[fg]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease[fg_sized];"
        f"[bg_blur][fg_sized]overlay=(W-w)/2:(H-h)/2"
    )

# Clear filters list and replace with complex part
filters = [complex_part]

print("Final filter chain:")
print(filters[0])
print()

# Check structure
parts = filters[0].split(';')
print(f"Filter has {len(parts)} parts:")
for i, part in enumerate(parts):
    print(f"  Part {i+1}: {part[:80]}...")
print()

# Now test adding sticker
print("Adding sticker...")
vf = filters[0]
has_complex_filter = vf and (';' in vf or 'split[' in vf)
print(f"Has complex filter: {has_complex_filter}")

s_pct = 0.2
x_expr = "W-w-20"
y_expr = "H-h-20"

if has_complex_filter:
    vf = f"{vf}[v_main];[1:v][v_main]scale2ref=w=iw*{s_pct}:h=-1[stk][bg];[bg][stk]overlay={x_expr}:{y_expr}"

print("\nFinal with sticker:")
parts = vf.split(';')
print(f"Filter has {len(parts)} parts:")
for i, part in enumerate(parts):
    print(f"  Part {i+1}: {part[:80]}...")

print("\n✅ Test completed!")
