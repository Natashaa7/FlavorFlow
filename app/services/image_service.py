import os
from uuid import uuid4
from PIL import Image, ImageOps, UnidentifiedImageError
from io import BytesIO
from app.db.session import get_db_connection


def process_image(image):
    try:
        contents = image.file.read()  
        img = Image.open(BytesIO(contents))

        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((512, 512))

        return img

    except Exception:
        return None



def save_profile_image(img):
    upload_dir = "app/static/profile_images"
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid4().hex}.jpg"
    file_path = os.path.join(upload_dir, filename)

    img.save(file_path, "JPEG", quality=85)

    return f"/static/profile_images/{filename}"


def update_profile_image(user_id, image_url):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE users SET profile_image=%s WHERE id=%s",
            (image_url, user_id)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()
