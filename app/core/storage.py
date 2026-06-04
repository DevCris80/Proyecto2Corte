import uuid
import io
from fastapi import UploadFile
from supabase import create_client, Client
from PIL import Image, UnidentifiedImageError

from app.core.config import settings


ALLOWED_IMAGE_MIMES = frozenset({
    "image/jpeg", "image/png", "image/webp", "image/gif", "image/avif"
})


def validar_mime_imagen(archivo: UploadFile) -> str | None:
    ct = archivo.content_type
    if ct is None:
        return None
    if ct not in ALLOWED_IMAGE_MIMES:
        return f"Formato no soportado: '{ct}'. Solo se permiten imágenes (JPG, PNG, WebP, GIF, AVIF)."
    return None


def _supabase_configured() -> bool:
    return bool(settings.supabase_url and settings.supabase_key and settings.supabase_bucket)


def _resize_image(file_bytes: bytes, max_size: int = 600) -> tuple[bytes, str]:
    try:
        img = Image.open(io.BytesIO(file_bytes))
    except UnidentifiedImageError:
        return None
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", optimize=True, quality=85)
    return buffer.getvalue(), "image/webp"


async def subir_imagen_supabase(path_file: UploadFile, folder: str = "general") -> str | None:
    if not _supabase_configured():
        return None

    supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

    file_bytes = await path_file.read()
    resized = _resize_image(file_bytes)
    if resized is None:
        return None
    file_bytes, content_type = resized

    unique_filename = f"{folder}/{uuid.uuid4()}.webp"

    try:
        supabase.storage.from_(settings.supabase_bucket).upload(
            file=file_bytes,
            path=unique_filename,
            file_options={"content-type": content_type}
        )

        public_url = supabase.storage.from_(settings.supabase_bucket).get_public_url(unique_filename)
        return public_url
    except Exception as e:
        return None


def imagen_url_transformada(url: str, width: int = 60, height: int | None = None) -> str:
    if not url:
        return ""
    if "/storage/v1/object/public/" not in url:
        return url
    base = url.replace("/storage/v1/object/public/", "/storage/v1/render/image/public/")
    if height is None:
        return f"{base}?width={width}"
    return f"{base}?width={width}&height={height}&resize=cover"



