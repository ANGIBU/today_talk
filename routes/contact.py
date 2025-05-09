# routes/contact.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
from flask_mail import Message
from models.contact import Contact
from db import db
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 정의
contact_blueprint = Blueprint('contact', __name__, url_prefix='/contact')

# 문의하기 페이지
@contact_blueprint.route('/', methods=['GET'])
def index():
    return render_template('contact/contact.html')

# 문의하기 처리
@contact_blueprint.route('/submit', methods=['POST'])
def submit():
    try:
        # 폼 데이터 가져오기
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        
        # 필수 필드 검증
        if not subject or not message:
            flash('제목과 메시지를 모두 입력해주세요.', 'danger')
            return redirect(url_for('contact.index'))
            
        # 새 문의 생성
        new_contact = Contact(
            subject=subject,
            message=message,
            name=name or None,
            email=email or None,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        
        db.session.add(new_contact)
        db.session.commit()
        
        # 관리자에게 이메일 전송
        try:
            from flask_mail import Mail
            mail = Mail(current_app)
            
            admin_email = current_app.config.get('MAIL_DEFAULT_SENDER')
            if admin_email:
                msg = Message(
                    subject=f'[Today Talk] 새 문의: {subject}',
                    recipients=[admin_email],
                    body=f'''
                    새 문의가 등록되었습니다.
                    
                    문의자: {name or '이름 없음'} {'(' + email + ')' if email else '(이메일 없음)'}
                    사용자 ID: {current_user.id if current_user.is_authenticated else '비회원'}
                    
                    제목: {subject}
                    
                    내용:
                    {message}
                    ''',
                    sender=current_app.config.get('MAIL_DEFAULT_SENDER')
                )
                mail.send(msg)
        except Exception as e:
            logger.error(f"이메일 전송 중 오류 발생: {e}")
            # 이메일 전송 실패해도 DB 저장은 완료되었으므로 성공 메시지 표시
            
        flash('문의가 성공적으로 접수되었습니다. 빠른 시일 내에 답변 드리겠습니다.', 'success')
        return redirect(url_for('contact.index'))
        
    except Exception as e:
        logger.error(f"문의 접수 중 오류 발생: {e}")
        db.session.rollback()
        flash('문의 접수 중 오류가 발생했습니다. 다시 시도해주세요.', 'danger')
        return redirect(url_for('contact.index'))

# 관리자용 문의 목록 페이지 (관리자만 접근 가능)
@contact_blueprint.route('/admin', methods=['GET'])
def admin():
    # 관리자 권한 확인
    if not current_user.is_authenticated or current_user.id != 1:  # 관리자 ID 확인
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('home.index'))
    
    # 문의 목록 조회
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    
    return render_template('contact/admin.html', contacts=contacts)

# 관리자용 문의 상세 페이지 (관리자만 접근 가능)
@contact_blueprint.route('/admin/<int:contact_id>', methods=['GET'])
def admin_detail(contact_id):
    # 관리자 권한 확인
    if not current_user.is_authenticated or current_user.id != 1:  # 관리자 ID 확인
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('home.index'))
    
    # 문의 상세 조회
    contact = Contact.query.get_or_404(contact_id)
    
    return render_template('contact/admin_detail.html', contact=contact)

# 관리자용 문의 답변 처리 (관리자만 접근 가능)
@contact_blueprint.route('/admin/<int:contact_id>/reply', methods=['POST'])
def admin_reply(contact_id):
    # 관리자 권한 확인
    if not current_user.is_authenticated or current_user.id != 1:  # 관리자 ID 확인
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('home.index'))
    
    # 문의 상세 조회
    contact = Contact.query.get_or_404(contact_id)
    
    # 답변 내용 가져오기
    reply = request.form.get('reply', '').strip()
    
    if not reply:
        flash('답변 내용을 입력해주세요.', 'danger')
        return redirect(url_for('contact.admin_detail', contact_id=contact_id))
    
    try:
        # 이메일 전송
        if contact.email:
            from flask_mail import Mail
            mail = Mail(current_app)
            
            msg = Message(
                subject=f'[Today Talk] 문의에 대한 답변: {contact.subject}',
                recipients=[contact.email],
                body=f'''
                안녕하세요, {contact.name or '회원님'}
                
                문의하신 내용에 대한 답변입니다.
                
                문의 제목: {contact.subject}
                문의 일시: {contact.created_at.strftime('%Y-%m-%d %H:%M')}
                
                답변:
                {reply}
                
                추가 문의사항이 있으시면 언제든지 문의해주세요.
                감사합니다.
                
                Today Talk 팀 드림
                ''',
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            mail.send(msg)
            
            # 답변 상태 업데이트
            contact.is_replied = True
            contact.replied_at = db.func.now()
            contact.reply = reply
            db.session.commit()
            
            flash('답변이 성공적으로 전송되었습니다.', 'success')
            
        else:
            flash('문의자의 이메일 정보가 없어 답변을 전송할 수 없습니다.', 'warning')
            
        return redirect(url_for('contact.admin_detail', contact_id=contact_id))
        
    except Exception as e:
        logger.error(f"답변 전송 중 오류 발생: {e}")
        db.session.rollback()
        flash('답변 전송 중 오류가 발생했습니다. 다시 시도해주세요.', 'danger')
        return redirect(url_for('contact.admin_detail', contact_id=contact_id))