import uuid
import logging
from fastapi import UploadFile
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)


def _supabase_configured() -> bool:
    return bool(settings.supabase_url and settings.supabase_key and settings.supabase_bucket)


async def subir_imagen_supabase(path_file: UploadFile, folder: str = "general") -> str | None:
    if not _supabase_configured():
        logger.warning("Supabase no configurado, imagen no subida")
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
        logger.error("Error al subir archivo a Supabase: %s", e)
        return None
