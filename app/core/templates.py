from urllib.parse import urlparse
from fastapi.templating import Jinja2Templates
from app.core.config import settings

supabase_host = ""
if settings.supabase_url:
    parsed = urlparse(settings.supabase_url)
    supabase_host = f"{parsed.scheme}://{parsed.netloc}"

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["supabase_host"] = supabase_host
