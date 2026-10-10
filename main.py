import os
import uuid
import traceback
import io
import json
import hmac
import re
import csv
import asyncio
import imaplib
import tempfile
import email as email_lib
from datetime import datetime, timedelta
from email.header import decode_header
import pandas as pd
import jwt
import urllib.request
import urllib.error
import base64
from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel, EmailStr
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from supabase import create_client, Client
from dotenv import load_dotenv
from passlib.context import CryptContext
from pathlib import Path

# --- YENİ: OPENAI VƏ PDF KİTABXANALARI ---
from openai import AsyncOpenAI
import PyPDF2

# --- TƏHLÜKƏSİZLİK KİTABXANALARI ---
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BASE_DIR = Path(__file__).resolve().parent

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "https://arachi.co")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL və ya SUPABASE_KEY təyin olunmayıb! Zəhmət olmasa .env faylını yoxlayın.")

# ==========================================
# OPENAI (CHATGPT) API BAĞLANTISI
# ==========================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("XƏBƏRDARLIQ: OPENAI_API_KEY təyin olunmayıb! .env faylını yoxlayın.")
else:
    print("OpenAI API açarı tapıldı!")

aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = FastAPI(title="Arachi Backend API")

# ==========================================
# MƏRHƏLƏ 4: BOT VƏ BRUTE-FORCE QORUNMASI
# ==========================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ==========================================
# MƏRHƏLƏ 1: JWT TOKEN VƏ IDOR QORUNMASI
# ==========================================
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET təyin olunmayıb! Zəhmət olmasa .env faylına əlavə edin.")
    
JWT_ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def _decode_token(credentials: HTTPAuthorizationCredentials):
    try:
        return jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sessiyanın vaxtı bitib. Zəhmət olmasa yenidən giriş edin.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Etibarsız token. Sistemə giriş qadağandır!")

def verify_any_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Hər hansı etibarlı token (şifrə / e-poçt dəyişmə kimi ortaq əməliyyatlar üçün)."""
    return _decode_token(credentials)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Müştəri paneli endpointləri. Köhnə tokenlərdə 'customer_access' yoxdur - onlar müştəri sayılır.
    Yalnız forwarder paneli hüququ olan hesablar müştəri panelinin məlumatlarına çıxış əldə edə bilmir."""
    payload = _decode_token(credentials)
    if payload.get("customer_access") is False:
        raise HTTPException(status_code=403, detail="Bu hesabın müştəri panelinə girişi yoxdur.")
    return payload

def verify_forwarder_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Freight forwarder paneli endpointləri."""
    payload = _decode_token(credentials)
    if payload.get("forwarder_access") is not True:
        raise HTTPException(status_code=403, detail="Bu hesabın forwarder panelinə girişi yoxdur.")
    return payload

def check_ownership(requested_customer_id: int, current_user: dict):
    if str(requested_customer_id) != str(current_user.get("sub")):
        raise HTTPException(status_code=403, detail="Təhlükəsizlik Xəbərdarlığı: İcazə rədd edildi! Bu məlumat sizə aid deyil.")

# ==========================================
# MƏRHƏLƏ 3: ZƏRƏRLİ FAYL QORUNMASI
# ==========================================
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".xlsx", ".xls", ".doc", ".docx", ".csv", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/csv",
    "text/plain"
}
MAX_FILE_SIZE = 10 * 1024 * 1024  

async def validate_file(file: UploadFile):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400, 
            detail="Təhlükəsizlik: Yalnız PDF, Word (DOC/DOCX), Excel (XLS/XLSX), CSV, TXT və ya Şəkil (PNG/JPG) yükləyə bilərsiniz."
        )
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Təhlükəsizlik: Faylın həcmi maksimum 10 MB ola bilər.")

# ==========================================
# CORS QORUNMASI
# ==========================================
ALLOWED_ORIGINS = [
    "https://arachi.co",
    "https://www.arachi.co",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOUNCE_CHECK_INTERVAL_SECONDS = int(os.getenv("BOUNCE_CHECK_INTERVAL_SECONDS", "300"))

async def _bounce_check_loop():
    while True:
        try:
            result = await asyncio.to_thread(check_bounced_emails)
            if result.get("updated"):
                print(f"[bounce-check] {len(result['updated'])} quote(s) 'failed' olaraq yeniləndi: {result['updated']}")
            if result.get("errors"):
                print(f"[bounce-check] Xətalar: {result['errors']}")
        except Exception:
            traceback.print_exc()
        await asyncio.sleep(BOUNCE_CHECK_INTERVAL_SECONDS)

@app.on_event("startup")
async def start_bounce_check_background_task():
    if ENABLE_BOUNCE_CHECK:
        asyncio.create_task(_bounce_check_loop())
    else:
        print("[bounce-check] Deaktivdir.")

os.makedirs("static", exist_ok=True)
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

SES_MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
SES_MAIL_USE_SSL = SES_MAIL_PORT == 465

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", ""),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Arachi"),
    MAIL_PORT=SES_MAIL_PORT,
    MAIL_SERVER=os.getenv("MAIL_SERVER", ""),
    MAIL_STARTTLS=not SES_MAIL_USE_SSL,
    MAIL_SSL_TLS=SES_MAIL_USE_SSL,
    USE_CREDENTIALS=True
)

fastmail = FastMail(conf)
ENABLE_BOUNCE_CHECK = os.getenv("ENABLE_BOUNCE_CHECK", "false").lower() == "true"
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USERNAME = os.getenv("IMAP_USERNAME", "")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD", "")

def _decode_mime_str(s: Optional[str]) -> str:
    if not s: return ""
    parts = decode_header(s)
    decoded = ""
    for text, enc in parts:
        if isinstance(text, bytes):
            try: decoded += text.decode(enc or "utf-8", errors="ignore")
            except LookupError: decoded += text.decode("utf-8", errors="ignore")
        else: decoded += text
    return decoded

def _get_message_text(msg) -> str:
    chunks = []
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype in ("text/plain", "text/html", "message/delivery-status"):
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        chunks.append(payload.decode(charset, errors="ignore"))
                except Exception: continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                chunks.append(payload.decode(charset, errors="ignore"))
        except Exception: pass
    return "\n".join(chunks)

def extract_bounced_recipient(msg) -> Optional[str]:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "message/delivery-status":
                try:
                    payload = part.get_payload(decode=True) or b""
                    text = payload.decode("utf-8", errors="ignore")
                    m = re.search(r'Final-Recipient:\s*rfc822;\s*([^\s]+)', text, re.IGNORECASE)
                    if m: return extract_clean_email(m.group(1))
                except Exception: continue
    body_text = _get_message_text(msg)
    m = re.search(r'Mesajınız\s+([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\s+ünvanına', body_text)
    if m: return extract_clean_email(m.group(1))
    m = re.search(r'(?:reach|deliver(?:ing)? (?:your message )?to|to)\s+([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', body_text, re.IGNORECASE)
    if m: return extract_clean_email(m.group(1))
    m = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', body_text)
    if m: return extract_clean_email(m.group(0))
    return None

def _is_bounce_message(msg) -> bool:
    from_addr = (msg.get("From") or "").lower()
    subject = _decode_mime_str(msg.get("Subject") or "").lower()
    content_type = (msg.get("Content-Type") or "").lower()
    bounce_signals = [
        "mailer-daemon" in from_addr, "mail delivery subsystem" in from_addr,
        "postmaster" in from_addr, "delivery status notification" in subject,
        "delivery failure" in subject, "undelivered" in subject,
        "undeliverable" in subject, "report-type=delivery-status" in content_type,
    ]
    return any(bounce_signals)

def check_bounced_emails() -> Dict[str, Any]:
    if not ENABLE_BOUNCE_CHECK or not IMAP_USERNAME or not IMAP_PASSWORD:
        return {"checked": 0, "updated": [], "errors": [], "disabled": True}
    updated = []
    checked = 0
    errors = []
    try:
        imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        imap.login(IMAP_USERNAME, IMAP_PASSWORD)
        imap.select("INBOX")
        status, data = imap.search(None, "UNSEEN")
        if status != "OK":
            imap.logout()
            return {"checked": 0, "updated": [], "errors": ["IMAP search uğursuz oldu."]}
        msg_ids = data[0].split()
        for msg_id in msg_ids:
            try:
                status, msg_data = imap.fetch(msg_id, "(RFC822)")
                if status != "OK" or not msg_data or not msg_data[0]: continue
                raw_msg = msg_data[0][1]
                msg = email_lib.message_from_bytes(raw_msg)
                checked += 1
                if not _is_bounce_message(msg): continue
                bounced_email = extract_bounced_recipient(msg)
                if not bounced_email: continue
                carriers_res = supabase.table("carriers").select("id").eq("email", bounced_email).execute()
                carrier_ids = [c["id"] for c in (carriers_res.data or [])]
                if not carrier_ids: continue
                for cid in carrier_ids:
                    q_res = supabase.table("quotes").select("id, mail_status").eq("carrier_id", cid).execute()
                    for q in (q_res.data or []):
                        if q.get("mail_status") in ("delivered", "pending"):
                            supabase.table("quotes").update({"mail_status": "failed"}).eq("id", q["id"]).execute()
                            updated.append({"quote_id": q["id"], "carrier_id": cid, "email": bounced_email})
                imap.store(msg_id, "+FLAGS", "\\Seen")
            except Exception as inner_e:
                errors.append(str(inner_e))
                continue
        imap.logout()
    except Exception as e:
        errors.append(str(e))
    return {"checked": checked, "updated": updated, "errors": errors}

def get_sender_info_from_shipment(shipment: Optional[Dict[str, Any]]) -> Tuple[str, Optional[str]]:
    shipment = shipment or {}
    customer = shipment.get("customers") or {}
    sender_company = customer.get("company_name") or customer.get("name") or "Arachi"
    customer_email = customer.get("email")
    return sender_company, customer_email

def normalize_text(text: Any) -> str:
    if not isinstance(text, str): text = str(text)
    text = text.strip().lower()
    replacements = {"ə": "e", "ç": "c", "ş": "s", "ı": "i", "ö": "o", "ü": "u", "ğ": "g"}
    for old, new in replacements.items(): text = text.replace(old, new)
    return text

def extract_clean_email(val: Any) -> Optional[str]:
    if val is None or pd.isna(val): return None
    val_str = str(val).strip()
    if not val_str or val_str.lower() == 'nan': return None
    match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', val_str)
    if match:
        clean = match.group(0).strip().lower()
        if '@' in clean and '.' in clean: return clean
    return None

def filter_and_insert_carriers(customer_id: int, raw_carriers: List[Dict[str, Any]], skip_duplicates: bool = False) -> Dict[str, Any]:
    if not raw_carriers: raise HTTPException(status_code=400, detail="Əlavə ediləcək daşıyıcı məlumatı tapılmadı.")
    existing_emails = set()
    try:
        res1 = supabase.table("carriers").select("email").eq("customer_id", customer_id).range(0, 9999).execute()
        if res1.data:
            for item in res1.data:
                em = extract_clean_email(item.get("email"))
                if em: existing_emails.add(em)
        res2 = supabase.table("carriers").select("email").eq("customer_id", str(customer_id)).range(0, 9999).execute()
        if res2.data:
            for item in res2.data:
                em = extract_clean_email(item.get("email"))
                if em: existing_emails.add(em)
    except Exception as e: print("Xəta (existing_emails yoxlanarkən):", e)

    carriers_to_insert = []
    seen_in_input = set()
    duplicate_emails = []

    for item in raw_carriers:
        if not isinstance(item, dict): continue
        raw_email = item.get("email")
        clean_email = extract_clean_email(raw_email)
        if not clean_email: continue
        if clean_email in existing_emails or clean_email in seen_in_input:
            duplicate_emails.append(clean_email)
            continue
        seen_in_input.add(clean_email)
        company = item.get("name") or item.get("company_name") or "Daşıyıcı"
        if not company or str(company).lower() == 'nan' or not str(company).strip(): company = "Daşıyıcı"
        carriers_to_insert.append({"customer_id": customer_id, "company_name": str(company).strip(), "email": clean_email})

    if duplicate_emails and not skip_duplicates:
        unique_dups = ", ".join(list(set(duplicate_emails)))
        raise HTTPException(status_code=400, detail=f"Bu e-poçt ünvanı artıq bazada və ya siyahıda mövcuddur: {unique_dups}")
    if not carriers_to_insert:
        raise HTTPException(status_code=400, detail="Daxil edilən e-poçt ünvanı etibarsızdır və ya artıq mövcuddur.")
    supabase.table("carriers").insert(carriers_to_insert).execute()
    message = f"{len(carriers_to_insert)} yeni daşıyıcı uğurla əlavə edildi!"
    skipped = len(set(duplicate_emails))
    if skipped: message += f" ({skipped} təkrar email atlandı.)"
    return {"status": "success", "message": message, "added": len(carriers_to_insert), "skipped_duplicates": skipped}

def process_dataframe_and_insert(df: pd.DataFrame, customer_id: int, skip_duplicates: bool = False):
    if df.empty: raise HTTPException(status_code=400, detail="Məlumat tapılmadı və ya cədvəl boşdur.")
    normalized_columns = {col: normalize_text(col) for col in df.columns}
    email_keywords = ['email', 'e-mail', 'e-poct', 'epoct', 'e poct', 'poct', 'elaqe', 'contact', 'mail']
    email_col = next((orig for orig, norm in normalized_columns.items() if any(kw in norm for kw in email_keywords)), None)
    if not email_col: raise HTTPException(status_code=400, detail="Cədvəldə e-poçt sütunu tapılmadı.")
    company_keywords = ['company', 'sirket', 'firma', 'ad', 'name', 'carrier', 'dasiyici']
    comp_col = next((orig for orig, norm in normalized_columns.items() if any(kw in norm for kw in company_keywords)), None)
    raw_list = []
    for _, row in df.iterrows():
        raw_email_val = row[email_col] if pd.notna(row[email_col]) else ""
        clean_email = extract_clean_email(raw_email_val)
        if not clean_email: continue
        company = str(row[comp_col]).strip() if comp_col and pd.notna(row[comp_col]) else "Daşıyıcı"
        raw_list.append({"name": company, "email": clean_email})
    return filter_and_insert_carriers(customer_id, raw_list, skip_duplicates)

async def send_carrier_email_link(carrier_email: str, carrier_name: str, origin: str, destination: str, token: str, custom_body: Optional[str] = None, custom_subject: Optional[str] = None, sender_company: str = "Arachi", is_reminder: bool = False, reply_to_email: Optional[str] = None):
    quote_link = f"{BASE_URL}/carrier_quote/quote?token={token}"
    tracking_pixel_url = f"{BASE_URL}/quotes/track/{token}"
    
    # === HƏLL BURADADIR: Fərdi başlıq gəlibsə onu istifadə edirik, əks halda standartı ===
    if is_reminder:
        subject_line = f"⏰ Reminder: Submit a Proposal: {origin} - {destination}"
        text_content = f"""Dear {carrier_name},\n\nThis is a gentle reminder regarding the shipment request from {origin} to {destination}. Please kindly submit your quotation using the link below if you haven't already.\n\nThank you.\n\nBest regards,\n{sender_company}"""
    else:
        if custom_subject and custom_subject.strip():
            # Əgər müştəri custom subject göndəribsə, içindəki {{origin}} və {{destination}} taglərini dəyişdirib istifadə edirik
            subject_line = custom_subject.replace("{{origin}}", origin).replace("{{destination}}", destination)
        else:
            # Standart başlıq
            subject_line = f"📦 Submit a Proposal: {origin} - {destination}"
            
        if custom_body and custom_body.strip():
            text_content = custom_body.replace("{{company_name}}", carrier_name).replace("{{sender_company}}", sender_company).replace("{{origin}}", origin).replace("{{destination}}", destination)
        else:
            text_content = f"""Dear {carrier_name},\n\nPlease review the shipment details below and kindly complete the quotation form using the link provided.\n\nThank you.\n\nBest regards,\n{sender_company}"""

    formatted_text = text_content.replace("\n", "<br>")
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; padding: 30px; border: 1px solid #e0e0e0;">
            <div style="font-size: 15px; color: #333333; line-height: 1.6; margin-bottom: 25px;">{formatted_text}</div>
            <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #1a73e8; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Route:</strong> {origin} ➔ {destination}</p>
            </div>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{quote_link}" style="background-color: #1a73e8; color: white; padding: 12px 24px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block;">👉 Submit Your Proposal</a>
            </div>
        </div>
        <img src="{tracking_pixel_url}" width="1" height="1" style="display:none;" />
    </div>
    """
    message_kwargs = dict(subject=subject_line, recipients=[carrier_email], body=html_content, subtype=MessageType.html, from_name=(sender_company or "Arachi").strip() or "Arachi")
    if reply_to_email: message_kwargs["reply_to"] = [reply_to_email]
    message = MessageSchema(**message_kwargs)
    try:
        await fastmail.send_message(message)
        supabase.table("quotes").update({"mail_status": "delivered"}).eq("token", token).execute()
    except Exception:
        traceback.print_exc()
        supabase.table("quotes").update({"mail_status": "failed"}).eq("token", token).execute()

class ShipmentRequestCreate(BaseModel):
    customer_id: int
    origin: str
    destination: str
    cargo_type: Optional[str] = ""
    weight_kg: Optional[float] = 0.0
    volume_m3: Optional[float] = 0.0
    deadline: Optional[str] = None
    truck_type: Optional[str] = ""
    hs_code: Optional[str] = ""
    stackable: Optional[Any] = None
    shipment_type: Optional[str] = ""
    required_fields: Optional[List[Any]] = []
    send_to_all: bool = True
    send_option: Optional[str] = "all"
    also_create_link: Optional[bool] = False
    carrier_ids: Optional[List[int]] = []
    category_ids: Optional[List[int]] = []
    attachment_url: Optional[str] = None
    additional_notes: Optional[str] = ""
    note: Optional[str] = ""
    email_template_type: Optional[str] = "standard"
    email_body: Optional[str] = None
    custom_email_body: Optional[str] = None
    custom_email_subject: Optional[str] = None

class DynamicQuoteSubmit(BaseModel):
    request_id: Optional[int] = None
    price: Optional[float] = None
    currency: Optional[str] = "AZN"
    transit_time_days: Optional[int] = None
    extra_details: Optional[Dict[str, Any]] = {}

class SelectWinnerRequest(BaseModel):
    request_id: int
    quote_id: int

class DeleteCarrierRequest(BaseModel):
    customer_id: int
    carrier_id: int

class BulkDeleteCarrierRequest(BaseModel):
    customer_id: int
    carrier_ids: List[int]

class ReportGenerateRequest(BaseModel):
    customer_id: int
    report_type: str
    report_category: str = "rfq"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    rfq_ids: Optional[List[int]] = []

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class BatchReminderRequest(BaseModel):
    quote_ids: List[int]

class CategoryCreate(BaseModel):
    customer_id: int
    name: str

class CategoryDelete(BaseModel):
    customer_id: int
    category_id: int

# YENİ: Alt Kateqoriya Yaratmaq üçün
class SubCategoryCreate(BaseModel):
    category_id: int
    name: str

class CarrierSetCategory(BaseModel):
    customer_id: int
    carrier_id: int
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None # YENİ ƏLAVƏ

class CarrierBulkSetCategory(BaseModel):
    customer_id: int
    carrier_ids: List[int]
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None # YENİ ƏLAVƏ
    
class RegisterRequest(BaseModel):
    token: Optional[str] = None
    email: EmailStr
    password: str
    company_name: str
    account_type: str = "importer_exporter"   # importer_exporter | forwarder
    panel_access: str = "customer"            # forwarder üçün: both | customer | forwarder

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ChangeEmailRequest(BaseModel):
    new_email: EmailStr
    current_password: str

class CustomerQuoteCreate(BaseModel):
    customer_id: int
    request_id: int
    quote_id: int
    base_price: float
    margin_type: str
    margin_value: float
    final_price: float
    currency: str
    valid_until: Optional[str] = None
    terms_conditions: Optional[str] = ""

@app.get("/", response_class=HTMLResponse)
def get_home(): 
    if os.path.exists("static/index.html"): return FileResponse("static/index.html")
    return "index.html tapılmadı", 404

@app.get("/login", response_class=HTMLResponse)
def get_login(): 
    response = FileResponse("static/login.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/customer")
def get_customer_dashboard(): 
    response = FileResponse("static/customer.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/forwarder")
def get_forwarder_dashboard():
    response = FileResponse("static/forwarder.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/carrier_quote/quote")

def get_carrier_quote_page(token: str):
    file_path = BASE_DIR / "static" / "carrier_quote.html"
    response = FileResponse(file_path)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def _own_category(category_id, current_user: dict) -> None:
    """Kateqoriya (və ya alt kateqoriyanın əsas kateqoriyası) bu müştəriyə aiddirmi."""
    if not category_id: return
    res = supabase.table("carrier_categories").select("customer_id").eq("id", category_id).execute()
    if not res.data or str(res.data[0].get("customer_id")) != str(current_user.get("sub")):
        raise HTTPException(status_code=403, detail="Təhlükəsizlik Xəbərdarlığı: İcazə rədd edildi! Bu kateqoriya sizə aid deyil.")


def _own_sub_category(sub_id, current_user: dict) -> None:
    if not sub_id: return
    res = supabase.table("carrier_sub_categories").select("category_id").eq("id", sub_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Alt kateqoriya tapılmadı.")
    _own_category(res.data[0].get("category_id"), current_user)


@app.get("/categories/customer/{customer_id}")
def get_customer_categories(customer_id: int, current_user: dict = Depends(verify_token)):
    check_ownership(customer_id, current_user)
    try:
        res = supabase.table("carrier_categories").select("*").eq("customer_id", customer_id).order("id", desc=False).execute()
        return {"status": "success", "categories": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/categories/create")
def create_category(payload: CategoryCreate, current_user: dict = Depends(verify_token)):
    check_ownership(payload.customer_id, current_user)
    try:
        res = supabase.table("carrier_categories").insert({"customer_id": payload.customer_id, "name": payload.name}).execute()
        return {"status": "success", "category": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/categories/delete")
def delete_category(payload: CategoryDelete, current_user: dict = Depends(verify_token)):
    check_ownership(payload.customer_id, current_user)
    try:
        supabase.table("carrier_categories").delete().eq("id", payload.category_id).eq("customer_id", payload.customer_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/carriers/set-category")
def set_carrier_category(payload: CarrierSetCategory, current_user: dict = Depends(verify_token)):
    check_ownership(payload.customer_id, current_user)
    _own_category(payload.category_id if payload.category_id and payload.category_id > 0 else None, current_user)
    _own_sub_category(payload.sub_category_id if payload.sub_category_id and payload.sub_category_id > 0 else None, current_user)
    try:
        val_cat = payload.category_id if payload.category_id and payload.category_id > 0 else None
        val_sub = payload.sub_category_id if payload.sub_category_id and payload.sub_category_id > 0 else None
        
        supabase.table("carriers").update({
            "category_id": val_cat,
            "sub_category_id": val_sub
        }).eq("id", payload.carrier_id).eq("customer_id", payload.customer_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/carriers/bulk-set-category")
def bulk_set_carrier_category(payload: CarrierBulkSetCategory, current_user: dict = Depends(verify_token)):
    check_ownership(payload.customer_id, current_user)
    _own_category(payload.category_id if payload.category_id and payload.category_id > 0 else None, current_user)
    _own_sub_category(payload.sub_category_id if payload.sub_category_id and payload.sub_category_id > 0 else None, current_user)
    try:
        val_cat = payload.category_id if payload.category_id and payload.category_id > 0 else None
        val_sub = payload.sub_category_id if payload.sub_category_id and payload.sub_category_id > 0 else None
        
        if not payload.carrier_ids:
            return {"status": "success"}
            
        supabase.table("carriers").update({
            "category_id": val_cat,
            "sub_category_id": val_sub
        }).in_("id", payload.carrier_ids).eq("customer_id", payload.customer_id).execute()
        return {"status": "success"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/carrier-sub-categories")
def create_sub_category(payload: SubCategoryCreate, current_user: dict = Depends(verify_token)):
    _own_category(payload.category_id, current_user)
    try:
        # Təhlükəsizlik: Əsas kateqoriyanın mövcudluğunu və icazələri yoxlamaq olar
        res = supabase.table("carrier_sub_categories").insert({
            "category_id": payload.category_id,
            "name": payload.name
        }).execute()
        return {"status": "success", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/carrier-sub-categories/{category_id}")
def get_sub_categories(category_id: int, current_user: dict = Depends(verify_token)):
    _own_category(category_id, current_user)
    try:
        res = supabase.table("carrier_sub_categories").select("*").eq("category_id", category_id).execute()
        return {"status": "success", "data": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/carrier-sub-categories/{sub_id}")
def delete_sub_category(sub_id: int, current_user: dict = Depends(verify_token)):
    _own_sub_category(sub_id, current_user)
    try:
        supabase.table("carrier_sub_categories").delete().eq("id", sub_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customer/stats/{customer_id}")
def get_customer_stats(customer_id: int, current_user: dict = Depends(verify_token)):
    check_ownership(customer_id, current_user)
    try:
        reqs_res = supabase.table("shipment_requests").select("id, status").eq("customer_id", customer_id).execute()
        requests = reqs_res.data or []
        active_rfqs = sum(1 for r in requests if r.get("status") == "open")
        completed_shipments = sum(1 for r in requests if r.get("status") == "closed")
        
        req_ids = [r["id"] for r in requests]
        incoming_quotes_count = 0
        if req_ids:
            quotes_res = supabase.table("quotes").select("price, extra_details").in_("request_id", req_ids).execute()
            incoming_quotes_count = sum(1 for q in (quotes_res.data or []) if q.get("price") is not None or (q.get("extra_details") and q.get("extra_details").get("submitted") == True))
        
        # HƏLL: Supabase-in xəta verdiyi "not_ilike" əmrini ləğv edib, Python ilə filtrləyirik
        carriers_res = supabase.table("carriers").select("id, email").eq("customer_id", customer_id).execute()
        all_carriers = carriers_res.data or []
        filtered_carriers = [c for c in all_carriers if not c.get("email", "").startswith("public_link_")]
        
        return {
            "status": "success", 
            "active_rfqs": active_rfqs, 
            "incoming_quotes": incoming_quotes_count, 
            "completed_shipments": completed_shipments, 
            "carriers_count": len(filtered_carriers)
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customer/recent-quotes/{customer_id}")
def get_recent_quotes(customer_id: int, current_user: dict = Depends(verify_token)):
    check_ownership(customer_id, current_user)
    try:
        req_res = supabase.table("shipment_requests").select("id, origin, destination").eq("customer_id", customer_id).execute()
        req_map = {r["id"]: {"origin": r["origin"], "destination": r["destination"]} for r in (req_res.data or [])}
        if not req_map:
            return {"status": "success", "quotes": []}
        
        quotes_res = supabase.table("quotes").select("*, carriers(company_name, name)").in_("request_id", list(req_map.keys())).execute()
        quotes = quotes_res.data or []
        
        recent_quotes = []
        for q in quotes:
            extra = q.get("extra_details") or {}
            is_submitted = q.get("price") is not None or extra.get("submitted") == True
            
            if is_submitted:
                carrier = q.get("carriers") or {}
                
                # ƏSAS HƏLL: Sürücünün formda yazdığı (məsələn, "lulu") adı birinci yoxlayırıq!
                custom_name = extra.get("carrier_company")
                if custom_name:
                    carrier_name = custom_name
                else:
                    carrier_name = carrier.get("company_name") or carrier.get("name") or "Daşıyıcı"
                    
                recent_quotes.append({
                    "request_id": q["request_id"],
                    "quote_id": q["id"],
                    "origin": req_map[q["request_id"]]["origin"],
                    "destination": req_map[q["request_id"]]["destination"],
                    "carrier_name": carrier_name,
                    "price": q.get("price"),
                    "currency": q.get("currency", "AZN"),
                    "submitted_at": q.get("created_at") 
                })
        recent_quotes.sort(key=lambda x: x["quote_id"], reverse=True)
        return {"status": "success", "quotes": recent_quotes[:10]}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
def format_excel_date(date_str: Any, is_utc: bool = False, use_ampm: bool = False) -> str:
    if not date_str or str(date_str).strip() in ("-", "None", ""):
        return "-"
    s = str(date_str).strip()
    if "AM" in s or "PM" in s:
        return s
    try:
        if "T" in s:
            clean_str = s.split("+")[0].split("Z")[0].split(".")[0]
            if len(clean_str) == 16:
                clean_str += ":00"
            dt = datetime.strptime(clean_str, "%Y-%m-%dT%H:%M:%S")
        else:
            clean_str = s.split("+")[0].split("Z")[0].split(".")[0]
            if len(clean_str) == 10:
                clean_str += " 00:00:00"
            elif len(clean_str) == 16:
                clean_str += ":00"
            dt = datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
        
        if is_utc:
            dt = dt + timedelta(hours=4)
        
        if dt.hour == 0 and dt.minute == 0 and dt.second == 0 and not is_utc:
            return dt.strftime("%Y-%m-%d")
        
        if use_ampm:
            return dt.strftime("%Y-%m-%d %I:%M %p")
        else:
            return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return s.split(".")[0].replace("T", " ")

@app.post("/reports/generate")
def generate_report_data(payload: ReportGenerateRequest, current_user: dict = Depends(verify_token)):
    check_ownership(payload.customer_id, current_user)
    try:
        all_reqs_res = supabase.table("shipment_requests").select("id").eq("customer_id", payload.customer_id).order("id", desc=True).execute()
        all_reqs = all_reqs_res.data or []
        total_reqs = len(all_reqs)
        display_id_map = {req["id"]: (total_reqs - i) for i, req in enumerate(all_reqs)}
        
        query = supabase.table("shipment_requests").select("*, quotes(*, carriers(company_name, email))").eq("customer_id", payload.customer_id)
        if payload.report_type == "selected" and payload.rfq_ids:
            query = query.in_("id", payload.rfq_ids)
        res = query.order("id", desc=True).execute()
        reqs = res.data or []
        
        filtered_reqs = []
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        for r in reqs:
            created_date = r.get("created_at", "")[:10] if r.get("created_at") else ""
            if payload.report_type == "today":
                if created_date != today_str: continue
            elif payload.report_type == "date_range":
                if payload.start_date and created_date < payload.start_date: continue
                if payload.end_date and created_date > payload.end_date: continue
            filtered_reqs.append(r)
        
        report_data = []

        if payload.report_category == "rfq":
            for r in filtered_reqs:
                disp_id = display_id_map.get(r.get("id"), r.get("id"))
                req_fields = r.get("required_fields") or []
                
                opts = {"Incoterm": "", "ADR": "", "Temperature": "", "Delivery": "", "Info": ""}
                for f in req_fields:
                    f_str = str(f)
                    lower_f = f_str.lower()
                    val = ""
                    if ":" in f_str: val = f_str.split(":", 1)[1].strip()

                    if lower_f.startswith("incoterm:"): opts["Incoterm"] = val
                    elif lower_f.startswith("dangerous goods") or lower_f.startswith("adr:"): opts["ADR"] = val
                    elif lower_f.startswith("temperature") or lower_f.startswith("temp:"): opts["Temperature"] = val
                    elif lower_f.startswith("delivery deadline") or lower_f.startswith("deliv_date:"): opts["Delivery"] = val
                    elif lower_f.startswith("additional info") or lower_f.startswith("info:"): opts["Info"] = val

                stackable_val = r.get("stackable")
                if stackable_val is True: stackable_str = "Bəli"
                elif stackable_val is False: stackable_str = "Xeyr"
                else: stackable_str = "Qeyd edilməyib"

                main_notes = (r.get("additional_notes") or "").strip()
                all_notes = " | ".join(filter(None, [main_notes, opts["Info"]]))

                report_data.append({
                    "Sorğu ID": f"RFQ #{disp_id}",
                    "Marşrut": f"{r.get('origin') or ''} -> {r.get('destination') or ''}",
                    "Yük Növü": r.get("cargo_type") or "Qeyd edilməyib",
                    "Çəki (kq)": r.get("weight_kg") if r.get("weight_kg") is not None else "Qeyd edilməyib",
                    "Həcm (CBM)": r.get("volume_m3") if r.get("volume_m3") is not None else "Qeyd edilməyib",
                    "Nəqliyyat Növü": r.get("transportation_mode") or "Qeyd edilməyib",
                    "Yükləmə Tarixi": format_excel_date(r.get("deadline"), is_utc=False, use_ampm=True) if r.get("deadline") else "Qeyd edilməyib",
                    "Maşın Növü": r.get("truck_type") or "Qeyd edilməyib",
                    "HS Kod": r.get("hs_code") or "Qeyd edilməyib",
                    "Stackable": stackable_str,
                    "Yük Tipi (FTL/LTL)": r.get("shipment_type") or "Qeyd edilməyib",
                    "Incoterm": opts["Incoterm"] or "Qeyd edilməyib",
                    "ADR (Təhlükəli Yük)": opts["ADR"] or "Qeyd edilməyib",
                    "Temperatur": opts["Temperature"] or "Qeyd edilməyib",
                    "Çatdırılma Tarixi": opts["Delivery"] or "Qeyd edilməyib",
                    "Əlavə Qeydlər / Fayl": all_notes or "Qeyd edilməyib",
                    "Status": (r.get("status") or "open").upper(),
                    "Yaradılma Tarixi": format_excel_date(r.get("created_at"), is_utc=True, use_ampm=False)
                })
        else:
            for r in filtered_reqs:
                disp_id = display_id_map.get(r.get("id"), r.get("id"))
                origin = r.get("origin") or ""
                dest = r.get("destination") or ""
                route = f"{origin} -> {dest}"
                quotes = r.get("quotes") or []
                
                for q in quotes:
                    extra = q.get("extra_details") or {}
                    if q.get("price") is None and not extra.get("submitted"):
                        continue

                    carrier = q.get("carriers") or {}
                    
                    # 1. YENİ ƏLAVƏ: Əvvəlcə formdakı xüsusi adı yoxlayırıq
                    custom_name = extra.get("carrier_company")
                    if custom_name:
                        carrier_name = custom_name
                    else:
                        carrier_name = carrier.get("company_name", "Daşıyıcı")
                    
                    extra_str = "; ".join([f"{k}: {v}" for k, v in extra.items() if k not in ("submitted", "submitted_at", "is_alternative") and v])
                    if extra.get("is_alternative"): extra_str = "Alternativ təklif" + ("; " + extra_str if extra_str else "")
                    date_val = extra.get("submitted_at") or q.get("updated_at") or q.get("created_at")

                    report_data.append({
                        "Sorğu ID": f"RFQ #{disp_id}",
                        "Marşrut": route,
                        "Daşıyıcı Şirkət": carrier_name, # 2. YENİLƏNDİ: Artıq düzgün adı bura yazdırırıq
                        "Daşıyıcı Email": "-" if "public_link_" in (carrier.get("email") or "") else carrier.get("email", ""),
                        "Qiymət": q.get("price", "Yoxdur") if q.get("price") is not None else "Yoxdur",
                        "Valyuta": q.get("currency", "AZN"),
                        "Tranzit Müddəti (gün)": q.get("transit_time_days", "Qeyd edilməyib") if q.get("transit_time_days") is not None else "Qeyd edilməyib",
                        "Qalibdir?": "Bəli" if q.get("is_winner") else "Xeyr",
                        "Əlavə Detallar": extra_str if extra_str else "Yoxdur",
                        "Təklif Tarixi": format_excel_date(date_val, is_utc=True, use_ampm=False)
                    })
        return {"status": "success", "data": report_data, "category": payload.report_category}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# FREIGHT FORWARDER: PROFİL, KƏŞF, BAZAYA ƏLAVƏ
# ==========================================
FORWARDER_SERVICES = {"road", "sea", "air", "rail", "multimodal", "customs", "warehouse"}
PROFILE_PHOTO_DIR = os.path.join(UPLOAD_DIR, "profiles")
os.makedirs(PROFILE_PHOTO_DIR, exist_ok=True)
MAX_PROFILE_PHOTO_BYTES = 2 * 1024 * 1024
PROFILE_PUBLIC_COLUMNS = "id, company_name, about, services, countries, country, city, website, contact_email, phone, whatsapp, telegram, photo_url, is_verified"
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class ForwarderProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    about: Optional[str] = None
    services: Optional[List[str]] = None
    countries: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    telegram: Optional[str] = None
    is_public: Optional[bool] = None

def _clean_text(value: Optional[str], max_len: int) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", (value or "")).strip()[:max_len]

def _get_or_create_profile(customer_id: int) -> Dict[str, Any]:
    res = supabase.table("forwarder_profiles").select("*").eq("customer_id", customer_id).execute()
    if res.data:
        return res.data[0]
    cust = supabase.table("customers").select("name").eq("id", customer_id).execute()
    name = (cust.data[0].get("name") if cust.data else "") or ""
    ins = supabase.table("forwarder_profiles").insert({"customer_id": customer_id, "company_name": name}).execute()
    return ins.data[0]

def _require_importer(current_user: dict):
    """Kəşf yalnız idxalçı/ixracçı hesabları üçündür (forwarder hesablarında bu bölmə yoxdur)."""
    if (current_user.get("account_type") or "importer_exporter") != "importer_exporter":
        raise HTTPException(status_code=403, detail="Daşıyıcıları kəşf et bölməsi yalnız idxalçı/ixracçı hesabları üçündür.")

@app.get("/forwarder/profile")
def get_my_forwarder_profile(current_user: dict = Depends(verify_forwarder_token)):
    try:
        return {"status": "success", "profile": _get_or_create_profile(int(current_user["sub"]))}
    except HTTPException as he: raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Profil yüklənmədi: {str(e)}")

@app.put("/forwarder/profile")
def update_my_forwarder_profile(payload: ForwarderProfileUpdate, current_user: dict = Depends(verify_forwarder_token)):
    try:
        customer_id = int(current_user["sub"])
        _get_or_create_profile(customer_id)
        upd: Dict[str, Any] = {}

        if payload.company_name is not None:
            name = _clean_text(payload.company_name, 150)
            if not name: raise HTTPException(status_code=400, detail="Şirkət adı boş ola bilməz.")
            upd["company_name"] = name
        if payload.about is not None: upd["about"] = _clean_text(payload.about, 2000)
        if payload.countries is not None: upd["countries"] = _clean_text(payload.countries, 300)
        if payload.country is not None: upd["country"] = _clean_text(payload.country, 80)
        if payload.city is not None: upd["city"] = _clean_text(payload.city, 80)
        if payload.phone is not None: upd["phone"] = _clean_text(payload.phone, 40)
        if payload.whatsapp is not None: upd["whatsapp"] = _clean_text(payload.whatsapp, 60)
        if payload.telegram is not None: upd["telegram"] = _clean_text(payload.telegram, 80)
        if payload.services is not None:
            upd["services"] = [s for s in dict.fromkeys(payload.services) if s in FORWARDER_SERVICES]
        if payload.website is not None:
            site = _clean_text(payload.website, 200)
            if re.match(r"^s*(javascript|data|vbscript|file|blob|ftp)s*:", site, re.I):
                raise HTTPException(status_code=400, detail="Veb sayt ünvanı düzgün deyil.")
            if site and not re.match(r"^https?://", site, re.I): site = "https://" + site
            if site and not re.match(r"^https?://[^\s<>\"']+$", site, re.I):
                raise HTTPException(status_code=400, detail="Veb sayt ünvanı düzgün deyil.")
            upd["website"] = site
        if payload.contact_email is not None:
            em = _clean_text(payload.contact_email, 150).lower()
            if em and not _EMAIL_RE.match(em):
                raise HTTPException(status_code=400, detail="Əlaqə e-poçtu düzgün deyil.")
            upd["contact_email"] = em
        if payload.is_public is not None: upd["is_public"] = bool(payload.is_public)

        if not upd: raise HTTPException(status_code=400, detail="Dəyişiklik göndərilməyib.")
        upd["updated_at"] = datetime.utcnow().isoformat()
        res = supabase.table("forwarder_profiles").update(upd).eq("customer_id", customer_id).execute()
        return {"status": "success", "message": "Profil yadda saxlanıldı.", "profile": res.data[0] if res.data else None}
    except HTTPException as he: raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Profil yadda saxlanmadı: {str(e)}")

def _delete_profile_photo_file(photo_url: Optional[str]):
    try:
        if photo_url and photo_url.startswith("/uploads/profiles/"):
            path = os.path.join(PROFILE_PHOTO_DIR, os.path.basename(photo_url))
            if os.path.isfile(path): os.remove(path)
    except Exception:
        traceback.print_exc()

@app.post("/forwarder/profile/photo")
@limiter.limit("10/minute")
async def upload_forwarder_photo(request: Request, file: UploadFile = File(...), current_user: dict = Depends(verify_forwarder_token)):
    customer_id = int(current_user["sub"])
    data = await file.read(MAX_PROFILE_PHOTO_BYTES + 1)
    if len(data) > MAX_PROFILE_PHOTO_BYTES:
        raise HTTPException(status_code=400, detail="Şəkil çox böyükdür (maksimum 2 MB).")
    # Fayl tipi uzantıya yox, real məzmuna görə təyin olunur
    if data[:8] == b"\x89PNG\r\n\x1a\n": ext = ".png"
    elif data[:3] == b"\xff\xd8\xff": ext = ".jpg"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP": ext = ".webp"
    else: raise HTTPException(status_code=400, detail="Yalnız PNG, JPG və ya WEBP şəkil yükləyə bilərsiniz.")
    try:
        profile = _get_or_create_profile(customer_id)
        filename = f"{uuid.uuid4().hex}{ext}"
        with open(os.path.join(PROFILE_PHOTO_DIR, filename), "wb") as f: f.write(data)
        new_url = f"/uploads/profiles/{filename}"
        supabase.table("forwarder_profiles").update({"photo_url": new_url, "updated_at": datetime.utcnow().isoformat()}).eq("customer_id", customer_id).execute()
        _delete_profile_photo_file(profile.get("photo_url"))
        return {"status": "success", "photo_url": new_url}
    except HTTPException as he: raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Şəkil yüklənmədi: {str(e)}")

@app.delete("/forwarder/profile/photo")
def delete_forwarder_photo(current_user: dict = Depends(verify_forwarder_token)):
    customer_id = int(current_user["sub"])
    profile = _get_or_create_profile(customer_id)
    supabase.table("forwarder_profiles").update({"photo_url": None, "updated_at": datetime.utcnow().isoformat()}).eq("customer_id", customer_id).execute()
    _delete_profile_photo_file(profile.get("photo_url"))
    return {"status": "success"}

@app.get("/forwarders/discover")
def discover_forwarders(q: str = "", service: str = "", limit: int = 24, offset: int = 0, current_user: dict = Depends(verify_token)):
    _require_importer(current_user)
    try:
        limit = max(1, min(int(limit), 50)); offset = max(0, int(offset))
        query = supabase.table("forwarder_profiles").select(PROFILE_PUBLIC_COLUMNS).eq("is_public", True).neq("company_name", "")
        if service in FORWARDER_SERVICES:
            query = query.contains("services", [service])
        # axtarış sözündən PostgREST filtrini pozan simvollar təmizlənir
        q_clean = re.sub(r"[^\w\s\.\-]", " ", q or "", flags=re.UNICODE).strip()[:60]
        if q_clean:
            like = f"%{q_clean}%"
            query = query.or_(f"company_name.ilike.{like},about.ilike.{like},countries.ilike.{like},city.ilike.{like},country.ilike.{like}")
        res = query.order("is_verified", desc=True).order("id", desc=True).range(offset, offset + limit - 1).execute()
        items = res.data or []

        # Artıq müştərinin bazasında olanlar işarələnir
        in_base = set()
        base = supabase.table("carriers").select("email").eq("customer_id", int(current_user["sub"])).range(0, 9999).execute()
        for row in (base.data or []):
            em = extract_clean_email(row.get("email"))
            if em: in_base.add(em)
        for it in items:
            em = extract_clean_email(it.get("contact_email"))
            it["can_add"] = bool(em)
            it["already_in_base"] = bool(em and em in in_base)
        return {"status": "success", "forwarders": items, "has_more": len(items) == limit}
    except HTTPException as he: raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Axtarış xətası: {str(e)}")

@app.post("/forwarders/{profile_id}/add-to-base")
@limiter.limit("30/minute")
def add_forwarder_to_base(request: Request, profile_id: int, current_user: dict = Depends(verify_token)):
    _require_importer(current_user)
    res = supabase.table("forwarder_profiles").select("company_name, contact_email, is_public").eq("id", profile_id).execute()
    prof = res.data[0] if res.data else None
    if not prof or not prof.get("is_public"):
        raise HTTPException(status_code=404, detail="Forwarder tapılmadı.")
    email = extract_clean_email(prof.get("contact_email"))
    if not email:
        raise HTTPException(status_code=400, detail="Bu forwarder əlaqə e-poçtu göstərməyib, ona görə bazaya əlavə etmək mümkün deyil.")
    return filter_and_insert_carriers(int(current_user["sub"]), [{"name": prof.get("company_name") or "Daşıyıcı", "email": email}])

# ==========================================
# Aİ (ARACHI V2) İNTEQRASİYASI: SSO
# ==========================================
V2_BASE_URL = os.getenv("V2_BASE_URL", "https://app.v2.arachi.co").rstrip("/")
V2_SSO_SECRET = os.getenv("V2_SSO_SECRET", "")      # arachi.co və v2 arasında ortaq gizli açar (.env-də saxlanır)
AI_SSO_AUDIENCE = "arachi-v2"
AI_SSO_TTL_SECONDS = 60          # bilet yalnız 1 dəqiqə etibarlıdır və bir dəfə istifadə olunur
AI_SESSION_HOURS = 12            # v2-nin arachi.co API-sinə girişi üçün verilən token ömrü

def _require_ai_customer(customer_id: int) -> Dict[str, Any]:
    """Aİ yalnız müştəri paneli olan və 'pro' planda olan hesablar üçündür. Plan hər dəfə bazadan təzədən yoxlanılır."""
    res = supabase.table("customers").select("id, email, name, plan, customer_access, forwarder_access, account_type").eq("id", customer_id).execute()
    user = res.data[0] if res.data else None
    if not user:
        raise HTTPException(status_code=404, detail="Hesab tapılmadı.")
    if user.get("customer_access") is False:
        raise HTTPException(status_code=403, detail="Bu hesabın müştəri panelinə girişi yoxdur.")
    if (user.get("plan") or "basic") != "pro":
        raise HTTPException(status_code=403, detail="Aİ funksiyası yalnız Pro plan üçün aktivdir.")
    return user

@app.post("/api/ai/launch")
@limiter.limit("20/minute")
def ai_launch(request: Request, current_user: dict = Depends(verify_token)):
    """'Aİ istifadə et' düyməsi: qısa ömürlü, birdəfəlik imzalı bilet yaradır və v2-nin giriş ünvanını qaytarır."""
    if not V2_SSO_SECRET:
        raise HTTPException(status_code=503, detail="Aİ inteqrasiyası hələ qurulmayıb.")
    user = _require_ai_customer(int(current_user["sub"]))
    now = datetime.utcnow()
    ticket = jwt.encode({
        "iss": "arachi.co", "aud": AI_SSO_AUDIENCE, "typ": "v2-sso",
        "sub": str(user["id"]), "email": user["email"], "name": user.get("name") or "",
        "jti": uuid.uuid4().hex, "iat": now, "exp": now + timedelta(seconds=AI_SSO_TTL_SECONDS),
    }, V2_SSO_SECRET, algorithm="HS256")
    return {"status": "success", "url": f"{V2_BASE_URL}/sso?ticket={ticket}"}

class AiExchangeRequest(BaseModel):
    ticket: str

@app.post("/api/ai/exchange")
@limiter.limit("60/minute")
def ai_exchange(request: Request, body: AiExchangeRequest):
    """Yalnız v2 SERVERİ çağırır (brauzer yox): biletdə imzanı, vaxtı, istifadə olunmamasını və planı yoxlayır,
    sonra istifadəçi adından arachi.co API-sinə giriş üçün adi token qaytarır."""
    if not V2_SSO_SECRET:
        raise HTTPException(status_code=503, detail="Aİ inteqrasiyası hələ qurulmayıb.")
    supplied = (request.headers.get("x-service-secret") or "").encode()
    if not hmac.compare_digest(supplied, V2_SSO_SECRET.encode()):
        raise HTTPException(status_code=403, detail="İcazə yoxdur.")
    try:
        claims = jwt.decode(body.ticket, V2_SSO_SECRET, algorithms=["HS256"], audience=AI_SSO_AUDIENCE,
                            issuer="arachi.co", options={"require": ["exp", "jti", "sub"]})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Giriş biletinin vaxtı bitib. arachi.co-dan yenidən 'Aİ istifadə et' basın.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Etibarsız giriş bileti.")
    if claims.get("typ") != "v2-sso":
        raise HTTPException(status_code=401, detail="Etibarsız giriş bileti.")
    user = _require_ai_customer(int(claims["sub"]))
    try:   # birdəfəlik: eyni bilet ikinci dəfə bazaya yazıla bilmir (jti unikaldır)
        supabase.table("ai_sso_jti").insert({"jti": claims["jti"], "customer_id": user["id"]}).execute()
    except Exception:
        raise HTTPException(status_code=401, detail="Bu giriş bileti artıq istifadə edilib.")
    token = create_access_token({
        "sub": str(user["id"]), "role": "customer", "email": user["email"],
        "account_type": user.get("account_type") or "importer_exporter",
        "customer_access": True, "forwarder_access": user.get("forwarder_access") is True,
        "plan": "pro", "via": "ai",
    }, expires_delta=timedelta(hours=AI_SESSION_HOURS))
    return {"status": "success", "token": token, "expires_in": AI_SESSION_HOURS * 3600,
            "user": {"id": user["id"], "email": user["email"], "name": user.get("name") or "", "plan": "pro"}}

@app.post("/carriers/manual")
async def add_carriers_manual(request: Request, current_user: dict = Depends(verify_token)):
    try:
        body = {}
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type: body = await request.json()
        else:
            form = await request.form()
            body = dict(form)
            if "carriers" in body and isinstance(body["carriers"], str):
                try: body["carriers"] = json.loads(body["carriers"])
                except: body["carriers"] = []

        customer_id = body.get("customer_id") or request.query_params.get("customer_id")
        if not customer_id: raise HTTPException(status_code=400, detail="customer_id tapılmadı.")
        check_ownership(int(customer_id), current_user)

        carriers = body.get("carriers")
        if not carriers:
            email = body.get("email")
            name = body.get("name") or body.get("company_name") or "Daşıyıcı"
            carriers = [{"name": name, "email": email}] if email else []

        skip = str(body.get("skip_duplicates") or request.query_params.get("skip_duplicates") or "").lower() in ("1", "true", "yes")
        return filter_and_insert_carriers(int(customer_id), carriers, skip)
    except HTTPException as he: raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/carriers/upload-excel")
async def upload_carriers_excel(request: Request, current_user: dict = Depends(verify_token)):
    try:
        form = await request.form()
        customer_id = form.get("customer_id") or request.query_params.get("customer_id")
        if not customer_id: raise HTTPException(status_code=400, detail="customer_id əskikdir.")
        check_ownership(int(customer_id), current_user)

        file = form.get("file")
        contents = await file.read()
        filename = getattr(file, "filename", "file.xlsx")
        df = pd.read_csv(io.BytesIO(contents)) if filename.lower().endswith('.csv') else pd.read_excel(io.BytesIO(contents))
        skip = str(form.get("skip_duplicates") or request.query_params.get("skip_duplicates") or "").lower() in ("1", "true", "yes")
        return process_dataframe_and_insert(df, int(customer_id), skip)
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(status_code=400, detail=f"Fayl oxunarkən xəta: {str(e)}")

@app.post("/carriers/upload-text")
async def upload_carriers_text(request: Request, current_user: dict = Depends(verify_token)):
    try:
        body = {}
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type: body = await request.json()
        else: body = dict(await request.form())
        
        customer_id = body.get("customer_id") or request.query_params.get("customer_id")
        if not customer_id: raise HTTPException(status_code=400, detail="customer_id tələb olunur.")
        check_ownership(int(customer_id), current_user)

        raw_text = body.get("raw_text") or body.get("text") or request.query_params.get("raw_text") or request.query_params.get("text") or ""
        lines = raw_text.strip().split("\n")
        raw_list = []
        for line in lines:
            line = line.strip()
            if not line: continue
            parts = [p.strip() for p in re.split(r'[\t,;|]', line) if p.strip()]
            email, name = None, "Daşıyıcı"
            for part in parts:
                extracted = extract_clean_email(part)
                if extracted:
                    email = extracted
                    break
            if not email: continue
            other_parts = [p for p in parts if extract_clean_email(p) != email]
            if other_parts: name = other_parts[0]
            raw_list.append({"name": name, "email": email})

        if not raw_list:
            try:
                df = pd.read_csv(io.StringIO(raw_text), sep="\t")
                if len(df.columns) == 1: df = pd.read_csv(io.StringIO(raw_text), sep=",")
                return process_dataframe_and_insert(df, int(customer_id))
            except Exception: raise HTTPException(status_code=400, detail="Məlumat formatı düzgün deyil.")
        return filter_and_insert_carriers(int(customer_id), raw_list)
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(status_code=400, detail=f"Xəta: {str(e)}")

@app.post("/carriers/delete")
def delete_customer_carrier(payload: DeleteCarrierRequest, current_user: dict = Depends(verify_token)):
    check_ownership(payload.customer_id, current_user)
    try:
        supabase.table("carriers").delete().eq("id", payload.carrier_id).eq("customer_id", payload.customer_id).execute()
        return {"status": "success", "message": "Daşıyıcı bazadan uğurla silindi!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/carriers/bulk-delete")
def bulk_delete_customer_carriers(payload: BulkDeleteCarrierRequest, current_user: dict = Depends(verify_token)):
    check_ownership(payload.customer_id, current_user)
    try:
        if not payload.carrier_ids:
            return {"status": "success", "message": "Silinəcək daşıyıcı seçilməyib."}
        supabase.table("carriers").delete().in_("id", payload.carrier_ids).eq("customer_id", payload.customer_id).execute()
        return {"status": "success", "message": f"{len(payload.carrier_ids)} daşıyıcı bazadan uğurla silindi!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Silinmə zamanı xəta: {str(e)}")

@app.get("/carriers/customer/{customer_id}")
def get_customer_carriers(customer_id: int, current_user: dict = Depends(verify_token)):
    check_ownership(customer_id, current_user)
    try:
        # Bütün daşıyıcıları bazadan çəkirik
        res = supabase.table("carriers").select("*").eq("customer_id", customer_id).range(0, 9999).execute()
        all_carriers = res.data or []
        
        # Python vasitəsilə yalnız "public_link" OLMAYANLARI saxlayırıq (Qüsursuz üsul)
        filtered_carriers = [c for c in all_carriers if not c.get("email", "").startswith("public_link_")]
        
        return filtered_carriers
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/requests/upload-attachment")
async def upload_request_attachment(file: UploadFile = File(...), current_user: dict = Depends(verify_token)):
    await validate_file(file)
    try:
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as buffer: buffer.write(await file.read())
        return {"status": "success", "attachment_url": f"/uploads/{unique_filename}", "filename": file.filename}
    except Exception as e: raise HTTPException(status_code=500, detail=f"Fayl yüklənərkən xəta: {str(e)}")

# Aİ ilə avtomatik doldurma üçün ortaq təlimat (həm fayl, həm də mətn analizi istifadə edir)
AI_PARSE_PROMPT = """Sən peşəkar logistika assistentisən. Sənə verilən sənədi/mətni böyük diqqətlə oxu və aşağıdakı qaydalara əməl edərək YALNIZ təmiz JSON formatında cavab qaytar.
    Heç bir əlavə markdown (məsələn ```json) və ya izahat yazma!

    Qaydalar:
    - Origin və destination hissələrində şəhər və ölkəni dəqiq təyin et. Mətn hansı dildə yazılıbsa, həmin dildə yaz (məsələn Azərbaycanca yazılıbsa "Bakı, Azərbaycan", ingiliscə yazılıbsa "Baku, Azerbaijan").
    - weight_kg yalnız ədəd olmalıdır (əgər ton ilədirsə kq-a çevir, məsələn 1.5 ton = 1500). Yoxdursa null qoy.
    - volume_m3 yalnız rəqəm (miqdar) olmalıdır və "volume_type" ilə birlikdə işləyir.
    - volume_type yalnız "CBM" və ya "Palet" ola bilər:
        * Yük palet / pallet / паллет / поддон ilə ifadə olunubsa (məsələn "10 palet mal", "10 pallets of goods") volume_type = "Palet" və volume_m3 = paletlərin SAYI (məsələn 10).
        * Həcm kub metr / m3 / m³ / CBM ilə verilibsə volume_type = "CBM" və volume_m3 = həmin rəqəm.
        * Heç biri göstərilməyibsə volume_m3 = null və volume_type = "CBM".
    - "cargo_type" yalnız yükün NÖVÜNÜ/təsvirini göstərməlidir (məsələn "Tekstil", "Electronics"). Miqdarı (palet sayı, çəki, həcm) cargo_type-a YAZMA. Yalnız "10 palet mal" kimi ümumi ifadə varsa cargo_type = "Mal" (ingiliscə mətndə "Goods").
    - DİL QAYDASI: "cargo_type" və "additional_notes" xanalarını sənəddəki/mətndəki ORİJİNAL DİLDƏ saxla, TƏRCÜMƏ ETMƏ. Azərbaycanca yazılıbsa Azərbaycanca, ingiliscə yazılıbsa ingiliscə, rusca yazılıbsa rusca yaz. Mətn qarışıqdırsa ən çox işlənən dildən istifadə et.

    JSON Formatı:
    {
        "origin": "Yükləmə yeri",
        "destination": "Boşaltma yeri",
        "cargo_type": "Yükün növü (mətnin öz dilində)",
        "weight_kg": 0.0,
        "volume_m3": 0.0,
        "volume_type": "CBM və ya Palet",
        "transportation_mode": "Quru (Road) / Hava (Air) / Su/Dəniz (Sea) / Dəmiryolu (Rail)",
        "truck_type": "Maşın növü",
        "hs_code": "HS Kod",
        "stackable": "Stackable / Non-stackable",
        "shipment_type": "FTL / LTL / FCL / LCL",
        "incoterm": "Incoterm",
        "adr": "ADR sinfi",
        "temperature": "Temperatur",
        "deadline": "YYYY-MM-DDTHH:MM",
        "additional_notes": "Əlavə qeydlər (mətnin öz dilində)"
    }"""


@app.post("/requests/parse-ai")
@limiter.limit("5/minute")
async def parse_document_with_ai(request: Request, file: UploadFile = File(...), current_user: dict = Depends(verify_token)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Server xətası: OpenAI API açarı təyin olunmayıb.")

    await validate_file(file)
    ext = os.path.splitext(file.filename)[1].lower()

    # TƏKMİLLƏŞDİRİLMİŞ VƏ SƏRT PROMPT:
    prompt = AI_PARSE_PROMPT

    try:
        text_content = ""
        image_content = None

        if ext in [".xls", ".xlsx", ".csv"]:
            contents_bytes = await file.read()
            df = pd.read_csv(io.BytesIO(contents_bytes)) if ext == ".csv" else pd.read_excel(io.BytesIO(contents_bytes))
            text_content = df.to_string()
        elif ext == ".txt":
            text_content = (await file.read()).decode("utf-8", errors="ignore")
        elif ext == ".pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
            text_content = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            if not text_content.strip():
                raise HTTPException(status_code=400, detail="PDF faylından mətn oxunmadı.")
        elif ext in [".png", ".jpg", ".jpeg"]:
            contents_bytes = await file.read()
            base64_encoded = base64.b64encode(contents_bytes).decode('utf-8')
            mime = "image/jpeg" if ext == ".jpg" else file.content_type
            image_content = f"data:{mime};base64,{base64_encoded}"
        else:
            raise HTTPException(status_code=400, detail="Dəstəklənməyən fayl formatı.")

        messages = [{"role": "system", "content": prompt}]

        if image_content:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Bu sənədi təhlil et və tələb olunan JSON formatını doldur:"},
                    {"type": "image_url", "image_url": {"url": image_content}}
                ]
            })
        else:
            messages.append({
                "role": "user",
                "content": f"Aşağıdakı sənəd məzmununu təhlil et:\n\n{text_content}"
            })

        # === BURADA TEMPERATURE: 0.0 ƏLAVƏ OLUNDU ===
        response = await aclient.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.0, 
            response_format={ "type": "json_object" } 
        )

        res_text = response.choices[0].message.content.strip()
        parsed_json = json.loads(res_text)

        return {"status": "success", "data": parsed_json}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Aİ düzgün formatda cavab qaytarmadı.")
    except HTTPException as he:
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Aİ analizi xətası: {str(e)}")


class TextParseRequest(BaseModel):
    raw_text: str

@app.post("/requests/parse-ai-text")
@limiter.limit("5/minute")
async def parse_text_with_ai(request: Request, payload: TextParseRequest, current_user: dict = Depends(verify_token)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Server xətası: OpenAI API açarı təyin olunmayıb.")

    if not payload.raw_text or not payload.raw_text.strip():
        raise HTTPException(status_code=400, detail="Analiz üçün mətn daxil edilməyib.")

    prompt = AI_PARSE_PROMPT
    
    try:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Aşağıdakı logistika sorğu mətnini təhlil et:\n\n{payload.raw_text}"}
        ]

        response = await aclient.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.0, 
            response_format={ "type": "json_object" } 
        )

        res_text = response.choices[0].message.content.strip()
        parsed_json = json.loads(res_text)

        return {"status": "success", "data": parsed_json}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Aİ düzgün formatda cavab qaytarmadı.")
    except HTTPException as he:
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Aİ analizi xətası: {str(e)}")
        
def create_public_link_quote(customer_id: int, request_id: int, all_carriers: list) -> str:
    """Sorğu üçün ictimai (public) təklif linki yaradır və həmin linkin URL-ni qaytarır.
    Yalnız link rejimində də, e-poçt + link (hibrid) rejimində də istifadə olunur."""
    generic_email = f"public_link_{customer_id}@arachi.local"
    pub_carrier = next((c for c in all_carriers if c.get("email") == generic_email), None)

    if not pub_carrier:
        ins_res = supabase.table("carriers").insert({
            "customer_id": customer_id,
            "company_name": "🌐 İctimai Link (Public)",
            "email": generic_email
        }).execute()
        pub_carrier_id = ins_res.data[0]["id"]
    else:
        pub_carrier_id = pub_carrier["id"]

    unique_token = str(uuid.uuid4())
    supabase.table("quotes").insert({
        "request_id": request_id,
        "carrier_id": pub_carrier_id,
        "token": unique_token,
        "mail_status": "delivered",
        "is_viewed": False
    }).execute()

    return f"{BASE_URL}/carrier_quote/quote?token={unique_token}&public=1"

@app.post("/requests/create")
async def create_shipment_request(payload: ShipmentRequestCreate, background_tasks: BackgroundTasks = BackgroundTasks(), current_user: dict = Depends(verify_token)):
    check_ownership(payload.customer_id, current_user)
    try:
        parsed_required = []
        for item in (payload.required_fields or []):
            if isinstance(item, dict): parsed_required.append(", ".join([f"{k}: {v}" for k, v in item.items()]))
            else: parsed_required.append(str(item))

        final_note = payload.additional_notes or payload.note or ""
        deadline_val = payload.deadline
        if deadline_val == "" or deadline_val is None: deadline_val = None
        elif deadline_val and deadline_val in final_note and ("loading" in final_note.lower() or "tarix" in final_note.lower()): deadline_val = None

        stackable_val = payload.stackable
        if isinstance(stackable_val, str):
            if stackable_val.strip() == "" or stackable_val.lower() == "none": stackable_val = None
            else: stackable_val = stackable_val.lower() in ["true", "1", "yes", "on"]

        response = supabase.table("shipment_requests").insert({
            "customer_id": payload.customer_id, "origin": payload.origin, "destination": payload.destination,
            "cargo_type": payload.cargo_type, "weight_kg": payload.weight_kg, "volume_m3": payload.volume_m3,
            "deadline": deadline_val, "truck_type": payload.truck_type, "hs_code": payload.hs_code,
            "stackable": stackable_val, "shipment_type": payload.shipment_type, "required_fields": parsed_required,
            "attachment_url": payload.attachment_url, "additional_notes": final_note, "status": "open"
        }).execute()
        
        shipment_data = response.data[0]
        request_id = shipment_data["id"]

        cust_res = supabase.table("customers").select("*").eq("id", payload.customer_id).execute()
        sender_company, customer_email = "Arachi", None
        if cust_res.data:
            c_data = cust_res.data[0]
            sender_company = c_data.get("company_name") or c_data.get("name") or "Arachi"
            customer_email = c_data.get("email")

        all_carriers = supabase.table("carriers").select("*").eq("customer_id", payload.customer_id).range(0, 9999).execute().data or []
        
        send_opt = getattr(payload, "send_option", "all")

        # --- YENİ: LİNK YARATMA REJİMİ (yalnız link) ---
        if send_opt == "public_link":
            public_url = create_public_link_quote(payload.customer_id, request_id, all_carriers)
            
            return {
                "status": "success", 
                "message": f"Sorğu #{request_id} yaradıldı!", 
                "public_link": public_url,
                "request_details": shipment_data
            }

        # --- YENİ: yalnız sorğunu yarat, heç nə göndərmə (Aİ agent göndərməni ayrıca təsdiqlə edir) ---
        if send_opt == "none":
            return {"status": "success", "message": f"Sorğu #{request_id} yaradıldı.", "emailed_count": 0, "request_details": shipment_data}

        # --- KÖHNƏ: STANDART EMAİL GÖNDƏRMƏ REJİMİ ---
        if send_opt == "category":
            cat_ids = set(payload.category_ids or [])
            target_carriers = [c for c in all_carriers if c.get("category_id") in cat_ids]
        elif send_opt == "selected" or not payload.send_to_all:
            selected_ids = set(payload.carrier_ids or [])
            target_carriers = [c for c in all_carriers if c.get("id") in selected_ids]
        else:
            target_carriers = all_carriers

        if not target_carriers:
            raise HTTPException(status_code=400, detail="Seçilmiş kriteriyalara uyğun daşıyıcı tapılmadı. Zəhmət olmasa ən azı 1 daşıyıcı seçin.")

        active_custom_body = payload.custom_email_body or payload.email_body
        active_custom_subject = payload.custom_email_subject

        for carrier in target_carriers:
            unique_token = str(uuid.uuid4())
            carrier_name = carrier.get("company_name") or "Daşıyıcı"
            carrier_email = carrier.get("email")
            initial_status = "pending" if carrier_email else "failed"
            supabase.table("quotes").insert({"request_id": request_id, "carrier_id": carrier["id"], "token": unique_token, "mail_status": initial_status, "is_viewed": False}).execute()

            if carrier_email:
                background_tasks.add_task(
                    send_carrier_email_link, carrier_email=carrier_email, carrier_name=carrier_name,
                    origin=payload.origin, destination=payload.destination, token=unique_token,
                    custom_body=active_custom_body, custom_subject=active_custom_subject, 
                    sender_company=sender_company, reply_to_email=customer_email
                )

        result = {"status": "success", "message": f"Sorğu #{request_id} yaradıldı. {len(target_carriers)} daşıyıcıya təklif linki göndərildi!", "emailed_count": len(target_carriers), "request_details": shipment_data}

        # --- YENİ: HİBRİD REJİM - seçilmiş daşıyıcılara e-poçt + paylaşmaq üçün link ---
        if payload.also_create_link:
            result["public_link"] = create_public_link_quote(payload.customer_id, request_id, all_carriers)
            result["message"] += " Paylaşmaq üçün link də yaradıldı."

        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class SendRequestPayload(BaseModel):
    carrier_ids: Optional[List[int]] = []
    category_ids: Optional[List[int]] = []
    send_to_all: bool = False
    also_create_link: Optional[bool] = False


def _own_request(request_id: int, current_user: dict) -> dict:
    res = supabase.table("shipment_requests").select("*").eq("id", request_id).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Sorğu tapılmadı.")
    check_ownership(res.data[0]["customer_id"], current_user)
    return res.data[0]


def _own_quote(quote_id: int, current_user: dict) -> dict:
    res = supabase.table("quotes").select("*").eq("id", quote_id).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Təklif qeydi tapılmadı.")
    _own_request(res.data[0]["request_id"], current_user)
    return res.data[0]


@app.post("/requests/{request_id}/send")
async def send_existing_request(request_id: int, payload: SendRequestPayload, background_tasks: BackgroundTasks, current_user: dict = Depends(verify_token)):
    """Əvvəl yaradılmış sorğunu daşıyıcılara göndərir (Aİ agent üçün). Artıq göndərilmiş daşıyıcılara təkrar getmir."""
    try:
        shipment = _own_request(request_id, current_user)
        customer_id = shipment["customer_id"]
        cust = (supabase.table("customers").select("*").eq("id", customer_id).execute().data or [{}])[0]
        sender_company = cust.get("company_name") or cust.get("name") or "Arachi"
        customer_email = cust.get("email")
        all_carriers = supabase.table("carriers").select("*").eq("customer_id", customer_id).range(0, 9999).execute().data or []
        real = [c for c in all_carriers if "public_link_" not in (c.get("email") or "")]
        if payload.send_to_all: targets = real
        elif payload.category_ids: targets = [c for c in real if c.get("category_id") in set(payload.category_ids)]
        else: targets = [c for c in real if c.get("id") in set(payload.carrier_ids or [])]
        already = {q["carrier_id"] for q in (supabase.table("quotes").select("carrier_id").eq("request_id", request_id).execute().data or [])}
        skipped = [c for c in targets if c["id"] in already]
        targets = [c for c in targets if c["id"] not in already]
        if not targets and not payload.also_create_link:
            raise HTTPException(status_code=400, detail="Göndəriləcək yeni daşıyıcı tapılmadı (seçilənlərə artıq göndərilib və ya seçim boşdur).")
        sent = []
        for carrier in targets:
            unique_token = str(uuid.uuid4())
            email = carrier.get("email")
            supabase.table("quotes").insert({"request_id": request_id, "carrier_id": carrier["id"], "token": unique_token, "mail_status": "pending" if email else "failed", "is_viewed": False}).execute()
            if email:
                background_tasks.add_task(
                    send_carrier_email_link, carrier_email=email, carrier_name=carrier.get("company_name") or "Daşıyıcı",
                    origin=shipment["origin"], destination=shipment["destination"], token=unique_token,
                    sender_company=sender_company, reply_to_email=customer_email)
            sent.append({"carrier_id": carrier["id"], "company_name": carrier.get("company_name"), "email": email, "token": unique_token})
        result = {"status": "success", "request_id": request_id, "sent": sent, "skipped_already_sent": [c["id"] for c in skipped]}
        if payload.also_create_link:
            result["public_link"] = create_public_link_quote(customer_id, request_id, all_carriers)
        return result
    except HTTPException: raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Göndərmə xətası: {e}")


@app.post("/requests/{request_id}/public-link")
def create_request_public_link(request_id: int, current_user: dict = Depends(verify_token)):
    shipment = _own_request(request_id, current_user)
    try:
        all_carriers = supabase.table("carriers").select("*").eq("customer_id", shipment["customer_id"]).range(0, 9999).execute().data or []
        return {"status": "success", "public_link": create_public_link_quote(shipment["customer_id"], request_id, all_carriers)}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Link yaratma xətası: {e}")


@app.get("/requests/customer/{customer_id}")
def get_customer_requests(customer_id: int, current_user: dict = Depends(verify_token)):
    check_ownership(customer_id, current_user)
    res = supabase.table("shipment_requests").select("*, quotes(id, price, extra_details, quote_history)").eq("customer_id", customer_id).order("id", desc=True).execute()
    requests = res.data or []
    for req in requests:
        valid_quotes = [q for q in (req.get("quotes") or []) if q.get("price") is not None or (q.get("extra_details") and q.get("extra_details").get("submitted") == True)]
        req["quotes_count"] = len(valid_quotes)
        if "quotes" in req: del req["quotes"]
    return {"status": "success", "requests": requests}

@app.get("/requests/carriers-status/{request_id}")
def get_request_carriers_status(request_id: int, current_user: dict = Depends(verify_token)):
    _own_request(request_id, current_user)
    try:
        quotes_res = supabase.table("quotes").select("*, carriers(*)").eq("request_id", request_id).execute()
        result_carriers = []
        has_public_link = False
        
        for item in (quotes_res.data or []):
            carrier = item.get("carriers") or {}
            extra = item.get("extra_details") or {}
            if "public_link_" in (carrier.get("email") or ""):
                has_public_link = True
            has_submitted = item.get("price") is not None or extra.get("submitted") == True
            
            # İctimai (Public) əsas linki tapırıq
            is_public_base = "public_link" in carrier.get("email", "") and not has_submitted
            
            # ƏSAS HƏLL: Əgər bu əsas public linkdirsə, onu siyahıya ÜMUMİYYƏTLƏ ƏLAVƏ ETMƏ (Gizlət)
            if is_public_base:
                continue
            
            custom_name = extra.get("carrier_company")
            display_name = custom_name if custom_name else carrier.get("company_name", "Daşıyıcı")
            
            result_carriers.append({
                "quote_id": item.get("id"), "carrier_id": item.get("carrier_id"), 
                "company_name": display_name,
                "email": carrier.get("email", ""), 
                "mail_status": item.get("mail_status", "pending"), 
                "is_viewed": item.get("is_viewed", False),
                "has_submitted": has_submitted, "token": item.get("token"),
                "is_public": "public_link_" in (carrier.get("email") or "")
            })
        # Eyni daşıyıcı bir neçə təklif göndəribsə (alternativ təkliflər), siyahıda bir daşıyıcı kimi görünür:
        # əsas qeyd ilk göndəriş sətridir (xatırlatma/yenidən göndərmə ona aiddir). İctimai link təklifləri ayrı şirkətlərdir.
        merged, by_carrier = [], {}
        for entry in sorted(result_carriers, key=lambda e: e.get("quote_id") or 0):
            if entry.get("is_public"):
                merged.append(entry)
                continue
            key = entry.get("carrier_id")
            main = by_carrier.get(key)
            if main is None:
                entry["offers_count"] = 1 if entry["has_submitted"] else 0
                by_carrier[key] = entry
                merged.append(entry)
            else:
                main["has_submitted"] = main["has_submitted"] or entry["has_submitted"]
                main["is_viewed"] = main["is_viewed"] or entry["is_viewed"]
                if entry["has_submitted"]: main["offers_count"] = main.get("offers_count", 0) + 1
        for e in merged:
            e.setdefault("offers_count", 1 if e.get("has_submitted") else 0)
        return {"status": "success", "carriers": merged, "has_public_link": has_public_link}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/requests/details/{target_id}")
def get_request_details(target_id: str):
    quote_res = supabase.table("quotes").select("*, shipment_requests(*)").eq("token", target_id).execute()
    if quote_res.data:
        quote = quote_res.data[0]
        
        if not quote.get("is_viewed"):
            try:
                supabase.table("quotes").update({"is_viewed": True}).eq("id", quote["id"]).execute()
            except Exception:
                pass
        
        shipment = quote.get("shipment_requests") or {}
        if isinstance(shipment, dict):
            note_val = shipment.get("additional_notes") or shipment.get("note") or shipment.get("customer_note") or ""
            shipment["additional_notes"], shipment["note"] = note_val, note_val
            vol = shipment.get("volume_m3")
            if vol is None or vol == 0 or vol == 0.0 or str(vol).strip() in ["0", "0.0", ""]: shipment["volume_m3"] = "Qeyd edilməyib"
            deadline = shipment.get("deadline")
            if deadline and str(deadline) in note_val and ("loading" in note_val.lower() or "tarix" in note_val.lower()): shipment["deadline"] = None
        
        all_quotes_data = []
        req_id = quote.get("request_id")
        car_id = quote.get("carrier_id")
        
        carrier_email = ""
        if car_id:
            car_res = supabase.table("carriers").select("email").eq("id", car_id).execute()
            if car_res.data:
                carrier_email = car_res.data[0].get("email", "")
        
        is_public_link = "public_link_" in quote.get("token", "") or "public_link_" in carrier_email
        
        # -------------------------------------------------------------------------
        # ƏN VACİB HİSSƏ: Public Linkdirsə, bazada nə olur olsun hər şeyi sıfırlayırıq!
        # -------------------------------------------------------------------------
        if is_public_link:
            quote["price"] = None
            quote["transit_time_days"] = None
            quote["extra_details"] = {}
        
        # Digər təklifləri (Option tabs) yalnız ənənəvi linklərdə göstəririk
        if req_id and car_id and not is_public_link:
            all_q_res = supabase.table("quotes").select("*").eq("request_id", req_id).eq("carrier_id", car_id).order("id").execute()
            for q in (all_q_res.data or []):
                ex = q.get("extra_details") or {}
                cex = dict(ex)
                cex.pop("submitted", None)
                q["extra_details"] = cex
                all_quotes_data.append(q)

        extra = quote.get("extra_details") or {}
        is_already_submitted = (quote.get("price") is not None) or (extra.get("submitted") == True)
        cleaned_extra = dict(extra)
        cleaned_extra.pop("submitted", None)
        quote["extra_details"] = cleaned_extra
        
        return {
            "already_submitted": is_already_submitted, 
            "request": shipment, 
            "quote": quote,
            "all_quotes": all_quotes_data,
            "is_public": is_public_link  # Frontendə bunun public olduğunu açıq deyirik
        }
    
    if target_id.isdigit():
        req_res = supabase.table("shipment_requests").select("*").eq("id", int(target_id)).execute()
        if req_res.data:
            shipment = req_res.data[0]
            if isinstance(shipment, dict):
                note_val = shipment.get("additional_notes") or shipment.get("note") or shipment.get("customer_note") or ""
                shipment["additional_notes"], shipment["note"] = note_val, note_val
                vol = shipment.get("volume_m3")
                if vol is None or vol == 0 or vol == 0.0 or str(vol).strip() in ["0", "0.0", ""]: shipment["volume_m3"] = "Qeyd edilməyib"
                deadline = shipment.get("deadline")
                if deadline and str(deadline) in note_val and ("loading" in note_val.lower() or "tarix" in note_val.lower()): shipment["deadline"] = None
            return {"request": shipment, "already_submitted": False}
            
    raise HTTPException(status_code=404, detail="Sorğu tapılmadı.")

@app.get("/quotes/form/{token}")
def get_quote_form_details(token: str):
    res = supabase.table("quotes").select("*, shipment_requests(*)").eq("token", token).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Keçərsiz link!")
    quote = res.data[0]
    
    # --- YENİ EKLENEN KISIM: LİNK AÇILDIĞINDA BAXILDI (VIEWED) OLARAK İŞARETLE ---
    if not quote.get("is_viewed"):
        try:
            supabase.table("quotes").update({"is_viewed": True}).eq("token", token).execute()
        except Exception:
            pass
    # ----------------------------------------------------------------------------
    
    shipment = quote.get("shipment_requests")
    if isinstance(shipment, dict):
        note_val = shipment.get("additional_notes") or shipment.get("note") or ""
        vol = shipment.get("volume_m3")
        if vol is None or vol == 0 or vol == 0.0 or str(vol).strip() in ["0", "0.0", ""]: shipment["volume_m3"] = "Qeyd edilməyib"
        deadline = shipment.get("deadline")
        if deadline and str(deadline) in note_val and ("loading" in note_val.lower() or "tarix" in note_val.lower()): shipment["deadline"] = None
        
    return {"already_submitted": quote.get("price") is not None, "quote": quote}
    
@app.post("/quotes/check-bounces")
async def check_bounces_endpoint():
    if not ENABLE_BOUNCE_CHECK: return {"status": "disabled", "message": "Bounce yoxlaması hazırda deaktivdir."}
    try: return {"status": "success", **(await asyncio.to_thread(check_bounced_emails))}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quotes/track/{token}")
def track_email_view(token: str):
    try: supabase.table("quotes").update({"is_viewed": True}).eq("token", token).execute()
    except Exception: pass
    transparent_gif = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    return Response(content=transparent_gif, media_type="image/gif")

@app.post("/quotes/resend/{quote_id}")
async def resend_carrier_email(quote_id: int, background_tasks: BackgroundTasks, current_user: dict = Depends(verify_token)):
    _own_quote(quote_id, current_user)
    try:
        res = supabase.table("quotes").select("*, shipment_requests(*, customers(*)), carriers(*)").eq("id", quote_id).execute()
        if not res.data: raise HTTPException(status_code=404, detail="Təklif qeydi tapılmadı.")
        quote = res.data[0]
        sender_company, customer_email = get_sender_info_from_shipment(quote.get("shipment_requests"))
        supabase.table("quotes").update({"mail_status": "pending"}).eq("id", quote_id).execute()
        background_tasks.add_task(
            send_carrier_email_link, carrier_email=quote["carriers"]["email"], carrier_name=quote["carriers"].get("company_name", "Daşıyıcı"),
            origin=quote["shipment_requests"]["origin"], destination=quote["shipment_requests"]["destination"], token=quote["token"], sender_company=sender_company, reply_to_email=customer_email
        )
        return {"status": "success", "message": "Mail yenidən göndərilməyə başlandı!"}
    except HTTPException: raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quotes/reminder/{quote_id}")
async def send_single_reminder(quote_id: int, background_tasks: BackgroundTasks, current_user: dict = Depends(verify_token)):
    _own_quote(quote_id, current_user)
    try:
        res = supabase.table("quotes").select("*, shipment_requests(*, customers(*)), carriers(*)").eq("id", quote_id).execute()
        if not res.data: raise HTTPException(status_code=404, detail="Qeyd tapılmadı.")
        quote = res.data[0]
        sender_company, customer_email = get_sender_info_from_shipment(quote.get("shipment_requests"))
        if not quote["carriers"].get("email"): raise HTTPException(status_code=400, detail="Daşıyıcı email ünvanı yoxdur.")
        background_tasks.add_task(
            send_carrier_email_link, carrier_email=quote["carriers"]["email"], carrier_name=quote["carriers"].get("company_name", "Daşıyıcı"),
            origin=quote["shipment_requests"]["origin"], destination=quote["shipment_requests"]["destination"], token=quote["token"], sender_company=sender_company, is_reminder=True, reply_to_email=customer_email
        )
        return {"status": "success", "message": "Reminder göndərildi!"}
    except HTTPException: raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quotes/reminder-batch")
async def send_batch_reminders(payload: BatchReminderRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(verify_token)):
    try:
        if not payload.quote_ids: raise HTTPException(status_code=400, detail="Heç bir ID seçilməyib.")
        res = supabase.table("quotes").select("*, shipment_requests(*, customers(*)), carriers(*)").in_("id", payload.quote_ids).execute()
        count = 0
        for quote in (res.data or []):
            if str((quote.get("shipment_requests") or {}).get("customer_id")) != str(current_user.get("sub")): continue
            if quote.get("carriers", {}).get("email"):
                sender_company, customer_email = get_sender_info_from_shipment(quote.get("shipment_requests"))
                background_tasks.add_task(
                    send_carrier_email_link, carrier_email=quote["carriers"]["email"], carrier_name=quote["carriers"].get("company_name", "Daşıyıcı"),
                    origin=quote["shipment_requests"]["origin"], destination=quote["shipment_requests"]["destination"], token=quote["token"],
                    sender_company=sender_company, is_reminder=True, reply_to_email=customer_email
                )
                count += 1
        return {"status": "success", "message": f"Seçilmiş {count} daşıyıcıya toplu reminder göndərildi!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quotes/create")
def create_quote_direct(payload: DynamicQuoteSubmit):
    if not payload.request_id: raise HTTPException(status_code=400, detail="request_id daxil edilməlidir.")
    res = supabase.table("quotes").insert({"request_id": payload.request_id, "price": payload.price, "transit_time_days": payload.transit_time_days, "extra_details": payload.extra_details, "currency": payload.currency or "AZN"}).execute()
    return {"status": "success", "message": "Təklif qəbul edildi!", "data": res.data}

@app.post("/quotes/submit/{token}")
@limiter.limit("5/minute")
async def submit_quote(request: Request, token: str, price: Optional[str] = Form(None), currency: Optional[str] = Form("AZN"), transit_time_days: Optional[int] = Form(None), extra_details: Optional[str] = Form("{}"), carrier_file: Optional[UploadFile] = File(None), is_alternative: str = Form("false")):
    try:
        res = supabase.table("quotes").select("*").eq("token", token).execute()
        if not res.data: raise HTTPException(status_code=404, detail="Xətalı link!")
        quote = res.data[0]
        
        parsed_price = float(price) if price and str(price).strip() else None
        parsed_extra = json.loads(extra_details) if extra_details else {}
        parsed_extra["submitted"] = True
        parsed_extra["submitted_at"] = datetime.utcnow().isoformat()

        # Public link yoxlaması
        carrier_email = ""
        try:
            car_res = supabase.table("carriers").select("email").eq("id", quote.get("carrier_id")).execute()
            if car_res.data:
                carrier_email = car_res.data[0].get("email", "")
        except Exception:
            pass

        is_public_link = "public_link_" in quote.get("token", "") or "public_link_" in carrier_email
        
        form_carrier_name = request.query_params.get("carrier_company") or parsed_extra.get("carrier_company")
        if not form_carrier_name:
            form_data_dict = await request.form()
            form_carrier_name = form_data_dict.get("carrier_company")

        if is_public_link and not form_carrier_name:
            raise HTTPException(status_code=400, detail="Zəhmət olmasa daşıyıcı şirkət adını daxil edin.")

        if form_carrier_name:
            parsed_extra["carrier_company"] = form_carrier_name.strip()
            # DİQQƏT: Orjinal "İctimai Link" profilinin adını ARTIQ DƏYİŞMİRİK. 

        # Daşıyıcı özü "alternativ təklif" seçibsə (ictimai link olmayan halda), təklif belə işarələnir
        explicitly_alternative = (is_alternative or "").lower() == "true" and not is_public_link
        if explicitly_alternative:
            parsed_extra["is_alternative"] = True

        # --- ƏSAS HƏLL: Public Linkdirsə əsas linki boş saxlamaq üçün həmişə YENİ təklif yaradırıq ---
        if is_public_link:
            is_alternative = "true"
                    
        if carrier_file and carrier_file.filename:
            await validate_file(carrier_file)
            file_ext = os.path.splitext(carrier_file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            with open(os.path.join(UPLOAD_DIR, unique_filename), "wb") as buffer: buffer.write(await carrier_file.read())
            parsed_extra["carrier_attachment_url"] = f"/uploads/{unique_filename}"
            parsed_extra["carrier_attachment_name"] = carrier_file.filename

        parsed_currency = (currency or "AZN").strip().upper()
        if parsed_currency not in ("AZN", "USD", "EUR", "TRY", "RUB", "GBP"): parsed_currency = "AZN"

        if is_alternative.lower() == "true":
            new_token = str(uuid.uuid4())
            new_quote_data = {
                "request_id": quote["request_id"],
                "carrier_id": quote["carrier_id"],
                "token": new_token,
                "price": parsed_price,
                "currency": parsed_currency,
                "transit_time_days": transit_time_days,
                "extra_details": parsed_extra,
                "mail_status": "delivered",
                "is_viewed": True
            }
            insert_res = supabase.table("quotes").insert(new_quote_data).execute()
            return {"status": "success", "message": "Alternativ təklif qəbul edildi!", "data": insert_res.data}

        # Bura yalnız public OLMAYAN (xüsusi) linklər üçün işləyəcək
        history = quote.get("quote_history") or []
        existing_price = quote.get("price")
        existing_extra = quote.get("extra_details") or {}

        if existing_price is not None or existing_extra.get("submitted"):
            old_state = {
                "version": len(history) + 1,
                "price": existing_price,
                "currency": quote.get("currency"),
                "transit_time_days": quote.get("transit_time_days"),
                "extra_details": existing_extra,
                "date": datetime.utcnow().isoformat()
            }
            history.append(old_state)

        update_res = supabase.table("quotes").update({
            "price": parsed_price, 
            "transit_time_days": transit_time_days, 
            "extra_details": parsed_extra, 
            "currency": parsed_currency,
            "quote_history": history
        }).eq("token", token).execute()
        
        return {"status": "success", "message": "Təklif qəbul edildi!", "data": update_res.data}
    except HTTPException as he:
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Sistem xətası: {str(e)}")

@app.get("/quotes/request/{request_id}")
def get_request_quotes(request_id: int, current_user: dict = Depends(verify_token)):
    _own_request(request_id, current_user)
    try:
        quotes_res = supabase.table("quotes").select("*, carriers(*)").eq("request_id", request_id).execute()
        quotes_list = []
        for item in quotes_res.data or []:
            raw_extra = item.get("extra_details") or {}
            if item.get("price") is None and raw_extra.get("submitted") != True: continue
            filtered_extra = {k: v for k, v in raw_extra.items() if normalize_text(k) not in ['company', 'sirket', 'firma', 'email', 'mail', 'name', 'ad', 'dasiyici']}
            quotes_list.append({
                "id": item.get("id"), "request_id": item.get("request_id"), "carrier_id": item.get("carrier_id"),
                "carrier_company": (item.get("extra_details") or {}).get("carrier_company") or item.get("carriers", {}).get("company_name", f"Daşıyıcı #{item.get('carrier_id')}"), "carrier_email": item.get("carriers", {}).get("email", ""),
                "price": item.get("price"), "currency": item.get("currency", "AZN"), "transit_time_days": item.get("transit_time_days"),
                "is_winner": item.get("is_winner", False), "extra_details": filtered_extra, "extra_responses": filtered_extra,
                "quote_history": item.get("quote_history", [])
            })
        return {"status": "success", "quotes": quotes_list}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quotes/select-winner/{quote_id}")
def select_winner_path(quote_id: int, current_user: dict = Depends(verify_token)):
    quote_res = supabase.table("quotes").select("request_id").eq("id", quote_id).execute()
    if not quote_res.data: raise HTTPException(status_code=404, detail="Təklif tapılmadı.")
    _own_request(quote_res.data[0]["request_id"], current_user)
    request_id = quote_res.data[0]["request_id"]
    supabase.table("quotes").update({"is_winner": False}).eq("request_id", request_id).execute()
    supabase.table("quotes").update({"is_winner": True}).eq("id", quote_id).execute()
    supabase.table("shipment_requests").update({"status": "closed"}).eq("id", request_id).execute()
    return {"status": "success", "message": "Təklif qalib olaraq seçildi!"}

@app.post("/quotes/cancel-winner/{quote_id}")
def cancel_winner_path(quote_id: int, current_user: dict = Depends(verify_token)):
    quote_res = supabase.table("quotes").select("request_id").eq("id", quote_id).execute()
    if not quote_res.data: raise HTTPException(status_code=404, detail="Təklif tapılmadı.")
    _own_request(quote_res.data[0]["request_id"], current_user)
    
    request_id = quote_res.data[0]["request_id"]
    
    supabase.table("quotes").update({"is_winner": False}).eq("request_id", request_id).execute()
    supabase.table("shipment_requests").update({"status": "open"}).eq("id", request_id).execute()
    
    return {"status": "success", "message": "Qalib seçimi ləğv edildi. Başqa təklif seçə bilərsiniz!"}

@app.post("/quotes/select-winner")
async def select_winner_body(payload: SelectWinnerRequest, current_user: dict = Depends(verify_token)):
    _own_request(payload.request_id, current_user)
    q = supabase.table("quotes").select("request_id").eq("id", payload.quote_id).execute()
    if not q.data or q.data[0]["request_id"] != payload.request_id: raise HTTPException(status_code=404, detail="Bu sorğuda belə təklif yoxdur.")
    supabase.table("quotes").update({"is_winner": False}).eq("request_id", payload.request_id).execute()
    supabase.table("quotes").update({"is_winner": True}).eq("id", payload.quote_id).execute()
    supabase.table("shipment_requests").update({"status": "closed"}).eq("id", payload.request_id).execute()
    return {"status": "success", "message": "Qalib təklif uğurla təsdiqləndi!"}

INVITE_TYPES = {"importer": "İdxalçı / İxracçı", "forwarder": "Freight forwarder (müştəri paneli ilə)"}

@app.get("/admin/generate-invite")
def generate_invite_link(secret: str = None, type: str = None, plan: str = "basic"):
    """Qeydiyyat linki yaradır. type=importer: idxalçı/ixracçı hesabı; type=forwarder: forwarder + müştəri paneli.
    Hesab növü linkin özündə (bazada) saxlanılır, link sahibi onu dəyişə bilmir."""
    ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
    if not ADMIN_SECRET_KEY or secret != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Giriş qadağandır! Gizli şifrə səhvdir və ya təyin olunmayıb.")
    if type not in INVITE_TYPES:
        raise HTTPException(status_code=400, detail="Link növünü yazın: &type=importer (idxalçı/ixracçı) və ya &type=forwarder (forwarder + müştəri paneli).")

    if plan not in ("basic", "pro"):
        raise HTTPException(status_code=400, detail="Plan yalnız basic və ya pro ola bilər (&plan=pro).")

    new_token = str(uuid.uuid4())
    try:
        supabase.table("registration_tokens").insert({"token": new_token, "is_used": False, "account_type": type, "plan": plan}).execute()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Baza xətası! registration_tokens cədvəlində account_type və plan sütunları olmalıdır (alter table registration_tokens add column if not exists account_type text; alter table registration_tokens add column if not exists plan text;): {str(e)}")

    invite_link = f"{BASE_URL}/register?token={new_token}"
    return {
        "mesaj": f"{INVITE_TYPES[type]} üçün link yaradıldı! Bütün yazını kopyalayıb müştəriyə WhatsApp-da və ya E-poçtla göndərin:",
        "novu": type,
        "plan": plan,
        "musteri_linki": invite_link
    }

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request, token: str = None):
    try:
        # Link (token) olmadan da açılır: yalnız "Freight forwarder paneli" üçün açıq qeydiyyat mümkündür.
        safe_token = ""
        safe_invite_type = ""
        if token:
            res = supabase.table("registration_tokens").select("*").eq("token", token).execute()
            token_record = res.data[0] if res.data else None
            if not token_record:
                return HTMLResponse("<h1>Xəta: Bu link mövcud deyil və ya səhvdir.</h1>", status_code=404)
            if token_record.get('is_used'):
                return HTMLResponse("<h1>Xəta: Bu qeydiyyat linki artıq istifadə edilib! Hər link yalnız 1 dəfə keçərlidir.</h1>", status_code=403)
            safe_token = token
            if token_record.get("account_type") in INVITE_TYPES:
                safe_invite_type = token_record["account_type"]

        file_path = os.path.join("static", "register.html")
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        html_content = html_content.replace("{{ token }}", safe_token).replace("{{ invite_type }}", safe_invite_type)
        return HTMLResponse(content=html_content)
    except Exception as e:
        traceback.print_exc()
        return HTMLResponse("<h1>Xəta: register.html faylı tapılmadı! Zəhmət olmasa static/ qovluğunda yaradın.</h1>", status_code=404)

@app.post("/api/register")
@limiter.limit("3/minute")
def process_registration(request: Request, data: RegisterRequest):
    if len(data.password) < 8 or not re.search(r"[A-Z]", data.password) or not re.search(r"[a-z]", data.password) or not re.search(r"[0-9]", data.password):
        raise HTTPException(
            status_code=400, 
            detail="Təhlükəsizlik: Şifrə ən azı 8 simvol olmalı, həmçinin ən azı 1 böyük hərf, 1 kiçik hərf və 1 rəqəm ehtiva etməlidir!"
        )

    try:
        # Hesab növü və panel hüquqları
        account_type = (data.account_type or "importer_exporter").strip()
        panel_access = (data.panel_access or "customer").strip()
        # Linkin növü varsa, istifadəçinin seçdiyi deyil, linkdəki növ tətbiq olunur
        if data.token:
            inv = supabase.table("registration_tokens").select("*").eq("token", data.token).eq("is_used", False).execute()
            invite_kind = (inv.data[0].get("account_type") if inv.data else None)
            if invite_kind == "importer": account_type, panel_access = "importer_exporter", "customer"
            elif invite_kind == "forwarder": account_type, panel_access = "forwarder", "both"
        if account_type not in ("importer_exporter", "forwarder"):
            raise HTTPException(status_code=400, detail="Etibarsız hesab növü.")
        if account_type == "importer_exporter":
            customer_access, forwarder_access = True, False
        else:
            if panel_access == "both": customer_access, forwarder_access = True, True
            elif panel_access == "customer": customer_access, forwarder_access = True, False
            elif panel_access == "forwarder": customer_access, forwarder_access = False, True
            else: raise HTTPException(status_code=400, detail="Etibarsız panel seçimi.")

        company_name = (data.company_name or "").strip()
        if not company_name or len(company_name) > 150:
            raise HTTPException(status_code=400, detail="Şirkət adı boş ola bilməz (maks. 150 simvol).")

        # Müştəri paneli hüququ (idxalçı/ixracçı və ya forwarder-in müştəri paneli) yalnız admin linki ilə verilir.
        # Yalnız forwarder paneli üçün qeydiyyat linksizdir.
        needs_token = customer_access
        valid_token = None
        if needs_token:
            if not data.token:
                raise HTTPException(status_code=400, detail="Bu qeydiyyat növü üçün sizə göndərilmiş qeydiyyat linki lazımdır.")
            res = supabase.table("registration_tokens").select("*").eq("token", data.token).eq("is_used", False).execute()
            valid_token = res.data[0] if res.data else None
            if not valid_token:
                raise HTTPException(status_code=400, detail="Qeydiyyat linki etibarsızdır və ya artıq istifadə edilib.")

        existing = supabase.table("customers").select("id").eq("email", data.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Bu e-poçt ünvanı artıq mövcuddur.")

        hashed_password = pwd_context.hash(data.password)
        new_customer = {
            "email": data.email, "password": hashed_password, "name": company_name,
            "account_type": account_type, "customer_access": customer_access, "forwarder_access": forwarder_access
        }
        # Linkdə plan yazılıbsa (basic | pro), hesab həmin planla açılır; yazılmayıbsa bazanın standart planı qalır
        invite_plan = valid_token.get("plan") if valid_token else None
        if invite_plan in ("basic", "pro"):
            new_customer["plan"] = invite_plan
        ins = supabase.table("customers").insert(new_customer).execute()
        new_id = ins.data[0]["id"] if ins.data else None

        # Forwarder panelinə girişi olan hesab üçün boş profil yaradılır (şirkət adı ilə)
        if forwarder_access and new_id:
            try:
                supabase.table("forwarder_profiles").insert({"customer_id": new_id, "company_name": company_name}).execute()
            except Exception:
                traceback.print_exc()

        if needs_token and valid_token:
            supabase.table("registration_tokens").update({"is_used": True}).eq("token", data.token).execute()
        return {"message": "Qeydiyyat uğurla tamamlandı!"}
    except HTTPException as he: raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Baza xətası: {str(e)}")

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest):
    customer = supabase.table("customers").select("*").eq("email", data.email).execute()
    if customer.data:
        user = customer.data[0]
        if pwd_context.verify(data.password, user.get("password", "")):
            account_type = user.get("account_type") or "importer_exporter"
            customer_access = user.get("customer_access") is not False
            forwarder_access = user.get("forwarder_access") is True
            plan = user.get("plan") or "basic"
            token = create_access_token({
                "sub": str(user["id"]), "role": "customer", "email": user["email"],
                "account_type": account_type, "customer_access": customer_access, "forwarder_access": forwarder_access, "plan": plan
            })
            safe_user = {k: v for k, v in user.items() if k != "password"}   # parol heş-i brauzerə göndərilmir
            home = "/forwarder" if (forwarder_access and not customer_access) else "/customer"
            return {"status": "success", "role": "customer", "token": token, "user": safe_user, "home": home,
                    "account_type": account_type, "customer_access": customer_access, "forwarder_access": forwarder_access,
                    "plan": plan, "ai_enabled": bool(customer_access and plan == "pro")}
        else: raise HTTPException(status_code=400, detail="Yanlış e-poçt və ya parol.")

    carrier = supabase.table("carriers").select("*").eq("email", data.email).execute()
    if carrier.data:
        user = carrier.data[0]
        if pwd_context.verify(data.password, user.get("password", "")):
            token = create_access_token({"sub": str(user["id"]), "role": "carrier", "email": user["email"]})
            safe_user = {k: v for k, v in user.items() if k != "password"}
            return {"status": "success", "role": "carrier", "token": token, "user": safe_user}
        else: raise HTTPException(status_code=400, detail="Yanlış e-poçt və ya parol.")

    raise HTTPException(status_code=404, detail="Bu e-poçt ilə qeydiyyatlı hesab tapılmadı.")

@app.post("/api/change-password")
@limiter.limit("5/minute")
def change_password(request: Request, data: ChangePasswordRequest, current_user: dict = Depends(verify_any_token)):
    user_id = current_user.get("sub")
    role = current_user.get("role")
    
    if role != "customer":
        raise HTTPException(status_code=403, detail="Yalnız müştərilər şifrəsini dəyişə bilər.")
        
    user_res = supabase.table("customers").select("*").eq("id", user_id).execute()
    if not user_res.data:
        raise HTTPException(status_code=404, detail="İstifadəçi tapılmadı.")
    user = user_res.data[0]
    
    if not pwd_context.verify(data.current_password, user.get("password", "")):
        raise HTTPException(status_code=400, detail="Cari şifrə yanlışdır.")
        
    if len(data.new_password) < 8 or not re.search(r"[A-Z]", data.new_password) or not re.search(r"[a-z]", data.new_password) or not re.search(r"[0-9]", data.new_password):
        raise HTTPException(
            status_code=400, 
            detail="Təhlükəsizlik: Yeni şifrə ən azı 8 simvol olmalı, 1 böyük hərf, 1 kiçik hərf və 1 rəqəm ehtiva etməlidir!"
        )
        
    new_hashed_password = pwd_context.hash(data.new_password)
    supabase.table("customers").update({"password": new_hashed_password}).eq("id", user_id).execute()
    
    return {"status": "success", "message": "Şifrəniz uğurla dəyişdirildi!"}

class DeleteAccountRequest(BaseModel):
    password: str


def _delete_where(table: str, column: str, value):
    try:
        supabase.table(table).delete().eq(column, value).execute()
    except Exception:
        traceback.print_exc()
        raise


def _delete_in(table: str, column: str, values: list):
    for i in range(0, len(values), 100):
        chunk = values[i:i + 100]
        if chunk:
            supabase.table(table).delete().in_(column, chunk).execute()


@app.post("/api/delete-account")
@limiter.limit("3/minute")
def delete_account(request: Request, data: DeleteAccountRequest, current_user: dict = Depends(verify_any_token)):
    """Hesabı və ona aid bütün məlumatları (sorğular, təkliflər, daşıyıcı bazası, profil) birdəfəlik silir.
    Cari şifrə tələb olunur. Aİ sessiyası ilə silmək olmaz."""
    if current_user.get("role") != "customer":
        raise HTTPException(status_code=403, detail="Yalnız müştəri hesabı silinə bilər.")
    if current_user.get("via") == "ai":
        raise HTTPException(status_code=403, detail="Hesab yalnız arachi.co saytından, öz girişinizlə silinə bilər.")
    customer_id = int(current_user.get("sub"))
    res = supabase.table("customers").select("*").eq("id", customer_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Hesab tapılmadı.")
    user = res.data[0]
    if not pwd_context.verify(data.password or "", user.get("password", "")):
        raise HTTPException(status_code=400, detail="Şifrə yanlışdır.")

    try:
        rfq_ids = [r["id"] for r in (supabase.table("shipment_requests").select("id").eq("customer_id", customer_id).execute().data or [])]
        carrier_ids = [c["id"] for c in (supabase.table("carriers").select("id").eq("customer_id", customer_id).execute().data or [])]
        category_ids = [c["id"] for c in (supabase.table("carrier_categories").select("id").eq("customer_id", customer_id).execute().data or [])]
        profile = (supabase.table("forwarder_profiles").select("photo_url").eq("customer_id", customer_id).execute().data or [{}])[0]

        _delete_where("customer_quotes", "customer_id", customer_id)
        _delete_in("quotes", "request_id", rfq_ids)
        _delete_in("quotes", "carrier_id", carrier_ids)
        _delete_where("shipment_requests", "customer_id", customer_id)
        _delete_in("carrier_sub_categories", "category_id", category_ids)
        _delete_where("carriers", "customer_id", customer_id)
        _delete_where("carrier_categories", "customer_id", customer_id)
        _delete_where("forwarder_profiles", "customer_id", customer_id)
        _delete_where("ai_sso_jti", "customer_id", customer_id)
        supabase.table("customers").delete().eq("id", customer_id).execute()
        _delete_profile_photo_file(profile.get("photo_url"))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Hesabı silmək alınmadı, bəzi məlumatlar silinməmiş ola bilər: {e}. info@arachi.co ünvanına yazın.")
    return {"status": "success", "message": "Hesabınız və bütün məlumatlarınız silindi."}


@app.post("/api/change-email")
@limiter.limit("5/minute")
def change_email(request: Request, data: ChangeEmailRequest, current_user: dict = Depends(verify_any_token)):
    user_id = current_user.get("sub")
    role = current_user.get("role")
    
    if role != "customer":
        raise HTTPException(status_code=403, detail="Yalnız müştərilər e-poçtunu dəyişə bilər.")
        
    user_res = supabase.table("customers").select("*").eq("id", user_id).execute()
    if not user_res.data:
        raise HTTPException(status_code=404, detail="İstifadəçi tapılmadı.")
    user = user_res.data[0]
    
    if not pwd_context.verify(data.current_password, user.get("password", "")):
        raise HTTPException(status_code=400, detail="Cari şifrə yanlışdır.")
        
    existing_cust = supabase.table("customers").select("id").eq("email", data.new_email).execute()
    if existing_cust.data and str(existing_cust.data[0]["id"]) != str(user_id):
        raise HTTPException(status_code=400, detail="Bu e-poçt ünvanı artıq başqa müştəri hesabı tərəfindən istifadə olunur.")
        
    supabase.table("customers").update({"email": data.new_email}).eq("id", user_id).execute()
    
    return {"status": "success", "message": "E-poçtunuz uğurla dəyişdirildi!"}

# YENİ ƏLAVƏ: Təklifin Müştəriyə PDF Üçün Yadda Saxlanılması
class CustomerQuoteCreate(BaseModel):
    customer_id: int
    request_id: int
    quote_id: int
    base_price: float
    margin_type: str
    margin_value: float
    final_price: float
    currency: str
    valid_until: Optional[str] = None
    terms_conditions: Optional[str] = ""

@app.post("/customer-quotes/create")
def create_customer_quote(payload: CustomerQuoteCreate, current_user: dict = Depends(verify_token)):
    check_ownership(payload.customer_id, current_user)
    _own_request(payload.request_id, current_user)
    q = supabase.table("quotes").select("request_id").eq("id", payload.quote_id).execute()
    if not q.data or q.data[0]["request_id"] != payload.request_id:
        raise HTTPException(status_code=404, detail="Bu sorğuda belə təklif yoxdur.")
    try:
        res = supabase.table("customer_quotes").insert({
            "customer_id": payload.customer_id,
            "request_id": payload.request_id,
            "quote_id": payload.quote_id,
            "base_price": payload.base_price,
            "margin_type": payload.margin_type,
            "margin_value": payload.margin_value,
            "final_price": payload.final_price,
            "currency": payload.currency,
            "valid_until": payload.valid_until,
            "terms_conditions": payload.terms_conditions
        }).execute()
        return {"status": "success", "message": "Müştəri təklifi bazada yadda saxlanıldı və PDF yaradıldı!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
