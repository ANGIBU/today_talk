from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from db import db
from models.comment import Comment
from sqlalchemy import case

comments_blueprint = Blueprint("comments", __name__, url_prefix="/comments")

@comments_blueprint.route("/<int:post_id>/create", methods=["POST"])
@login_required
def create_comment(post_id):
    """댓글 작성"""
    content = request.form["content"]
    new_comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    flash("댓글이 성공적으로 작성되었습니다.", "success")
    return redirect(url_for("posts.detail_post", post_id=post_id))

@comments_blueprint.route("/<int:comment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    """댓글 수정"""
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        flash("수정 권한이 없습니다.", "danger")
        return redirect(url_for("posts.detail_post", post_id=comment.post_id))

    if request.method == "POST":
        comment.content = request.form["content"]
        db.session.commit()
        flash("댓글이 성공적으로 수정되었습니다.", "success")
        return redirect(url_for("posts.detail_post", post_id=comment.post_id))
    return render_template("comments/edit.html", comment=comment)

@comments_blueprint.route("/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    """댓글 삭제"""
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        flash("삭제 권한이 없습니다.", "danger")
        return redirect(url_for("posts.detail_post", post_id=comment.post_id))

    db.session.delete(comment)
    db.session.commit()
    flash("댓글이 성공적으로 삭제되었습니다.", "success")
    return redirect(url_for("posts.detail_post", post_id=comment.post_id))

@comments_blueprint.route("/list", methods=["GET"])
def list_comments():
    """댓글 목록 조회"""
    comments = (
        Comment.query.order_by(
            case((Comment.parent_id.is_(None), 0), else_=1),
            Comment.parent_id.asc(),
            Comment.created_at.asc(),
        ).all()
    )
    return render_template("comments/list.html", comments=comments)

@comments_blueprint.route("/<int:post_id>/<int:parent_id>/reply", methods=["POST"])
@login_required
def create_reply(post_id, parent_id):
    """답글 작성"""
    content = request.form.get("content")
    if not content:
        flash("답글 내용을 입력해주세요.", "danger")
        return redirect(url_for("posts.detail_post", post_id=post_id))

    parent_comment = Comment.query.get_or_404(parent_id)
    reply = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id,
        depth=parent_comment.depth + 1,
    )
    db.session.add(reply)
    db.session.commit()
    flash("답글이 성공적으로 작성되었습니다.", "success")
    return redirect(url_for("posts.detail_post", post_id=post_id))
