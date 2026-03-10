# ============================================================================
# FILE: upload_handler.py
# PURPOSE: Secure file upload handling for garment images.
# ============================================================================

import os
import uuid
from flask import request, jsonify

# Allowed image extensions and MIME types
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ALLOWED_MIME_TYPES  = {"image/png", "image/jpeg", "image/webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB


def _allowed_file(filename: str, mimetype: str) -> bool:
    """Returns True only if extension AND MIME type are both on the allow-list."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS and mimetype in ALLOWED_MIME_TYPES


def handle_upload():
    """
    Handles POST /upload.
    Validates file type and size before saving to the uploads/ directory.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "" or file.filename is None:
        return jsonify({"error": "No file selected"}), 400

    # --- Security: validate type ---
    if not _allowed_file(file.filename, file.mimetype):
        return jsonify(
            {"error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}
        ), 400

    # --- Security: validate size ---
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_FILE_SIZE_BYTES:
        return jsonify({"error": "File too large. Maximum size is 10 MB."}), 400

    # --- Save with a UUID prefix to prevent filename collisions / traversal ---
    safe_ext      = file.filename.rsplit(".", 1)[1].lower()
    safe_filename = f"{uuid.uuid4().hex}.{safe_ext}"

    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    filepath = os.path.join(uploads_dir, safe_filename)
    file.save(filepath)

    description = request.form.get("description", "").strip()

    return jsonify(
        {
            "image_path": filepath,
            "session_id": str(uuid.uuid4()),
            "description": description,
            "message": "Image uploaded successfully. Ready to analyse.",
            "success": True,
        }
    )
