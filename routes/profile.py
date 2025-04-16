from flask import Blueprint

profile_blueprint = Blueprint('profile', __name__, url_prefix='/profile')

# 라우트 추가
@profile_blueprint.route('/')
def profile():
    return "Profile 페이지"
