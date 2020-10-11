from PIL import Image
from numpy import asarray
import re
import base64

# Open file
img = Image.open("monika.chr")
# Crop to binary data
img = img.crop(box=(330, 330, 470, 470))
imgdata = asarray(img)

# browse the pixels
byte_str = ""
for x in range(140):
    for y in range(140):
        byte_str += "0" if imgdata[x, y, 0] == 0 else "1"

# Split to blocks of 8 bits
blocks = re.findall(".{8}", byte_str)
# Convert to bytes
blocks_bytes = [int(block, base=2) for block in blocks]
b = bytes(blocks_bytes)
# Decode the message from base64
output = base64.b64decode(b)
# Write it in a file
open("monika.txt", "w").write(output.decode("ascii"))
