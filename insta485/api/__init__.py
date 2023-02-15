"""Insta485 REST API."""


from insta485.api.posts import get_services, get_posts, get_post
from insta485.api.comments import post_comment, delete_comment
from insta485.api.likes import post_likes, delete_likes