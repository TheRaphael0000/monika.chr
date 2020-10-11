import re
import base64

import cv2
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import scipy.signal as signal

from PIL import Image


def monika():
    # Open file image file
    img = Image.open("monika.chr")
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
    open("monika.txt", "wb").write(output)


def natsuki():
    # Open the image file
    img = cv2.imread("natsuki.chr")
    # Rotate it to the left since cv2 use the left has the center
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # Inverse the polar coordinates
    img = cv2.linearPolar(
        img, (img.shape[1] / 2, img.shape[0] / 2), 360, cv2.WARP_INVERSE_MAP)
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # Inverse the colors
    img = ~img
    cv2.imwrite("natsuki.jpeg", img)


def yuri():
    # Open the text file
    str = open("yuri.chr").read()
    # Decode the base64 text
    b = base64.b64decode(str)
    # Write it in a file
    open("yuri.txt", "wb").write(b)


def sayori():
    # Open the audio file
    data, rate = sf.read("sayori.chr")
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
    plt.savefig("sayori.png", bbox_inches="tight")

    # Post processing
    img = cv2.imread("sayori.png", 0)
    # Fill the holes
    kernel = np.ones((10, 10), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    # Thresholding
    retval, img = cv2.threshold(img, 127, 255, type=cv2.THRESH_OTSU)
    # Write back the image
    cv2.imwrite("sayori.png", img)

    # Read the qr code
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(img)
    # Save the data into a file
    open("sayori.txt", "w+").write(data)


if __name__ == "__main__":
    monika()
    natsuki()
    yuri()
    sayori()
