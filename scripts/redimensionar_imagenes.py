import asyncio
import io
import os
import httpx
from PIL import Image
from sqlmodel import select
from supabase import create_client, Client

from app.core.database import async_session
from app.core.config import settings
from app.models.producto import Producto
from app.models.proveedor import Proveedor


def _resize_image(file_bytes: bytes, max_size: int = 600) -> bytes:
    img = Image.open(io.BytesIO(file_bytes))
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        fmt = img.format or "JPEG"
        buffer = io.BytesIO()
        img.save(buffer, format=fmt, optimize=True, quality=85)
        return buffer.getvalue()
    return file_bytes


def _extract_path(public_url: str) -> str | None:
    prefix = f"{settings.supabase_url}/storage/v1/object/public/"
    if public_url.startswith(prefix):
        return public_url[len(prefix):]
    return None


async def main():
    supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
    bucket = settings.supabase_bucket

    async with httpx.AsyncClient(timeout=30) as http:
        async with async_session() as session:
            for model, tipo in [(Producto, "productos"), (Proveedor, "proveedores")]:
                result = await session.execute(select(model).where(model.imagen_url.isnot(None)))
                items = result.scalars().all()
                for item in items:
                    if not item.imagen_url:
                        continue
                    path = _extract_path(item.imagen_url)
                    if not path:
                        continue
                    print(f"Procesando {tipo}/{item.id}...")
                    try:
                        resp = await http.get(item.imagen_url)
                        resp.raise_for_status()
                        original = resp.content
                        resized = _resize_image(original)
                        if len(resized) >= len(original):
                            continue
                        supabase.storage.from_(bucket).upload(
                            file=resized,
                            path=path,
                            file_options={"content-type": resp.headers.get("content-type", "image/png"), "upsert": "true"}
                        )
                        mb_original = len(original) / (1024 * 1024)
                        mb_resized = len(resized) / (1024 * 1024)
                        print(f"  {item.imagen_url.split('/')[-1]}: {mb_original:.2f}MB → {mb_resized:.2f}MB")
                    except Exception as e:
                        print(f"  Error: {e}")
            await session.commit()
    print("Listo.")


if __name__ == "__main__":
    asyncio.run(main())
