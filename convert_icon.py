"""
Convert PNG logo to ICO format for Windows executable.
"""
from PIL import Image

# Open the PNG logo
img = Image.open('app_logo.png')

# Define icon sizes (Windows expects multiple sizes in .ico)
icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

# Save as .ico with multiple sizes
img.save('app_icon.ico', format='ICO', sizes=icon_sizes)

print("✓ Icon created successfully!")
print("  Sizes included: 256x256, 128x128, 64x64, 48x48, 32x32, 16x16")
print("  File: app_icon.ico")
