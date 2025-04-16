from flask import Blueprint, request, jsonify
from services.user_service import check_duplicate

check_nickname_blueprint = Blueprint('check_nickname', __name__)

@check_nickname_blueprint.route('/check-nickname', methods=['POST'])
def check_nickname():
    """
    Check if a nickname is already in use.
    """
    data = request.get_json()
    nickname = data.get('nickname', '').strip() if data else ''
    if not nickname:
        return jsonify({'success': False, 'message': '닉네임을 입력하세요.'}), 400
    is_duplicate = check_duplicate('nickname', nickname)
    return jsonify({'success': True, 'is_duplicate': is_duplicate})
