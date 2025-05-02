from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from flask import url_for

# Blueprint 이름을 api로 변경하고 url_prefix 추가
upload_blueprint = Blueprint("api", __name__, url_prefix="/api")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_blueprint.route(
    "/upload", methods=["POST"]
)  # url_prefix가 있으므로 /api는 제거
def upload_file():
    print("Upload endpoint hit!")  # 디버깅용 로그
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.static_folder, "uploads")

        # uploads 폴더가 없으면 생성
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # URL 생성 (static/uploads/ 폴더 기준)
        url = url_for("static", filename=f"uploads/{filename}")
        return jsonify({"url": url})

    return jsonify({"error": "Invalid file type"}), 400


@upload_blueprint.route(
    "/delete-upload", methods=["DELETE"]
)  # url_prefix가 있으므로 /api는 제거
def delete_upload():
    print("Delete endpoint hit!")  # 디버깅용 로그
    file_url = request.args.get("url")
    if not file_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # URL에서 파일명 추출
        filename = os.path.basename(file_url)
        filepath = os.path.join(current_app.static_folder, "uploads", filename)

        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
