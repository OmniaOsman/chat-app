import os
import logging
import redis
from PIL import Image
from io import BytesIO
from celery import shared_task
from chat.models import ImageFile


@shared_task(bind=True)
def resize_image(self, image_id: str):
    """ Resize an image and save the thumbnail version. """
    thumbnail_size = (100, 100)
    logging.warning(f'Resizing image with ID: {image_id}')

    redis_client = redis.Redis()
    image_data = redis_client.get(image_id)

    image_data_io = BytesIO(image_data)

    original_image = Image.open(image_data_io)
    thumbnail_image = original_image.resize(thumbnail_size)

    # Convert the image to RGB mode
    if thumbnail_image.mode == 'RGBA':
        thumbnail_image = thumbnail_image.convert('RGB')

    thumbnail_file_name = f"{image_id}-thumbnail.jpeg"
    thumbnail_file_path = os.path.join('media', 'resized_images', thumbnail_file_name)
    logging.warning(f'Saving thumbnail image to: {thumbnail_file_path}')
    thumbnail_image.save(thumbnail_file_path)

    return thumbnail_file_path

