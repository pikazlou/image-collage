$(document).ready(function(){

    var multiplier = 20;

    const can = document.getElementById('canvas');
    const ctx = can.getContext('2d');
    const can_rect = can.getBoundingClientRect();

    let tiles = [[0, 0, 5, 5], [5, 0, 3, 3], [8, 0, 4, 3], [5, 3, 4, 3], [9, 3, 3, 3], [12, 0, 3, 3], [0, 5, 5, 4], [5, 6, 3, 3], [12, 3, 3, 4], [0, 9, 4, 4], [4, 9, 4, 5], [8, 6, 4, 4], [12, 7, 3, 3], [8, 10, 3, 4], [11, 10, 4, 3], [11, 13, 4, 4], [0, 13, 4, 3], [4, 14, 3, 3], [0, 16, 4, 4], [7, 14, 4, 3], [4, 17, 4, 3], [8, 17, 3, 3], [11, 17, 4, 3]]
    draw_tiles(tiles, -1, multiplier, ctx);

    $('#canvas').click(function(e) {
        ctx.clearRect(0, 0, can.width, can.height);
        let mouse_x = e.clientX;
        let mouse_y = e.clientY;
        let selected_tile = find_selected_tile(mouse_x - can_rect.left, mouse_y - can_rect.top, tiles, multiplier);
        draw_tiles(tiles, selected_tile, multiplier, ctx);
    });
});

function draw_tiles(tiles, selected_tile, multiplier, canvas_ctx) {
    canvas_ctx.strokeStyle = '#ff0000';
    for (i in tiles) {
        draw_single_tile(tiles[i], multiplier, canvas_ctx)
    }

    canvas_ctx.strokeStyle = '#00ff00';
    if (selected_tile >= 0) {
        draw_single_tile(tiles[selected_tile], multiplier, canvas_ctx)
    }
}

function draw_single_tile(tile, multiplier, ctx) {
    let x = tile[0];
    let y = tile[1];
    let width = tile[2];
    let height = tile[3];

    ctx.beginPath();
    ctx.moveTo(x * multiplier, y * multiplier);
    ctx.lineTo((x + width) * multiplier, y * multiplier);
    ctx.lineTo((x + width) * multiplier, (y + height) * multiplier);
    ctx.lineTo(x * multiplier, (y + height) * multiplier);
    ctx.lineTo(x * multiplier, y * multiplier);
    ctx.closePath();
    ctx.stroke();
}

function find_selected_tile(event_x, event_y, tiles, multiplier) {
    for (i in tiles) {
        let tile = tiles[i];
        let x = tile[0];
        let y = tile[1];
        let width = tile[2];
        let height = tile[3];
        if ((x * multiplier <= event_x) && (event_x < (x + width) * multiplier) &&
            (y * multiplier <= event_y) && (event_y < (y + height) * multiplier)) {
            return i;
        }
    }
    return -1;
}