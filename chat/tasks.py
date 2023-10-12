from celery import Celery
from PIL import Image

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def resize_image(image_file, thumbnail_size=(120, 100)):
    image = Image.open(image_file)
    image.thumbnail(thumbnail_size)
    image.save(f'{image_file.name}-thumbnail.jpg')

