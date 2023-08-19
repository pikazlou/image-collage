import os
import json
from flask import Flask, request, send_from_directory, redirect, url_for
from waitress import serve
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/tmp/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def root():
    return redirect('index.html')


@app.route('/<path:path>')
def serve_static(path):
    print(path)
    return send_from_directory('../site', path)


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return json.dumps({'message': 'No file part'}), 400
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return json.dumps({'message': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return json.dumps({'message': 'OK'})
    # return redirect(url_for('download_file', name=filename))


if __name__ == "__main__":
    app.run(debug=True, port=9000)
