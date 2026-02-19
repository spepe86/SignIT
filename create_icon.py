"""
Erstellt ein Platzhalter-Icon für Let's Do. | SignIT.
Erzeugt eine einfache .ico-Datei mit einem Schloss-Symbol.
"""

import struct
import os


def create_ico(filepath: str) -> None:
    """Erstellt ein minimales 32x32 ICO mit einem einfachen Design."""
    width = 32
    height = 32
    bpp = 32  # bits per pixel (BGRA)

    # Pixel-Daten (BGRA, bottom-up)
    pixels = bytearray()

    # Farben
    bg = (30, 26, 46, 255)  # Dunkles Lila #1e1a2e
    accent = (59, 130, 246, 255)  # Blau #3b82f6
    green = (74, 222, 128, 255)  # Grün #4ade80
    white = (255, 255, 255, 255)
    transparent = (0, 0, 0, 0)

    # Pixel als 2D-Array (top-down, wird dann umgekehrt)
    img = [[bg for _ in range(width)] for _ in range(height)]

    # Hintergrund: abgerundetes Quadrat
    for y in range(height):
        for x in range(width):
            # Abgerundete Ecken (Radius 4)
            r = 4
            if (
                (x < r and y < r and (x - r) ** 2 + (y - r) ** 2 > r**2)
                or (
                    x >= width - r
                    and y < r
                    and (x - width + r + 1) ** 2 + (y - r) ** 2 > r**2
                )
                or (
                    x < r
                    and y >= height - r
                    and (x - r) ** 2 + (y - height + r + 1) ** 2 > r**2
                )
                or (
                    x >= width - r
                    and y >= height - r
                    and (x - width + r + 1) ** 2 + (y - height + r + 1) ** 2 > r**2
                )
            ):
                img[y][x] = transparent
            elif x < 1 or x >= width - 1 or y < 1 or y >= height - 1:
                img[y][x] = accent  # Rand
            else:
                img[y][x] = bg

    # "S" Buchstabe zeichnen (SignIT)
    s_pixels = [
        "..XXXXX..",
        ".XX...XX.",
        ".XX......",
        ".XX......",
        "..XXXXX..",
        "......XX.",
        "......XX.",
        ".XX...XX.",
        "..XXXXX..",
    ]

    start_x = 8
    start_y = 5
    for row_idx, row in enumerate(s_pixels):
        for col_idx, ch in enumerate(row):
            if ch == "X":
                px = start_x + col_idx * 2
                py = start_y + row_idx * 2
                for dy in range(2):
                    for dx in range(2):
                        nx, ny = px + dx, py + dy
                        if 1 <= nx < width - 1 and 1 <= ny < height - 1:
                            img[ny][nx] = green

    # Kleiner Haken unten rechts
    for i in range(3):
        cx, cy = 24 + i, 26 - i
        if 1 <= cx < width - 1 and 1 <= cy < height - 1:
            img[cy][cx] = green
    for i in range(2):
        cx, cy = 22 + i, 24 + i
        if 1 <= cx < width - 1 and 1 <= cy < height - 1:
            img[cy][cx] = green

    # Bottom-up für BMP
    for y in range(height - 1, -1, -1):
        for x in range(width):
            b, g, r, a = img[y][x]
            pixels.extend([r, g, b, a])  # ICO ist BGRA

    # AND-Maske (1bpp, alle opak → Transparenz über Alpha)
    and_mask = bytearray()
    row_bytes = ((width + 31) // 32) * 4  # Auf 4 Bytes ausrichten
    for y in range(height):
        row = bytearray(row_bytes)
        for x in range(width):
            if img[height - 1 - y][x][3] == 0:
                byte_idx = x // 8
                bit_idx = 7 - (x % 8)
                row[byte_idx] |= 1 << bit_idx
        and_mask.extend(row)

    # BITMAPINFOHEADER
    bih = struct.pack(
        "<IiiHHIIiiII",
        40,  # biSize
        width,  # biWidth
        height * 2,  # biHeight (XOR + AND)
        1,  # biPlanes
        bpp,  # biBitCount
        0,  # biCompression
        len(pixels) + len(and_mask),  # biSizeImage
        0,
        0,  # biXPelsPerMeter, biYPelsPerMeter
        0,
        0,  # biClrUsed, biClrImportant
    )

    image_data = bih + bytes(pixels) + bytes(and_mask)

    # ICO Header
    ico_header = struct.pack("<HHH", 0, 1, 1)  # Reserved, Type(1=ICO), Count

    # ICO Directory Entry
    offset = 6 + 16  # Header + 1 Directory Entry
    ico_entry = struct.pack(
        "<BBBBHHII",
        width if width < 256 else 0,
        height if height < 256 else 0,
        0,  # Color palette
        0,  # Reserved
        1,  # Color planes
        bpp,  # Bits per pixel
        len(image_data),
        offset,
    )

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(ico_header)
        f.write(ico_entry)
        f.write(image_data)

    print(f"Icon erstellt: {filepath}")


if __name__ == "__main__":
    create_ico(os.path.join(os.path.dirname(__file__), "assets", "icon.ico"))
