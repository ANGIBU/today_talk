from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
)
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.post import Post
from models.comment import Comment
from sqlalchemy import case

posts_blueprint = Blueprint("posts", __name__, url_prefix="/posts")

@posts_blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        category = request.form["category"]
        image_url = request.form.get("image_url")

        new_post = Post(
            title=title,
            content=content,
            category=category,
            user_id=current_user.id,
            image_url=image_url,
        )
        try:
            db.session.add(new_post)
            db.session.commit()
            flash("게시글이 성공적으로 작성되었습니다.", "success")
            return redirect(url_for("posts.get_posts", category=category))
        except Exception as e:
            db.session.rollback()
            flash(f"게시글 작성 중 오류가 발생했습니다: {e}", "danger")
            current_app.logger.error(f"Error creating post: {e}")
            return redirect(url_for("posts.create_post"))

    return render_template("posts/add.html")

@posts_blueprint.route("/<int:post_id>")
def detail_post(post_id):
    post = Post.query.get_or_404(post_id)

    comments = (
        Comment.query.filter(Comment.post_id == post_id)
        .order_by(case((Comment.parent_id.is_(None), 0), else_=1), Comment.parent_id.asc(), Comment.created_at.asc())
        .all()
    )

    try:
        db.session.query(Post).filter(Post.id == post_id).update(
            {"views": Post.views + 1}
        )
        db.session.flush()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"조회수 업데이트 중 오류 발생: {e}")

    return render_template("posts/detail.html", post=post, comments=comments)

@posts_blueprint.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash("수정 권한이 없습니다.", "danger")
        return redirect(url_for("posts.detail_post", post_id=post_id))

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        post.image_url = request.form.get("image_url")
        try:
            db.session.commit()
            flash("게시글이 성공적으로 수정되었습니다.", "success")
            return redirect(url_for("posts.detail_post", post_id=post_id))
        except Exception as e:
            db.session.rollback()
            flash(f"게시글 수정 중 오류가 발생했습니다: {e}", "danger")
            current_app.logger.error(f"Error updating post: {e}")
            return redirect(url_for("posts.edit_post", post_id=post_id))

    return render_template("posts/edit.html", post=post)

@posts_blueprint.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash("삭제 권한이 없습니다.", "danger")
        return redirect(url_for("posts.detail_post", post_id=post_id))

    try:
        category = post.category
        db.session.delete(post)
        db.session.commit()
        flash("게시글이 성공적으로 삭제되었습니다.", "success")
        return redirect(url_for("posts.get_posts", category=category))
    except Exception as e:
        db.session.rollback()
        flash(f"게시글 삭제 중 오류가 발생했습니다: {e}", "danger")
        current_app.logger.error(f"Error deleting post: {e}")
        return redirect(url_for("posts.detail_post", post_id=post_id))

@posts_blueprint.route("/<string:category>")
def get_posts(category):
    try:
        page = request.args.get("page", 1, type=int)
        per_page = 10

        if category == "all":
            posts_query = Post.query.order_by(Post.created_at.desc())
        elif category == "popular":
            posts_query = Post.query.order_by(Post.likes.desc())
        else:
            posts_query = Post.query.filter_by(category=category).order_by(
                Post.created_at.desc()
            )

        posts = posts_query.paginate(page=page, per_page=per_page, error_out=False)

        template_name = f"posts/posts_{category}.html"
        return render_template(template_name, posts=posts)

    except Exception as e:
        current_app.logger.error(f"Error in get_posts: {str(e)}")
        flash("게시글을 불러오는 중 오류가 발생했습니다.", "danger")
        return redirect(url_for("home.index"))

posts_blueprint.add_url_rule(
    "/all", "get_posts", get_posts, defaults={"category": "all"}
)
posts_blueprint.add_url_rule(
    "/free", "get_posts", get_posts, defaults={"category": "free"}
)
posts_blueprint.add_url_rule(
    "/popular", "get_posts", get_posts, defaults={"category": "popular"}
)
posts_blueprint.add_url_rule(
    "/humor", "get_posts", get_posts, defaults={"category": "humor"}
)
posts_blueprint.add_url_rule(
    "/info", "get_posts", get_posts, defaults={"category": "info"}
)
