from PIL import Image, ImageDraw


def draw_tiled_images(canvas_width, canvas_height, tiles, images_per_tile, multiplier=150):
    size = (canvas_width * multiplier, canvas_height * multiplier)
    res = Image.new("RGBA", size)
    for tile_index, image  in images_per_tile:
        img = Image.open(image)
        img = img.resize((tiles[tile_index][2] * multiplier, tiles[tile_index][3] * multiplier))
        res.paste(img, (tiles[tile_index][0] * multiplier, tiles[tile_index][1] * multiplier))
    res.show()


if __name__ == '__main__':
    draw_tiled_images(
        30, 40,
        [(0, 0, 6, 8), (6, 0, 4, 4), (0, 8, 8, 6), (6, 4, 6, 4), (10, 0, 6, 4), (0, 14, 6, 8), (8, 8, 6, 6), (12, 4, 4, 4), (16, 0, 6, 8), (6, 14, 6, 4), (14, 8, 8, 6), (22, 0, 8, 6), (0, 22, 4, 4), (6, 18, 4, 4), (4, 22, 6, 6), (12, 14, 4, 4), (0, 26, 4, 6), (10, 18, 8, 6), (22, 6, 4, 4), (16, 14, 6, 4), (4, 28, 6, 8), (22, 10, 4, 6), (26, 6, 4, 6), (0, 32, 4, 4), (10, 24, 4, 4), (18, 18, 4, 4), (0, 36, 6, 4), (10, 28, 4, 6), (14, 24, 4, 6), (22, 16, 8, 6), (26, 12, 4, 4), (18, 22, 6, 4), (6, 36, 4, 4), (10, 34, 8, 6), (14, 30, 4, 4), (18, 26, 6, 8), (24, 22, 6, 8), (18, 34, 6, 6), (24, 30, 6, 6), (24, 36, 6, 4)],
        [],
        100
    )
