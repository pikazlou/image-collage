var tiles;
var pixels_per_tile_unit;
var allowed_tile_indices;
var selected_tile;
var multiplier;

var canv;
var ctx;
var canv_rect;

var cropbox_too_small = false;
var code_is_valid = false;

$(document).ready(function(){

    $.ajax('/current', {
        method: 'GET',
        success: function (data) {
            var json = $.parseJSON(data);
            tiles = json['tiles'];
            pixels_per_tile_unit = json['pixels_per_tile_unit'];

            resize_canvas();

            allowed_tile_indices = json['allowed_tile_indices'];
            $('#canvas').css("background-image", "url(" + json['canvas_url'] + ")");

            canv = document.getElementById('canvas');
            ctx = canv.getContext('2d');
            canv_rect = canv.getBoundingClientRect();

            draw_tiles(tiles, -1, multiplier, ctx);

            $('.overlay').hide();
        },

        error: function () {

        },
    });

    $('#canvas').click(function(e) {
        $('.alert').hide();

        ctx.clearRect(0, 0, canv.width, canv.height);
        let mouse_x = e.clientX;
        let mouse_y = e.clientY;
        selected_tile = find_selected_tile(mouse_x - canv_rect.left, mouse_y - canv_rect.top, tiles, multiplier);
        if (selected_tile >= 0) {
            $('#select_file').show();
        } else {
            $('#select_file').hide();
        }
        draw_tiles(tiles, selected_tile, multiplier, ctx);
    });

    $('#code').bind('keypress', function (event) {
        var value = String.fromCharCode(event.which);
        var pattern = new RegExp(/[a-z]/i);
        return pattern.test(value);
    });

    $("#code").on("input", function() {
        let cur_val = $(this).val();
        if (cur_val.length == 8) {
            code_is_valid = true;
            $(this).removeClass('invalid_code_input').addClass('valid_code_input');
        } else {
            code_is_valid = false;
            $(this).removeClass('valid_code_input').addClass('invalid_code_input');
        }
        toggle_enabled_for_crop_button();
    });
});

function resize_canvas() {
    let max_tiles_width = 0;
    let max_tiles_height = 0;
    for(var i=0; i<tiles.length; i++) {
        let tile = tiles[i];
        if (max_tiles_width < tile[0] + tile[2]) {
            max_tiles_width = tile[0] + tile[2]
        }
        if (max_tiles_height < tile[1] + tile[3]) {
            max_tiles_height = tile[1] + tile[3]
        }
    }

    let width_pixels_per_unit = (window.innerWidth - 20) / max_tiles_width;
    let height_pixels_per_unit = (window.innerHeight - 100) / max_tiles_height;
    multiplier = Math.floor(Math.min(width_pixels_per_unit, height_pixels_per_unit));

    let canvas = $('#canvas')[0];
    canvas.width = multiplier * max_tiles_width;
    canvas.height = multiplier * max_tiles_height;
}

function draw_tiles(tiles, selected_tile, multiplier, canvas_ctx) {
    canvas_ctx.strokeStyle = '#ffffff';
    canvas_ctx.lineWidth = 2;
    for(var i=0; i<tiles.length; i++) {
        if (!allowed_tile_indices.includes(i)) {
            draw_single_tile(tiles[i], multiplier, canvas_ctx)
        }
    }

    canvas_ctx.strokeStyle = '#cc6666';
    canvas_ctx.lineWidth = 1;
    for(var i=0; i<tiles.length; i++) {
        if (allowed_tile_indices.includes(i)) {
            draw_single_tile(tiles[i], multiplier, canvas_ctx)
        }
    }

    if (selected_tile >= 0) {
        canvas_ctx.strokeStyle = '#00ff00';
        canvas_ctx.lineWidth = 5;
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
    for(var i=0; i<tiles.length; i++) {
        let tile = tiles[i];
        let x = tile[0];
        let y = tile[1];
        let width = tile[2];
        let height = tile[3];
        if ((x * multiplier <= event_x) && (event_x < (x + width) * multiplier) &&
            (y * multiplier <= event_y) && (event_y < (y + height) * multiplier) &&
            allowed_tile_indices.includes(i)) {
            return i;
        }
    }
    return -1;
}

function toggle_enabled_for_crop_button() {
    if (!cropbox_too_small && code_is_valid) {
        $('#crop').prop("disabled", false);
    } else {
        $('#crop').prop("disabled", true);
    }
}


window.addEventListener('DOMContentLoaded', function () {
  var image = document.getElementById('image');
  var input = document.getElementById('select_file_input');
  var $alert = $('.alert');
  var $modal = $('#modal');
  var cropper;

  $('[data-toggle="tooltip"]').tooltip();

  input.addEventListener('change', function (e) {
    var files = e.target.files;
    var done = function (url) {
      input.value = '';
      image.src = url;
      $alert.hide();
      $modal.modal('show');
    };
    var reader;
    var file;
    var url;

    if (files && files.length > 0) {
      file = files[0];

      if (URL) {
        done(URL.createObjectURL(file));
      } else if (FileReader) {
        reader = new FileReader();
        reader.onload = function (e) {
          done(reader.result);
        };
        reader.readAsDataURL(file);
      }
    }
  });

  $modal.on('shown.bs.modal', function () {
    let tile_width = tiles[selected_tile][2];
    let tile_height = tiles[selected_tile][3];
    let aspectRatio = 1.0 * tile_width / tile_height;
    let minCroppedWidth = tile_width * pixels_per_tile_unit;
    let minCroppedHeight = tile_height * pixels_per_tile_unit;
    var recursion = false;
    cropper = new Cropper(image, {
      aspectRatio: aspectRatio,
      viewMode: 2,
      zoomable: true,
      crop: function (event) {
          var width = Math.round(event.detail.width);
          var height = Math.round(event.detail.height);

          if (!recursion && (width < minCroppedWidth || height < minCroppedHeight)) {
            recursion = true;
            cropper.setData({
              width: minCroppedWidth,
              height: minCroppedHeight,
            });
          }

          recursion = false;

          let data = cropper.getData();
          if (Math.round(data.width) < minCroppedWidth || Math.round(data.height) < minCroppedHeight) {
            $('#modal_message').show();
            cropbox_too_small = true;
            toggle_enabled_for_crop_button();
          } else {
            $('#modal_message').hide();
            cropbox_too_small = false;
            toggle_enabled_for_crop_button();
          }
      }
    });
  }).on('hidden.bs.modal', function () {
    cropper.destroy();
    cropper = null;
  });

  document.getElementById('crop').addEventListener('click', function () {
    var canvas;

    $modal.modal('hide');

    if (cropper) {
      canvas = cropper.getCroppedCanvas({});
      $alert.removeClass('alert-success alert-warning');

      let code = $('#code').val();

      canvas.toBlob(function (blob) {
        var formData = new FormData();

        formData.append('file', blob, 'upload.jpg');
        formData.append('selected_tile', selected_tile);
        formData.append('code', code);

        $('.overlay').show();

        $.ajax('/upload', {
          method: 'POST',
          data: formData,
          processData: false,
          contentType: false,

          success: function (data) {
            $alert.show().addClass('alert-success').text('Запампавана паспяхова');
            var json = $.parseJSON(data);
            allowed_tile_indices = json['allowed_tile_indices'];
            $('#canvas').css("background-image", "url(" + json['canvas_url'] + ")");
            selected_tile = -1;
            $('#select_file').hide();
            ctx.clearRect(0, 0, canv.width, canv.height);
            draw_tiles(tiles, selected_tile, multiplier, ctx);
          },

          error: function (xhr, status, error) {
            let msg;
            try {
                msg = JSON.parse(xhr.responseText)['message'];
            } catch (e) {
                msg = 'Памылка';
            }
            $alert.show().addClass('alert-warning').text(msg);

            selected_tile = -1;
            $('#select_file').hide();
            ctx.clearRect(0, 0, canv.width, canv.height);
            draw_tiles(tiles, selected_tile, multiplier, ctx);
          },

          complete: function () {
            $('.overlay').hide();
          },
        });
      });
    }
  });
});