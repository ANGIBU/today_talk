# api\check_email.py
from flask import Blueprint, request, jsonify
from services.user_service import check_duplicate

check_email_blueprint = Blueprint('check_email', __name__)

@check_email_blueprint.route('/check-email', methods=['POST'])
def check_email():
    """
    Check if an email is already in use.
    """
    data = request.get_json()
    email = data.get('email', '').strip() if data else ''
    if not email:
        return jsonify({'success': False, 'message': '이메일을 입력하세요.'}), 400
    is_duplicate = check_duplicate('email', email)
    return jsonify({'success': True, 'is_duplicate': is_duplicate})
