import numpy as np
import random
from PIL import Image, ImageDraw


def partition(n, numbers):
    """
    Checks whethen number n can be represented as a sum of numbers. Numbers can be repeated.
    :param n: number to represent as sum
    :param numbers: numbers allowed to be used in sum
    :return: empty list if n can't be represented as sum of numbers, otherwise actual list of numbers
    """
    for i in numbers:
        if n == i:
            return [i]
        elif n > i:
            subpartition = partition(n-i, numbers)
            if subpartition:
                return subpartition + [i]
    return []


def try_layout(width, height, tiles):
    """
    tries to perfectly lay rectangle tiles to cover rectangle width x height
    :param width: width of rectangle to cover with tiles
    :param height: height of rectangle to cover with tiles
    :param tiles: 2-tuples describing width and height of each rectangle tile
    :return: empty list if haven't managed to lay tiles, otherwise list of 4-tuples, each tuple represents tile and its position: (x, y, width, height)
    """

    tile_widths = set([t[0] for t in tiles])
    tile_heights = set([t[1] for t in tiles])

    def inner(matrix, accum):
        if len(accum) == 1:
            print(accum)
        cols, rows = np.where(matrix < 0)
        if cols.size == 0:
            return accum
        else:
            diff_x = np.diff(matrix, axis=0)
            diff_y = np.diff(matrix, axis=1)
            cand_xx, cand_xy = np.where(diff_x < -100)
            cand_yx, cand_yy = np.where(diff_y < -100)
            candidate_points = np.append(np.dstack((cand_xx + 1, cand_xy))[0], np.dstack((cand_yx, cand_yy + 1))[0], axis=0)
            if candidate_points.size > 0:
                best_choice = (1000, 1000)
                for _x, _y in candidate_points:
                    if _x + _y < best_choice[0] + best_choice[1]:
                        best_choice = (_x, _y)
                x, y = best_choice
            else:
                x = 0
                y = 0

            restrictions = []
            if x > 0:
                restrictions.append(tiles[int(matrix[x-1, y]) - 1])
            if y > 0:
                restrictions.append(tiles[int(matrix[x, y-1]) - 1])

            shuffled_tiles = [t for t in tiles if t not in restrictions]
            random.shuffle(shuffled_tiles)
            for t in shuffled_tiles:
                x_with_tile = x + t[0]
                y_with_tile = y + t[1]
                if (x_with_tile <= width) and (y_with_tile <= height) and \
                        ((x_with_tile == width) or partition(width - x_with_tile, tile_widths)) and \
                        ((y_with_tile == height) or partition(height - y_with_tile, tile_heights)) and \
                        (matrix[x:x_with_tile, y:y_with_tile] < 0).all():
                    new_matrix = np.copy(matrix)
                    new_matrix[x:x_with_tile, y:y_with_tile] = tiles.index(t) + 1
                    new_accum = list(accum)
                    new_accum.append((x, y, t[0], t[1]))
                    res = inner(new_matrix, new_accum)
                    if res:
                        return res

            return []

    m = np.zeros((width, height)) - 100
    return inner(m, [])


def display_tiles_console(tiles):
    chars = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    width = max([t[0] + t[2] for t in tiles])
    height = max([t[1] + t[3] for t in tiles])
    m = np.zeros((width, height), dtype=int)
    for i, t in enumerate(tiles):
        m[t[0]:t[0]+t[2], t[1]:t[1]+t[3]] = i
    for x in range(width):
        for y in range(height):
            print(chars[m[x, y]] + ' ', end="")
        print()


def display_tiles_pil(width, height, tiles):
    img = Image.new("RGBA", (2000, 2000))
    w_ratio = int(2000 / width)
    h_ratio = int(2000 / height)
    mult = min(w_ratio, h_ratio)
    draw = ImageDraw.Draw(img)
    for t in tiles:
        coords = [
            (t[0] * mult, t[1] * mult),
            ((t[0] + t[2]) * mult, t[1] * mult),
            ((t[0] + t[2]) * mult, (t[1] + t[3]) * mult),
            (t[0] * mult, (t[1] + t[3]) * mult),
            (t[0] * mult, t[1] * mult),
        ]
        draw.line(coords, fill="black", width=0)
    img.show()


if __name__ == '__main__':
    layout = try_layout(30, 40, [(4, 4), (4, 6), (6, 4), (6, 6), (6, 8), (8, 6)])
    print(layout)
    display_tiles_pil(30, 40, layout)
