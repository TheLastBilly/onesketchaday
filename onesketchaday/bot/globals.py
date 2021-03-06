from django.core.exceptions import *
from asgiref.sync import *
from app.models import *
import logging, os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ['.png', '.jpeg', '.gif', '.jpg', '.mp4']
VIDEO_EXTENSIONS = ['.mp4', '.mov']

FILE_EXTENSIONS = IMAGE_EXTENSIONS + VIDEO_EXTENSIONS