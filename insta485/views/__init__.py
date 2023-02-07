"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.accounts import login_page, logout, create_page, edit_page
from insta485.views.accounts import delete_page, password_page, post_accounts
from insta485.views.posts import post_page
from insta485.views.users import user_page
from insta485.views.followers import show_followers
from insta485.views.following import show_following
from insta485.views.explore import explore
from insta485.views.likes import like_action
from insta485.views.comments import comment_action
from insta485.views.uploads import file_url
