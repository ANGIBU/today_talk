# services/user_service.py
from models.user import User
from models.post import Post
from models.comment import Comment
from db import db
from werkzeug.security import generate_password_hash
import os
from datetime import datetime

def get_user_by_id(user_id):
    """
    ID로 사용자 정보 조회
    """
    return User.query.get(user_id)

def get_user_by_username(username):
    """
    사용자명으로 사용자 정보 조회
    """
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    """
    이메일로 사용자 정보 조회
    """
    return User.query.filter_by(email=email).first()

def update_user_profile(user_id, data):
    """
    사용자 프로필 업데이트
    """
    user = get_user_by_id(user_id)
    if not user:
        return False, "사용자를 찾을 수 없습니다."
    
    try:
        # 이메일 중복 확인
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return False, "이미 사용 중인 이메일입니다."
            user.email = data['email']
        
        # 닉네임 중복 확인
        if 'nickname' in data and data['nickname'] != user.nickname:
            if User.query.filter_by(nickname=data['nickname']).first():
                return False, "이미 사용 중인 닉네임입니다."
            user.nickname = data['nickname']
        
        # 비밀번호 변경
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        # 기타 필드 업데이트
        for field in ['name', 'bio', 'profile_image']:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        return True, "프로필이 성공적으로 업데이트되었습니다."
    except Exception as e:
        db.session.rollback()
        return False, f"프로필 업데이트 실패: {str(e)}"

def get_user_posts(user_id, page=1, per_page=10):
    """
    사용자가 작성한 게시글 목록 조회
    """
    return Post.query.filter_by(user_id=user_id)\
                    .order_by(Post.created_at.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)

def get_user_comments(user_id, page=1, per_page=20):
    """
    사용자가 작성한 댓글 목록 조회
    """
    return Comment.query.filter_by(user_id=user_id)\
                       .order_by(Comment.created_at.desc())\
                       .paginate(page=page, per_page=per_page, error_out=False)

def upload_profile_image(user_id, image_file):
    """
    사용자 프로필 이미지 업로드
    """
    user = get_user_by_id(user_id)
    if not user:
        return False, "사용자를 찾을 수 없습니다."
    
    try:
        # 이전 프로필 이미지 삭제
        if hasattr(user, 'profile_image') and user.profile_image:
            old_image_path = os.path.join('static', 'uploads', 'profiles', user.profile_image)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        # 새 프로필 이미지 저장
        filename = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        upload_path = os.path.join('static', 'uploads', 'profiles')
        
        # 디렉토리가 없으면 생성
        os.makedirs(upload_path, exist_ok=True)
        
        # 이미지 저장
        image_file.save(os.path.join(upload_path, filename))
        
        # 사용자 정보 업데이트
        user.profile_image = filename
        db.session.commit()
        
        return True, "프로필 이미지가 성공적으로 업로드되었습니다."
    except Exception as e:
        db.session.rollback()
        return False, f"프로필 이미지 업로드 실패: {str(e)}"

def check_duplicate(field, value):
    """
    중복 확인 (아이디, 이메일, 닉네임)
    """
    if field not in ['username', 'email', 'nickname']:
        raise ValueError('허용되지 않은 필드입니다.')
    
    # 필드별 중복 확인
    filter_condition = {field: value}
    exists = User.query.filter_by(**filter_condition).first() is not None
    return exists