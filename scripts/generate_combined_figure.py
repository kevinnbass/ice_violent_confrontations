"""
Combine the county map and pie chart into a single stacked figure.
Map on top, pie chart on bottom, scaled to match widths.
"""
from PIL import Image

# Load the two images
map_img = Image.open('non_immigrant_incident_map_county_filtered.png')
pie_img = Image.open('non_immigrant_pie_charts.png')

print(f"Map dimensions: {map_img.size}")
print(f"Pie chart dimensions: {pie_img.size}")

# Determine target width (use the larger width)
target_width = max(map_img.width, pie_img.width)

# Scale images to match target width while preserving aspect ratio
def scale_to_width(img, target_w):
    if img.width == target_w:
        return img
    ratio = target_w / img.width
    new_height = int(img.height * ratio)
    return img.resize((target_w, new_height), Image.LANCZOS)

map_scaled = scale_to_width(map_img, target_width)
pie_scaled = scale_to_width(pie_img, target_width)

print(f"Map scaled: {map_scaled.size}")
print(f"Pie scaled: {pie_scaled.size}")

# Create combined image (stack vertically)
combined_height = map_scaled.height + pie_scaled.height
combined = Image.new('RGB', (target_width, combined_height), 'white')

# Paste map on top
combined.paste(map_scaled, (0, 0))

# Paste pie chart below
combined.paste(pie_scaled, (0, map_scaled.height))

# Save
combined.save('non_immigrant_combined.png', dpi=(150, 150))
print(f"\nCombined figure saved: non_immigrant_combined.png")
print(f"Final dimensions: {combined.size}")
