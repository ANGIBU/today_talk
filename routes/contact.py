from flask import Blueprint, render_template, request, flash, redirect, url_for

# Contact 블루프린트 정의
contact_blueprint = Blueprint('contact', __name__, url_prefix='/contact')

# 문의 목록 페이지
@contact_blueprint.route('/')
def contact_index():
    return render_template('contact/index.html')

# 문의 작성 페이지
@contact_blueprint.route('/create', methods=['GET', 'POST'])
def contact_create():
    if request.method == 'POST':
        # 여기에 문의 데이터 처리 로직 추가
        flash('문의가 성공적으로 접수되었습니다.', 'success')
        return redirect(url_for('contact.contact_index'))
    return render_template('contact/create.html')
