import os
from dotenv import load_dotenv
from supabase import create_client, Client

# .env faylındakı dəyişənləri yükləyirik
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL və ya KEY tapılmadı! .env faylını yoxlayın.")

# Supabase müştərisini başladırıq
supabase: Client = create_client(url, key)