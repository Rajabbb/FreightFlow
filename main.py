import os
import uuid
import traceback
import io
import json
import re
import asyncio
import imaplib
import email as email_lib
from datetime import datetime
from email.header import decode_header
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel, EmailStr
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from supabase import create_client, Client
from dotenv import load_dotenv
from passlib.context import CryptContext
from pathlib import Path

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BASE_DIR = Path(__file__).resolve().parent

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "https://arachi.co")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL və ya SUPABASE_KEY təyin olunmayıb! Zəhmət olmasa .env faylını yoxlayın.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = FastAPI(title="Arachi Backend API")

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
        print("[bounce-check] Deaktivdir (ENABLE_BOUNCE_CHECK=false). Amazon SES + SNS ilə əvəz olunana qədər söndürülüb.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def filter_and_insert_carriers(customer_id: int, raw_carriers: List[Dict[str, Any]]) -> Dict[str, Any]:
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

    if duplicate_emails:
        unique_dups = ", ".join(list(set(duplicate_emails)))
        raise HTTPException(status_code=400, detail=f"Bu e-poçt ünvanı artıq bazada və ya siyahıda mövcuddur: {unique_dups}")
    if not carriers_to_insert:
        raise HTTPException(status_code=400, detail="Daxil edilən e-poçt ünvanı etibarsızdır və ya artıq mövcuddur.")
    supabase.table("carriers").insert(carriers_to_insert).execute()
    return {"status": "success", "message": f"{len(carriers_to_insert)} yeni daşıyıcı uğurla əlavə edildi!"}

def process_dataframe_and_insert(df: pd.DataFrame, customer_id: int):
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
    return filter_and_insert_carriers(customer_id, raw_list)

async def send_carrier_email_link(carrier_email: str, carrier_name: str, origin: str, destination: str, token: str, custom_body: Optional[str] = None, sender_company: str = "Arachi", is_reminder: bool = False, reply_to_email: Optional[str] = None):
    quote_link = f"{BASE_URL}/carrier_quote/quote?token={token}"
    tracking_pixel_url = f"{BASE_URL}/quotes/track/{token}"
    if is_reminder:
        text_content = f"""Dear {carrier_name},\n\nThis is a gentle reminder regarding the shipment request from {origin} to {destination}. Please kindly submit your quotation using the link below if you haven't already.\n\nThank you.\n\nBest regards,\n{sender_company}"""
        subject_prefix = "⏰ Reminder: Submit a Proposal"
    elif not custom_body or not custom_body.strip():
        text_content = f"""Dear {carrier_name},\n\nPlease review the shipment details below and kindly complete the quotation form using the link provided.\n\nThank you.\n\nBest regards,\n{sender_company}"""
        subject_prefix = "📦 Submit a Proposal"
    else:
        text_content = custom_body.replace("{{company_name}}", carrier_name).replace("{{sender_company}}", sender_company).replace("{{origin}}", origin).replace("{{destination}}", destination)
        subject_prefix = "📦 Submit a Proposal"

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
    message_kwargs = dict(subject=f"{subject_prefix}: {origin} - {destination}", recipients=[carrier_email], body=html_content, subtype=MessageType.html, from_name=(sender_company or "Arachi").strip() or "Arachi")
    if reply_to_email: message_kwargs["reply_to"] = [reply_to_email]
    message = MessageSchema(**message_kwargs)
    try:
        await fastmail.send_message(message)
        supabase.table("quotes").update({"mail_status": "delivered"}).eq("token", token).execute()
    except Exception:
        traceback.print_exc()
        supabase.table("quotes").update({"mail_status": "failed"}).eq("token", token).execute()

# --- PYDANTIC MODELLƏRİ ---
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
    carrier_ids: Optional[List[int]] = []
    category_ids: Optional[List[int]] = []
    
    attachment_url: Optional[str] = None
    additional_notes: Optional[str] = ""
    note: Optional[str] = ""
    email_template_type: Optional[str] = "standard"
    email_body: Optional[str] = None
    custom_email_body: Optional[str] = None

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

class CarrierSetCategory(BaseModel):
    customer_id: int
    carrier_id: int
    category_id: Optional[int] = None

class CarrierBulkSetCategory(BaseModel):
    customer_id: int
    carrier_ids: List[int]
    category_id: Optional[int] = None

class RegisterRequest(BaseModel):
    token: str
    email: EmailStr
    password: str
    company_name: str

# --- ROUTELAR (API və Səhifələr) ---

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

@app.get("/carrier_quote/quote")
def get_carrier_quote_page(token: str):
    file_path = BASE_DIR / "static" / "carrier_quote.html"
    return FileResponse(file_path)

# --- INVITE & REGISTRATION LİNK MƏNTİQİ ---

@app.get("/admin/generate-invite")
def generate_invite_link(secret: str = None):
    # DİQQƏT: Bu gizli parolu kimsə bilməsə link yarada bilməz
    ADMIN_SECRET_KEY = "arachi_super_gizli_recebvusal2026" 
    
    if secret != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Giriş qadağandır! Gizli şifrə səhvdir.")
        
    # Təxmin edilməsi qeyri-mümkün olan unikal token (kod)
    new_token = str(uuid.uuid4())
    
    try:
        supabase.table("registration_tokens").insert({"token": new_token, "is_used": False}).execute()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Baza xətası! registration_tokens cədvəlinin olduğuna əmin olun: {str(e)}")
        
    invite_link = f"{BASE_URL}/register?token={new_token}"
    return {
        "mesaj": "Link yaradıldı! Bütün yazını kopyalayıb müştəriyə WhatsApp-da və ya E-poçtla göndərin:", 
        "musteri_linki": invite_link
    }

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request, token: str = None):
    if not token:
        return HTMLResponse("<h1>Xəta: Token tapılmadı. Zəhmət olmasa etibarlı linkdən istifadə edin.</h1>", status_code=400)
        
    try:
        res = supabase.table("registration_tokens").select("*").eq("token", token).execute()
        token_record = res.data[0] if res.data else None
        
        if not token_record:
            return HTMLResponse("<h1>Xəta: Bu link mövcud deyil və ya səhvdir.</h1>", status_code=404)
            
        if token_record.get('is_used'):
            return HTMLResponse("<h1>Xəta: Bu qeydiyyat linki artıq istifadə edilib! Hər link yalnız 1 dəfə keçərlidir.</h1>", status_code=403)
            
        # register.html faylını oxuyur və içindəki {{ token }} sözünü əsl tokenlə əvəzləyib müştəriyə göstərir
        file_path = os.path.join("static", "register.html")
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        html_content = html_content.replace("{{ token }}", token)
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        traceback.print_exc()
        return HTMLResponse("<h1>Xəta: register.html faylı tapılmadı! Zəhmət olmasa static/ qovluğunda yaradın.</h1>", status_code=404)

@app.post("/api/register")
def process_registration(data: RegisterRequest):
    try:
        # Tokeni yenidən yoxla
        res = supabase.table("registration_tokens").select("*").eq("token", data.token).eq("is_used", False).execute()
        valid_token = res.data[0] if res.data else None
        
        if not valid_token:
            raise HTTPException(status_code=400, detail="Qeydiyyat linki etibarsızdır və ya artıq istifadə edilib.")
            
        # Emailin artıq olub-olmadığını yoxla
        existing = supabase.table("customers").select("id").eq("email", data.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Bu e-poçt ünvanı artıq mövcuddur.")
        
        # Mövcud Passlib (bcrypt) ilə parolu gizlət
        hashed_password = pwd_context.hash(data.password)
        
        # Yeni müştərini cədvələ əlavə et
        insert_res = supabase.table("customers").insert({
            "email": data.email,
            "password": hashed_password,
            "company_name": data.company_name
        }).execute()
        
        new_user_id = insert_res.data[0]['id']
        
        # Və ən əsası tokeni "istifadə edildi" kimi qeyd et
        supabase.table("registration_tokens").update({"is_used": True}).eq("token", data.token).execute()
        
        return {"message": "Qeydiyyat uğurla tamamlandı!", "user_id": new_user_id}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Sistem xətası baş verdi.")

# --- ƏSAS TƏTBİQ ROUTELARI ---

@app.get("/categories/customer/{customer_id}")
def get_customer_categories(customer_id: int):
    try:
        res = supabase.table("carrier_categories").select("*").eq("customer_id", customer_id).order("id", desc=False).execute()
        return {"status": "success", "categories": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/categories/create")
def create_category(payload: CategoryCreate):
    try:
        res = supabase.table("carrier_categories").insert({"customer_id": payload.customer_id, "name": payload.name}).execute()
        return {"status": "success", "category": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/categories/delete")
def delete_category(payload: CategoryDelete):
    try:
        supabase.table("carrier_categories").delete().eq("id", payload.category_id).eq("customer_id", payload.customer_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/carriers/set-category")
def set_carrier_category(payload: CarrierSetCategory):
    try:
        val = payload.category_id if payload.category_id and payload.category_id > 0 else None
        supabase.table("carriers").update({"category_id": val}).eq("id", payload.carrier_id).eq("customer_id", payload.customer_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/carriers/bulk-set-category")
def bulk_set_carrier_category(payload: CarrierBulkSetCategory):
    try:
        val = payload.category_id if payload.category_id and payload.category_id > 0 else None
        if not payload.carrier_ids:
            return {"status": "success"}
        supabase.table("carriers").update({"category_id": val}).in_("id", payload.carrier_ids).eq("customer_id", payload.customer_id).execute()
        return {"status": "success"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customer/stats/{customer_id}")
def get_customer_stats(customer_id: int):
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
        carriers_res = supabase.table("carriers").select("id").eq("customer_id", customer_id).execute()
        return {"status": "success", "active_rfqs": active_rfqs, "incoming_quotes": incoming_quotes_count, "completed_shipments": completed_shipments, "carriers_count": len(carriers_res.data or [])}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/carriers/manual")
async def add_carriers_manual(request: Request):
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
        customer_id = int(customer_id)
        carriers = body.get("carriers")
        if not carriers:
            email = body.get("email")
            name = body.get("name") or body.get("company_name") or "Daşıyıcı"
            carriers = [{"name": name, "email": email}] if email else []

        return filter_and_insert_carriers(customer_id, carriers)
    except HTTPException as he: raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/carriers/upload-excel")
async def upload_carriers_excel(request: Request):
    try:
        form = await request.form()
        customer_id = form.get("customer_id") or request.query_params.get("customer_id")
        file = form.get("file")
        if not customer_id or not file: raise HTTPException(status_code=400, detail="customer_id və ya fayl əskikdir.")
        customer_id = int(customer_id)
        contents = await file.read()
        filename = getattr(file, "filename", "file.xlsx")
        df = pd.read_csv(io.BytesIO(contents)) if filename.lower().endswith('.csv') else pd.read_excel(io.BytesIO(contents))
        return process_dataframe_and_insert(df, customer_id)
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(status_code=400, detail=f"Fayl oxunarkən xəta: {str(e)}")

@app.post("/carriers/upload-text")
async def upload_carriers_text(request: Request):
    try:
        body = {}
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type: body = await request.json()
        else: body = dict(await request.form())
        
        customer_id = body.get("customer_id") or request.query_params.get("customer_id")
        raw_text = body.get("raw_text") or body.get("text") or request.query_params.get("raw_text") or request.query_params.get("text") or ""

        if not customer_id or not str(raw_text).strip(): raise HTTPException(status_code=400, detail="customer_id və raw_text tələb olunur.")
        customer_id = int(customer_id)

        lines = raw_text.strip().split("\n")
        raw_list = []
        for line in lines:
            line = line.strip()
            if not line: continue
            parts = [p.strip() for p in re.split(r'[\t,;|]', line) if p.strip()]
            email = None
            name = "Daşıyıcı"
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
                return process_dataframe_and_insert(df, customer_id)
            except Exception: raise HTTPException(status_code=400, detail="Məlumat formatı düzgün deyil. E-poçt tapılmadı.")
        return filter_and_insert_carriers(customer_id, raw_list)
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(status_code=400, detail=f"Xəta: {str(e)}")

@app.post("/carriers/delete")
def delete_customer_carrier(payload: DeleteCarrierRequest):
    try:
        supabase.table("carriers").delete().eq("id", payload.carrier_id).eq("customer_id", payload.customer_id).execute()
        return {"status": "success", "message": "Daşıyıcı bazadan uğurla silindi!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/carriers/customer/{customer_id}")
def get_customer_carriers(customer_id: int):
    try:
        res = supabase.table("carriers").select("*").eq("customer_id", customer_id).range(0, 9999).execute()
        return res.data if res.data is not None else []
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/requests/upload-attachment")
async def upload_request_attachment(file: UploadFile = File(...)):
    try:
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as buffer: buffer.write(await file.read())
        return {"status": "success", "attachment_url": f"/uploads/{unique_filename}", "filename": file.filename}
    except Exception as e: raise HTTPException(status_code=500, detail=f"Fayl yüklənərkən xəta: {str(e)}")

@app.post("/requests/create")
async def create_shipment_request(payload: ShipmentRequestCreate, background_tasks: BackgroundTasks = BackgroundTasks()):
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
        if send_opt == "category":
            cat_ids = set(payload.category_ids or [])
            target_carriers = [c for c in all_carriers if c.get("category_id") in cat_ids]
        elif send_opt == "selected" or not payload.send_to_all:
            selected_ids = set(payload.carrier_ids or [])
            target_carriers = [c for c in all_carriers if c.get("id") in selected_ids]
        else:
            target_carriers = all_carriers

        if not target_carriers:
            raise HTTPException(status_code=400, detail="Seçilmiş kriteriyalara uyğun daşıyıcı tapılmadı.")

        active_custom_body = payload.custom_email_body or payload.email_body

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
                    custom_body=active_custom_body, sender_company=sender_company, reply_to_email=customer_email
                )

        return {"status": "success", "message": f"Sorğu #{request_id} yaradıldı. {len(target_carriers)} daşıyıcıya təklif linki göndərildi!", "request_details": shipment_data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/requests/customer/{customer_id}")
def get_customer_requests(customer_id: int):
    res = supabase.table("shipment_requests").select("*, quotes(id, price, extra_details, quote_history)").eq("customer_id", customer_id).order("id", desc=True).execute()
    requests = res.data or []
    for req in requests:
        valid_quotes = [q for q in (req.get("quotes") or []) if q.get("price") is not None or (q.get("extra_details") and q.get("extra_details").get("submitted") == True)]
        req["quotes_count"] = len(valid_quotes)
        if "quotes" in req: del req["quotes"]
    return {"status": "success", "requests": requests}

@app.get("/requests/carriers-status/{request_id}")
def get_request_carriers_status(request_id: int):
    try:
        quotes_res = supabase.table("quotes").select("*, carriers(*)").eq("request_id", request_id).execute()
        result_carriers = []
        for item in (quotes_res.data or []):
            carrier = item.get("carriers") or {}
            extra = item.get("extra_details") or {}
            has_submitted = item.get("price") is not None or extra.get("submitted") == True
            result_carriers.append({
                "quote_id": item.get("id"), "carrier_id": item.get("carrier_id"), "company_name": carrier.get("company_name", "Daşıyıcı"),
                "email": carrier.get("email", ""), "mail_status": item.get("mail_status", "pending"), "is_viewed": item.get("is_viewed", False),
                "has_submitted": has_submitted, "token": item.get("token")
            })
        return {"status": "success", "carriers": result_carriers}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/requests/details/{target_id}")
def get_request_details(target_id: str):
    quote_res = supabase.table("quotes").select("*, shipment_requests(*)").eq("token", target_id).execute()
    if quote_res.data:
        quote = quote_res.data[0]
        shipment = quote.get("shipment_requests") or {}
        if isinstance(shipment, dict):
            note_val = shipment.get("additional_notes") or shipment.get("note") or shipment.get("customer_note") or ""
            shipment["additional_notes"], shipment["note"] = note_val, note_val
            vol = shipment.get("volume_m3")
            if vol is None or vol == 0 or vol == 0.0 or str(vol).strip() in ["0", "0.0", ""]: shipment["volume_m3"] = "Qeyd edilməyib"
            deadline = shipment.get("deadline")
            if deadline and str(deadline) in note_val and ("loading" in note_val.lower() or "tarix" in note_val.lower()): shipment["deadline"] = None
        extra = quote.get("extra_details") or {}
        is_already_submitted = (quote.get("price") is not None) or (extra.get("submitted") == True)
        cleaned_extra = dict(extra)
        cleaned_extra.pop("submitted", None)
        quote["extra_details"] = cleaned_extra
        
        return {"already_submitted": is_already_submitted, "request": shipment, "quote": quote}
    
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
    raise HTTPException(status_code=404, detail="Sorğu və ya keçərli Token tapılmadı.")

@app.get("/quotes/form/{token}")
def get_quote_form_details(token: str):
    res = supabase.table("quotes").select("*, shipment_requests(*)").eq("token", token).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Keçərsiz link!")
    quote = res.data[0]
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
async def resend_carrier_email(quote_id: int, background_tasks: BackgroundTasks):
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
async def send_single_reminder(quote_id: int, background_tasks: BackgroundTasks):
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
async def send_batch_reminders(payload: BatchReminderRequest, background_tasks: BackgroundTasks):
    try:
        if not payload.quote_ids: raise HTTPException(status_code=400, detail="Heç bir ID seçilməyib.")
        res = supabase.table("quotes").select("*, shipment_requests(*, customers(*)), carriers(*)").in_("id", payload.quote_ids).execute()
        count = 0
        for quote in (res.data or []):
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
async def submit_quote(token: str, price: Optional[str] = Form(None), currency: Optional[str] = Form("AZN"), transit_time_days: Optional[int] = Form(None), extra_details: Optional[str] = Form("{}"), carrier_file: Optional[UploadFile] = File(None)):
    res = supabase.table("quotes").select("*").eq("token", token).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Xətalı link!")
    quote = res.data[0]
    
    parsed_price = float(price) if price and str(price).strip() else None
    parsed_extra = json.loads(extra_details) if extra_details else {}
    parsed_extra["submitted"] = True

    if carrier_file and carrier_file.filename:
        file_ext = os.path.splitext(carrier_file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        with open(os.path.join(UPLOAD_DIR, unique_filename), "wb") as buffer: buffer.write(await carrier_file.read())
        parsed_extra["carrier_attachment_url"] = f"/uploads/{unique_filename}"
        parsed_extra["carrier_attachment_name"] = carrier_file.filename

    parsed_currency = (currency or "AZN").strip().upper()
    if parsed_currency not in ("AZN", "USD", "EUR", "TRY", "RUB", "GBP"): parsed_currency = "AZN"

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

@app.get("/quotes/request/{request_id}")
def get_request_quotes(request_id: int):
    try:
        quotes_res = supabase.table("quotes").select("*, carriers(*)").eq("request_id", request_id).execute()
        quotes_list = []
        for item in quotes_res.data or []:
            raw_extra = item.get("extra_details") or {}
            if item.get("price") is None and raw_extra.get("submitted") != True: continue
            filtered_extra = {k: v for k, v in raw_extra.items() if normalize_text(k) not in ['company', 'sirket', 'firma', 'email', 'mail', 'name', 'ad', 'dasiyici']}
            quotes_list.append({
                "id": item.get("id"), "request_id": item.get("request_id"), "carrier_id": item.get("carrier_id"),
                "carrier_company": item.get("carriers", {}).get("company_name", f"Daşıyıcı #{item.get('carrier_id')}"), "carrier_email": item.get("carriers", {}).get("email", ""),
                "price": item.get("price"), "currency": item.get("currency", "AZN"), "transit_time_days": item.get("transit_time_days"),
                "is_winner": item.get("is_winner", False), "extra_details": filtered_extra, "extra_responses": filtered_extra,
                "quote_history": item.get("quote_history", [])
            })
        return {"status": "success", "quotes": quotes_list}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quotes/select-winner/{quote_id}")
def select_winner_path(quote_id: int):
    quote_res = supabase.table("quotes").select("request_id").eq("id", quote_id).execute()
    if not quote_res.data: raise HTTPException(status_code=404, detail="Təklif tapılmadı.")
    request_id = quote_res.data[0]["request_id"]
    supabase.table("quotes").update({"is_winner": False}).eq("request_id", request_id).execute()
    supabase.table("quotes").update({"is_winner": True}).eq("id", quote_id).execute()
    supabase.table("shipment_requests").update({"status": "closed"}).eq("id", request_id).execute()
    return {"status": "success", "message": "Təklif qalib olaraq seçildi!"}

@app.post("/quotes/select-winner")
async def select_winner_body(payload: SelectWinnerRequest):
    supabase.table("quotes").update({"is_winner": False}).eq("request_id", payload.request_id).execute()
    supabase.table("quotes").update({"is_winner": True}).eq("id", payload.quote_id).execute()
    supabase.table("shipment_requests").update({"status": "closed"}).eq("id", payload.request_id).execute()
    return {"status": "success", "message": "Qalib təklif uğurla təsdiqləndi!"}

@app.post("/auth/login")
async def login(data: LoginRequest):
    customer = supabase.table("customers").select("*").eq("email", data.email).execute()
    if customer.data:
        user = customer.data[0]
        if pwd_context.verify(data.password, user.get("password", "")):
            return {"status": "success", "role": "customer", "user": user}
        else: raise HTTPException(status_code=400, detail="Yanlış e-poçt və ya parol.")
    
    carrier = supabase.table("carriers").select("*").eq("email", data.email).execute()
    if carrier.data:
        user = carrier.data[0]
        if pwd_context.verify(data.password, user.get("password", "")):
            return {"status": "success", "role": "carrier", "user": user}
        else: raise HTTPException(status_code=400, detail="Yanlış e-poçt və ya parol.")

    raise HTTPException(status_code=404, detail="Bu e-poçt ilə qeydiyyatlı hesab tapılmadı.")
