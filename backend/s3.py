import os
import boto3, botocore
from PIL import Image


if __name__ == '__main__':
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    resp = s3.get_object(
        Bucket='belarus-image-collage',
        Key='tiles.png'
    )
    file_stream = resp['Body']
    im = Image.open(file_stream)

    multiplier = 150

    tile_img = Image.open('/tmp/300.jpeg')
    tile_img = tile_img.resize((3 * multiplier, 3 * multiplier))
    im.paste(tile_img, (12 * multiplier, 0 * multiplier))
    im.save('result.png')
