import os
import json
import sys
from flask import Flask, request, send_from_directory, redirect, url_for
from waitress import serve
from PIL import Image
import boto3
import io

UPLOAD_FOLDER = '/tmp/uploads'

ALL_TILES = [[0, 0, 5, 5], [5, 0, 3, 3], [8, 0, 4, 3], [5, 3, 4, 3], [9, 3, 3, 3], [12, 0, 3, 3], [0, 5, 5, 4], [5, 6, 3, 3], [12, 3, 3, 4], [0, 9, 4, 4], [4, 9, 4, 5], [8, 6, 4, 4], [12, 7, 3, 3], [8, 10, 3, 4], [11, 10, 4, 3], [11, 13, 4, 4], [0, 13, 4, 3], [4, 14, 3, 3], [0, 16, 4, 4], [7, 14, 4, 3], [4, 17, 4, 3], [8, 17, 3, 3], [11, 17, 4, 3]]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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

    state_s3_resp = s3.get_object(
        Bucket=S3_BUCKET,
        Key=S3_STATE_KEY
    )
    used_tiles = json.loads(state_s3_resp['Body'].read())['used_tiles']

    return json.dumps({'canvas_url': canvas_url, 'tiles': ALL_TILES, 'used_tile_idx': used_tiles})


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return json.dumps({'message': 'No file part'}), 400
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return json.dumps({'message': 'No selected file'}), 400

    selected_tile = int(request.form['selected_tile'])

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    resp = s3.get_object(
        Bucket=S3_BUCKET,
        Key=S3_CANVAS_KEY
    )
    file_stream = resp['Body']
    main_img = Image.open(file_stream)

    tile_img = Image.open(file.stream)

    multiplier = 150

    tile_img = tile_img.resize((ALL_TILES[selected_tile][2] * multiplier, ALL_TILES[selected_tile][3] * multiplier))
    main_img.paste(tile_img, (ALL_TILES[selected_tile][0] * multiplier, ALL_TILES[selected_tile][1] * multiplier))

    in_mem_file = io.BytesIO()
    main_img.save(in_mem_file, format=main_img.format)
    in_mem_file.seek(0)

    result = s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_CANVAS_KEY,
        Body=in_mem_file
    )

    canvas_url = CANVAS_BASE_URL + '?versionId=' + result['VersionId']
    return json.dumps({'canvas_url': canvas_url})


if __name__ == "__main__":
    if len(sys.argv) == 2:
        app.run(debug=True, port=8000)
    else:
        serve(app, host="0.0.0.0", port=8000)

