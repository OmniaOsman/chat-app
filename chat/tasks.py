import redis
from io import BytesIO
from celery import Celery
from PIL import Image
from celery import shared_task
from chat.models import ImageFile
import logging

app = Celery('tasks', broker='redis://localhost:6379/0', serializer='json')


@shared_task
def resize_image(image_file_name: str) -> None:
    """ Resizes an image to the specified thumbnail size 
    and saves it to Redis. """
    
    # Retrieve the image data from Redis
    redis_client = redis.Redis()
    image_data = redis_client.get(image_file_name)
    
    image = Image.open(BytesIO(image_data))
    cropped_image = image.crop((0, 0, 100, 100))

    # Save the resized image to a BytesIO object
    resized_image_data = BytesIO()
    cropped_image.save(resized_image_data, format='JPEG')
    resized_image_data.seek(0)

    # Create a new ImageFile object and save the resized image
    image_file = ImageFile(image_name=image_file_name, 
                           image_file=resized_image_data)
    image_file.save()
    logging.warning(f'Image saved: {image_file.image_name}')
 
    # Delete the image data from Redis
    redis_client.delete(image_file_name)
