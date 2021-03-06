import re
import base64
import os
import itertools
import string

import cv2
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import scipy.signal as signal

from PIL import Image

input_folder = "chr"
misc_folder = "misc"
output_folder = "out"


def monika():
    # Open file image file
    img = Image.open(f"{input_folder}/monika.chr")
    # Crop to binary data
    img = img.crop(box=(330, 330, 470, 470))
    imgdata = np.asarray(img)

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
    open(f"{output_folder}/monika.txt", "wb").write(output)


def natsuki():
    # Open the image file
    img = cv2.imread(f"{input_folder}/natsuki.chr")
    # Rotate it to the left since cv2 use the left has the center
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # Inverse the polar coordinates
    img = cv2.linearPolar(
        img, (img.shape[1] / 2, img.shape[0] / 2), 360, cv2.WARP_INVERSE_MAP)
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # Inverse the colors
    img = ~img
    cv2.imwrite(f"{output_folder}/natsuki.jpeg", img)


def yuri():
    # Open the text file
    str = open(f"{input_folder}/yuri.chr").read()
    # Decode the base64 text
    b = base64.b64decode(str)
    # Write it in a file
    open(f"{output_folder}/yuri.txt", "wb").write(b)


def sayori():
    # Open the audio file
    data, rate = sf.read(f"{input_folder}/sayori.chr")
    # Create the spectrogram of the audio file
    f, t, Sxx = signal.spectrogram(data, rate, window=signal.get_window(
        "hann", 2**12), noverlap=2**12 - 2**10)
    # Plot it in a figure
    plt.figure(figsize=(6, 6))
    plt.pcolormesh(t, f, Sxx, cmap="Greys", shading="gouraud")
    # Take only the frequencies between 9200 and 23000
    plt.ylim(9200, 23000)
    plt.yscale("log")
    plt.axis("off")
    # Save it
    plt.savefig(f"{output_folder}/sayori.png", bbox_inches="tight")

    # Post processing
    img = cv2.imread(f"{output_folder}/sayori.png", 0)
    # Fill the holes
    kernel = np.ones((10, 10), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    # Thresholding
    retval, img = cv2.threshold(img, 127, 255, type=cv2.THRESH_OTSU)
    # Write back the image
    cv2.imwrite(f"{output_folder}/sayori.png", img)

    # Read the qr code
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(img)
    # Save the data into a file
    open(f"{output_folder}/sayori.txt", "w+").write(data)


def have_a_nice_weekend():
    # Loading the file
    str = open("misc/have a nice weekend").read()

    # creating a inverse vigenere lookup table
    # format : m = inverse_tabula_recta[(k, c)]
    alphabet = string.ascii_lowercase
    grid = list(itertools.product(alphabet, repeat=2))
    inverse_tabula_recta = {}
    for cell in grid:
        index = (alphabet.index(cell[1]) - alphabet.index(cell[0]))
        inverse_tabula_recta[cell] = alphabet[index % len(alphabet)]

    # Using libitina as the vigenere's key (see sayori.chr)
    key = "libitina"
    cipher = str

    # Special vigenere lookup
    msg = ""
    index_key = 0
    index_cipher = 0
    while index_cipher < len(cipher):
        k = key[index_key % len(key)]
        c = cipher[index_cipher]

        # Keep the case
        if c in string.ascii_lowercase:
            m = inverse_tabula_recta[(k, c)]
            index_key += 1
        elif c in string.ascii_uppercase:
            m = inverse_tabula_recta[(k, c.lower())].upper()
            index_key += 1
        # Skip the non-literal
        else:
            m = c
        index_cipher += 1
        msg += m

    # Convert the output from b64 to bytes strings can be read in utf-8 / ascii
    open(f"{output_folder}/have a nice weekend.txt",
         "wb+").write(base64.b64decode(msg))


def natsuki_poem():
    # Open the text file
    str = open(f"{misc_folder}/natsuki_poem.txt").read()

    lines = str.split("\n")
    title = lines[0]
    text = "".join(lines[1:])
    # Decode the base64 text
    title = base64.b64decode(title)
    text = base64.b64decode(text)
    # Write it in a file
    with open(f"{output_folder}/natsuki_poem.txt", "wb") as file:
        file.write(title)
        file.write(b"\n")
        file.write(text)


if __name__ == "__main__":
    try:
        print(f"Creating '{output_folder}' folder.")
        os.mkdir(f"{output_folder}")
    except FileExistsError:
        print(f"'{output_folder}' folder already exist !")

    print(f"Using '{output_folder}' folder for outputs.")

    print("Decrypting monika.chr")
    monika()
    print("Decrypting natsuki.chr")
    natsuki()
    print("Decrypting yuri.chr")
    yuri()
    print("Decrypting sayori.chr")
    sayori()
    print("Decrypting have a nice weekend")
    have_a_nice_weekend()
    print("Decrypting natsuki_poem")
    natsuki_poem()
