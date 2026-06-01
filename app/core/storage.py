import uuid
from fastapi import UploadFile, HTTPException
from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    if not settings.supabase_url or not settings.supabase_key:
        raise HTTPException(
            status_code=500,
            detail="La configuración de Supabase no está definida en el servidor."
        )
    return create_client(settings.supabase_url, settings.supabase_key)

async def subir_imagen_supabase(path_file: UploadFile, folder: str = "general") -> str:
    if not settings.supabase_bucket:
        raise HTTPException(
            status_code=500,
            detail="El bucket de Supabase no está configurado."
        )

    supabase: Client = get_supabase_client()
    
    file_extension = path_file.filename.split(".")[-1] if path_file.filename else "bin"
    unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
    
    file_bytes = await path_file.read()
    
    try:
        response = supabase.storage.from_(settings.supabase_bucket).upload(
            file=file_bytes,
            path=unique_filename,
            file_options={"content-type": path_file.content_type}
        )
        
        public_url = supabase.storage.from_(settings.supabase_bucket).get_public_url(unique_filename)
        return public_url
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir archivo a Supabase: {str(e)}"
        )
