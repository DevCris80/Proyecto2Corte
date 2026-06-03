import uuid
import io
from fastapi import UploadFile
from supabase import create_client, Client
from PIL import Image

from app.core.config import settings



def _supabase_configured() -> bool:
    return bool(settings.supabase_url and settings.supabase_key and settings.supabase_bucket)


def _resize_image(file_bytes: bytes, max_size: int = 600) -> bytes:
    img = Image.open(io.BytesIO(file_bytes))
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        fmt = img.format or "JPEG"
        buffer = io.BytesIO()
        img.save(buffer, format=fmt, optimize=True, quality=85)
        return buffer.getvalue()
    return file_bytes


async def subir_imagen_supabase(path_file: UploadFile, folder: str = "general") -> str | None:
    if not _supabase_configured():
        return None

    supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

    file_extension = path_file.filename.split(".")[-1] if path_file.filename else "bin"
    unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"

    file_bytes = await path_file.read()
    file_bytes = _resize_image(file_bytes)

    try:
        supabase.storage.from_(settings.supabase_bucket).upload(
            file=file_bytes,
            path=unique_filename,
            file_options={"content-type": path_file.content_type}
        )

        public_url = supabase.storage.from_(settings.supabase_bucket).get_public_url(unique_filename)
        return public_url
    except Exception as e:
        return None

    supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

    file_extension = path_file.filename.split(".")[-1] if path_file.filename else "bin"
    unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"

    file_bytes = await path_file.read()

    try:
        supabase.storage.from_(settings.supabase_bucket).upload(
            file=file_bytes,
            path=unique_filename,
            file_options={"content-type": path_file.content_type}
        )

        public_url = supabase.storage.from_(settings.supabase_bucket).get_public_url(unique_filename)
        return public_url
    except Exception as e:
        return None


async def get_imagen(request: Request) -> UploadFile | None:
    form = await request.form()
    imagen = form.get("imagen")

    if isinstance(imagen, UploadFile) and imagen.filename:
        return imagen
    return None
