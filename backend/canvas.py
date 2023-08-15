from PIL import Image, ImageDraw


def draw_tiled_images(canvas_width, canvas_height, tiles, images_per_tile, multiplier=50):
    size = (canvas_width * multiplier, canvas_height * multiplier)
    res = Image.new("RGBA", size)
    for tile_index, image  in images_per_tile:
        img = Image.open(image)
        img = img.resize((tiles[tile_index][2] * multiplier, tiles[tile_index][3] * multiplier))
        res.paste(img, (tiles[tile_index][0] * multiplier, tiles[tile_index][1] * multiplier))
    res.show()


if __name__ == '__main__':
    draw_tiled_images(
        15, 20,
        [(0, 0, 5, 5), (5, 0, 3, 3), (8, 0, 4, 3), (5, 3, 4, 3), (9, 3, 3, 3), (12, 0, 3, 3), (0, 5, 5, 4), (5, 6, 3, 3), (12, 3, 3, 4), (0, 9, 4, 4), (4, 9, 4, 5), (8, 6, 4, 4), (12, 7, 3, 3), (8, 10, 3, 4), (11, 10, 4, 3), (11, 13, 4, 4), (0, 13, 4, 3), (4, 14, 3, 3), (0, 16, 4, 4), (7, 14, 4, 3), (4, 17, 4, 3), (8, 17, 3, 3), (11, 17, 4, 3)],
        [(0, '/tmp/300.jpeg'), (1, '/tmp/320.jpeg'), (2, '/tmp/340.jpeg'), (3, '/tmp/350.jpeg'), (4, '/tmp/300.jpeg')]
    )
