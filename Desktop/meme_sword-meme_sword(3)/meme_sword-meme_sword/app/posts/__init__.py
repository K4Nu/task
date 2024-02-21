from flask import Blueprint
from .utils import utility_processor
posts = Blueprint('posts', __name__)
posts.context_processor(utility_processor)

from . import routes