import io
import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import UploadFile

from app.core.storage import (
    ALLOWED_IMAGE_MIMES,
    validar_mime_imagen,
    _resize_image,
    _supabase_configured,
    subir_imagen_supabase,
)


class TestValidarMIME:
    def test_mime_permitido_jpeg(self):
        archivo = MagicMock(spec=UploadFile, content_type="image/jpeg")
        assert validar_mime_imagen(archivo) is None

    def test_mime_permitido_png(self):
        archivo = MagicMock(spec=UploadFile, content_type="image/png")
        assert validar_mime_imagen(archivo) is None

    def test_mime_permitido_webp(self):
        archivo = MagicMock(spec=UploadFile, content_type="image/webp")
        assert validar_mime_imagen(archivo) is None

    def test_mime_permitido_gif(self):
        archivo = MagicMock(spec=UploadFile, content_type="image/gif")
        assert validar_mime_imagen(archivo) is None

    def test_mime_permitido_avif(self):
        archivo = MagicMock(spec=UploadFile, content_type="image/avif")
        assert validar_mime_imagen(archivo) is None

    def test_mime_video_rechazado(self):
        archivo = MagicMock(spec=UploadFile, content_type="video/mp4")
        error = validar_mime_imagen(archivo)
        assert error is not None
        assert "Formato no soportado" in error
        assert "video/mp4" in error

    def test_mime_pdf_rechazado(self):
        archivo = MagicMock(spec=UploadFile, content_type="application/pdf")
        error = validar_mime_imagen(archivo)
        assert error is not None
        assert "Formato no soportado" in error

    def test_mime_none_aceptado(self):
        archivo = MagicMock(spec=UploadFile, content_type=None)
        assert validar_mime_imagen(archivo) is None

    def test_allowed_mimes_contiene_tipos_esperados(self):
        assert "image/jpeg" in ALLOWED_IMAGE_MIMES
        assert "image/png" in ALLOWED_IMAGE_MIMES
        assert "image/webp" in ALLOWED_IMAGE_MIMES
        assert "image/gif" in ALLOWED_IMAGE_MIMES
        assert "image/avif" in ALLOWED_IMAGE_MIMES


class TestResizeImage:
    def test_resize_imagen_valida(self):
        from PIL import Image
        buf = io.BytesIO()
        img = Image.new("RGB", (100, 100), color="red")
        img.save(buf, "JPEG")
        result = _resize_image(buf.getvalue())
        assert result is not None
        bytes_out, content_type = result
        assert content_type == "image/webp"
        assert len(bytes_out) > 0

    def test_resize_imagen_grande_se_redimensiona(self):
        from PIL import Image
        buf = io.BytesIO()
        img = Image.new("RGB", (1200, 800), color="blue")
        img.save(buf, "JPEG")
        result = _resize_image(buf.getvalue())
        assert result is not None
        bytes_out, content_type = result
        assert content_type == "image/webp"
        img_out = Image.open(io.BytesIO(bytes_out))
        assert max(img_out.size) <= 600

    def test_resize_imagen_pequena_no_se_redimensiona(self):
        from PIL import Image
        buf = io.BytesIO()
        img = Image.new("RGB", (50, 50), color="green")
        img.save(buf, "PNG")
        result = _resize_image(buf.getvalue())
        assert result is not None
        img_out = Image.open(io.BytesIO(result[0]))
        assert max(img_out.size) == 50

    def test_resize_bytes_no_imagen_retorna_none(self):
        result = _resize_image(b"esto no es una imagen")
        assert result is None

    def test_resize_vacio_retorna_none(self):
        result = _resize_image(b"")
        assert result is None


class TestSubirImagenSupabase:
    @pytest.fixture
    def mock_upload_file(self):
        from PIL import Image
        buf = io.BytesIO()
        img = Image.new("RGB", (100, 100), color="red")
        img.save(buf, "JPEG")
        f = MagicMock(spec=UploadFile)
        f.read = AsyncMock(return_value=buf.getvalue())
        f.content_type = "image/jpeg"
        return f

    async def test_supabase_no_configurado_retorna_none(self, mock_upload_file):
        with patch("app.core.storage._supabase_configured", return_value=False):
            result = await subir_imagen_supabase(mock_upload_file)
            assert result is None

    async def test_upload_mime_invalido_pasa_validacion_resize(self):
        """Si content_type no se valida antes, _resize_image lo maneja con None"""
        f = MagicMock(spec=UploadFile)
        f.read = AsyncMock(return_value=b"datos no imagen")
        f.content_type = None
        with patch("app.core.storage._supabase_configured", return_value=True):
            result = await subir_imagen_supabase(f)
            assert result is None

    async def test_upload_exitoso_retorna_url(self, mock_upload_file):
        supabase_mock = MagicMock()
        supabase_mock.storage.from_.return_value.upload.return_value = None
        supabase_mock.storage.from_.return_value.get_public_url.return_value = (
            "https://ejemplo.supabase.co/storage/v1/object/public/test/foo.webp"
        )
        with (
            patch("app.core.storage._supabase_configured", return_value=True),
            patch("app.core.storage.create_client", return_value=supabase_mock),
        ):
            result = await subir_imagen_supabase(mock_upload_file)
            assert result == "https://ejemplo.supabase.co/storage/v1/object/public/test/foo.webp"
