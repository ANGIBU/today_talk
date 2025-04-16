# api\check_id.py
from flask import Blueprint, request, jsonify
from services.user_service import check_duplicate

check_id_blueprint = Blueprint('check_id', __name__)

@check_id_blueprint.route('/check-id', methods=['POST'])
def check_id():
    """
    Check if a user ID is already in use.
    """
    data = request.get_json()
    user_id = data.get('user_id') or data.get('username', '').strip() if data else ''
    if not user_id:
        return jsonify({'success': False, 'message': '아이디를 입력하세요.'}), 400
    is_duplicate = check_duplicate('username', user_id)
    return jsonify({'success': True, 'is_duplicate': is_duplicate})
