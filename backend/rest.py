import os
import json
import sys
import time
import dataclasses
from dataclasses import dataclass
from typing import Any, List

from flask import Flask, request, send_from_directory, redirect
from waitress import serve
from PIL import Image
import boto3
import io

ALL_TILES = [[0, 0, 5, 5], [5, 0, 3, 3], [8, 0, 4, 3], [5, 3, 4, 3], [9, 3, 3, 3], [12, 0, 3, 3], [0, 5, 5, 4], [5, 6, 3, 3], [12, 3, 3, 4], [0, 9, 4, 4], [4, 9, 4, 5], [8, 6, 4, 4], [12, 7, 3, 3], [8, 10, 3, 4], [11, 10, 4, 3], [11, 13, 4, 4], [0, 13, 4, 3], [4, 14, 3, 3], [0, 16, 4, 4], [7, 14, 4, 3], [4, 17, 4, 3], [8, 17, 3, 3], [11, 17, 4, 3]]

app = Flask(__name__)


@app.route('/')
def root():
    return redirect('index.html')


@app.route('/<path:path>')
def serve_static(path):
    print(path)
    return send_from_directory('../site', path)


S3_BUCKET = 'belarus-image-collage'
S3_CANVAS_KEY = 'tiles.png'
S3_STATE_KEY = 'state.json'


CANVAS_BASE_URL = 'https://belarus-image-collage.s3.eu-central-1.amazonaws.com/tiles.png'


@dataclass(frozen=True)
class UsedTile:
    index: int
    code: str
    epoch_seconds: int


@dataclass(frozen=True)
class State:
    codes: List[str]
    used_tiles: List[UsedTile]

    @classmethod
    def from_dict(cls, d: dict[str, Any]):
        codes = d['codes']
        used_tiles = [UsedTile(obj['index'], obj['code'], obj['epoch_seconds']) for obj in d['used_tiles']]
        return State(codes, used_tiles)

    def used_tile_indices(self):
        return [tile.index for tile in self.used_tiles]

    def used_tile_by_index(self, index):
        return next((elem for elem in self.used_tiles if elem.index == index), None)

    def used_tile_by_code(self, code):
        return next((elem for elem in self.used_tiles if elem.code == code), None)


@app.route('/current', methods=['GET'])
def get_current_tiles():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    canvas_s3_resp = s3.list_object_versions(
        Bucket=S3_BUCKET,
        Prefix=S3_CANVAS_KEY
    )
    latest_version_id = next(ver['VersionId'] for ver in canvas_s3_resp['Versions'] if ver['IsLatest'])
    canvas_url = CANVAS_BASE_URL + '?versionId=' + latest_version_id

    state = get_state(s3)
    used_tile_indices = state.used_tile_indices()
    allowed_tile_indices = [i for i in range(len(ALL_TILES)) if i not in used_tile_indices]

    return json.dumps({'canvas_url': canvas_url, 'tiles': ALL_TILES, 'allowed_tile_indices': allowed_tile_indices})


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return json.dumps({'message': 'No file part'}), 400
    new_tile_file = request.files['file']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if new_tile_file.filename == '':
        return json.dumps({'message': 'No selected file'}), 400

    selected_tile = int(request.form['selected_tile'])
    code = request.form['code'].upper()

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    state = get_state(s3)
    current_epoch_seconds = int(time.time())

    used_tile_same_index = state.used_tile_by_index(selected_tile)
    if used_tile_same_index and (used_tile_same_index.code != code or current_epoch_seconds - used_tile_same_index.epoch_seconds > 3600):
        return json.dumps({'message': 'Tile has been populated already'}), 409

    used_tile_same_code = state.used_tile_by_code(code)
    if used_tile_same_code and (used_tile_same_code.index != selected_tile):
        return json.dumps({'message': 'Code has been used already'}), 409

    if code not in state.codes:
        return json.dumps({'message': 'Wrong code'}), 400

    resp = s3.get_object(
        Bucket=S3_BUCKET,
        Key=S3_CANVAS_KEY
    )
    canvas_file_stream = resp['Body']

    in_mem_file = apply_tile_to_canvas(new_tile_file.stream, canvas_file_stream, ALL_TILES[selected_tile])

    new_canvas_s3_resp = s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_CANVAS_KEY,
        Body=in_mem_file
    )
    canvas_url = CANVAS_BASE_URL + '?versionId=' + new_canvas_s3_resp['VersionId']

    if not used_tile_same_index:
        state.used_tiles.append(UsedTile(selected_tile, code, current_epoch_seconds))

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_STATE_KEY,
        Body=json.dumps(dataclasses.asdict(state))
    )

    used_tile_indices = state.used_tile_indices()
    allowed_tile_indices = [i for i in range(len(ALL_TILES)) if (i not in used_tile_indices) or (i == selected_tile)]

    return json.dumps({'canvas_url': canvas_url, 'allowed_tile_indices': allowed_tile_indices})


def get_state(s3):
    state_s3_resp = s3.get_object(
        Bucket=S3_BUCKET,
        Key=S3_STATE_KEY
    )
    return State.from_dict(json.loads(state_s3_resp['Body'].read()))


def apply_tile_to_canvas(tile_file_stream, canvas_file_stream, tile_box):
    canvas_img = Image.open(canvas_file_stream)
    tile_img = Image.open(tile_file_stream)

    multiplier = 150

    tile_img = tile_img.resize((tile_box[2] * multiplier, tile_box[3] * multiplier))
    canvas_img.paste(tile_img, (tile_box[0] * multiplier, tile_box[1] * multiplier))

    in_mem_file = io.BytesIO()
    canvas_img.save(in_mem_file, format=canvas_img.format)
    in_mem_file.seek(0)
    return in_mem_file


if __name__ == "__main__":
    if len(sys.argv) == 2:
        app.run(debug=True, port=8000)
    else:
        serve(app, host="0.0.0.0", port=8000)

