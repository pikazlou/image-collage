var tiles;
var used_tile_idx;
var selected_tile;
const multiplier = 20;

$(document).ready(function(){

    var canv;
    var ctx;
    var canv_rect;

    $.ajax('/current', {
        method: 'GET',
        success: function (data) {
            var json = $.parseJSON(data);
            tiles = json['tiles'];
            used_tile_idx = json['used_tile_idx'];
            $('#canvas').css("background-image", "url(" + json['canvas_url'] + ")");

            canv = document.getElementById('canvas');
            ctx = canv.getContext('2d');
            canv_rect = canv.getBoundingClientRect();

            draw_tiles(tiles, -1, multiplier, ctx);
        },

        error: function () {

        },
    });

    $('#canvas').click(function(e) {
        ctx.clearRect(0, 0, canv.width, canv.height);
        let mouse_x = e.clientX;
        let mouse_y = e.clientY;
        selected_tile = find_selected_tile(mouse_x - canv_rect.left, mouse_y - canv_rect.top, tiles, multiplier);
        if (selected_tile >= 0) {
            $('#select_file_button').show();
        }
        draw_tiles(tiles, selected_tile, multiplier, ctx);
    });
});

function draw_tiles(tiles, selected_tile, multiplier, canvas_ctx) {
    canvas_ctx.strokeStyle = '#ff0000';
    canvas_ctx.lineWidth = 1;
    for (i in tiles) {
        draw_single_tile(tiles[i], multiplier, canvas_ctx)
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
            !used_tile_idx.includes(i)) {
            return i;
        }
    }
    return -1;
}


window.addEventListener('DOMContentLoaded', function () {
  //var avatar = document.getElementById('avatar');
  var image = document.getElementById('image');
  var input = document.getElementById('input');
  var $progress = $('.progress');
  var $progressBar = $('.progress-bar');
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
    cropper = new Cropper(image, {
      aspectRatio: aspectRatio,
      viewMode: 2,
    });
  }).on('hidden.bs.modal', function () {
    cropper.destroy();
    cropper = null;
  });

  document.getElementById('crop').addEventListener('click', function () {
    //var initialAvatarURL;
    var canvas;

    $modal.modal('hide');

    if (cropper) {
      canvas = cropper.getCroppedCanvas({
        //width: 160,
        //height: 160,
      });
      //initialAvatarURL = avatar.src;
      //avatar.src = canvas.toDataURL();
      $progress.show();
      $alert.removeClass('alert-success alert-warning');
      canvas.toBlob(function (blob) {
        var formData = new FormData();

        formData.append('file', blob, 'upload.jpg');
        formData.append('selected_tile', selected_tile);
        $.ajax('/upload', {
          method: 'POST',
          data: formData,
          processData: false,
          contentType: false,

          xhr: function () {
            var xhr = new XMLHttpRequest();

            xhr.upload.onprogress = function (e) {
              var percent = '0';
              var percentage = '0%';

              if (e.lengthComputable) {
                percent = Math.round((e.loaded / e.total) * 100);
                percentage = percent + '%';
                $progressBar.width(percentage).attr('aria-valuenow', percent).text(percentage);
              }
            };

            return xhr;
          },

          success: function (data) {
            $alert.show().addClass('alert-success').text('Upload success');
            var json = $.parseJSON(data);
            $('#canvas').css("background-image", "url(" + json['canvas_url'] + ")");
          },

          error: function () {
            //avatar.src = initialAvatarURL;
            $alert.show().addClass('alert-warning').text('Upload error');
          },

          complete: function () {
            $progress.hide();
          },
        });
      });
    }
  });
});