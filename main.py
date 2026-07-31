import os
import uuid
import traceback
import io
import json
import re
import pandas as pd
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from supabase import create_client, Client
from dotenv import load_dotenv
from passlib.context import CryptContext
from pathlib import Path

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BASE_DIR = Path(__file__).resolve().parent

# Mühit dəyişənlərini yükləyirik (.env faylından)
load_dotenv()

# ------------------------------------------------------------------
# KONFİQURASİYA VƏ BAZA
# ------------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL və ya SUPABASE_KEY təyin olunmayıb! Zəhmət olmasa .env faylını yoxlayın.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="LogiFast Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Qovluqların yaradılması
os.makedirs("static", exist_ok=True)
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Statik faylların və uploads qovluğunun montajı
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

conf = ConnectionConfig(
    MAIL_USERNAME="burzuyevrcb@gmail.com",
    MAIL_PASSWORD="yslb bddm cgyg scns",
    MAIL_FROM="burzuyevrcb@gmail.com",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True
)

fastmail = FastMail(conf)

# ------------------------------------------------------------------
# KÖMƏKÇİ FUNKSİYALAR
# ------------------------------------------------------------------
def normalize_text(text: Any) -> str:
    if not isinstance(text, str):
        text = str(text)
    text = text.strip().lower()
    replacements = {"ə": "e", "ç": "c", "ş": "s", "ı": "i", "ö": "o", "ü": "u", "ğ": "g"}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def process_dataframe_and_insert(df: pd.DataFrame, customer_id: int):
    if df.empty:
        raise HTTPException(status_code=400, detail="Məlumat tapılmadı və ya cədvəl boşdur.")

    normalized_columns = {col: normalize_text(col) for col in df.columns}

    email_keywords = ['email', 'e-mail', 'e-poct', 'epoct', 'e poct', 'poct', 'elaqe', 'contact', 'mail']
    email_col = next((orig for orig, norm in normalized_columns.items() if any(kw in norm for kw in email_keywords)), None)

    if not email_col:
        raise HTTPException(status_code=400, detail="Cədvəldə e-poçt sütunu tapılmadı.")

    company_keywords = ['company', 'sirket', 'firma', 'ad', 'name', 'carrier', 'dasiyici']
    comp_col = next((orig for orig, norm in normalized_columns.items() if any(kw in norm for kw in company_keywords)), None)

    existing_carriers = supabase.table("carriers").select("email").eq("customer_id", customer_id).execute()
    existing_emails = {item["email"].strip().lower() for item in existing_carriers.data if item.get("email")}

    carriers_to_insert = []
    seen_in_input = set()

    for _, row in df.iterrows():
        raw_email = str(row[email_col]).strip() if pd.notna(row[email_col]) else ""
        if raw_email and raw_email.lower() != 'nan' and '@' in raw_email and '.' in raw_email:
            clean_email = raw_email.lower()
            if clean_email in existing_emails or clean_email in seen_in_input:
                continue
            seen_in_input.add(clean_email)
            company = str(row[comp_col]).strip() if comp_col and pd.notna(row[comp_col]) else "Daşıyıcı"
            if company.lower() == 'nan' or not company:
                company = "Daşıyıcı"

            carriers_to_insert.append({
                "customer_id": customer_id,
                "company_name": company,
                "email": raw_email
            })

    if not carriers_to_insert:
        return {"status": "warning", "message": "Daxil edilən bütün e-poçtlar artıq bazada mövcuddur."}

    supabase.table("carriers").insert(carriers_to_insert).execute()
    return {"status": "success", "message": f"{len(carriers_to_insert)} yeni daşıyıcı uğurla əlavə edildi!"}

async def send_carrier_email_link(
    carrier_email: str, 
    carrier_name: str, 
    origin: str, 
    destination: str, 
    token: str, 
    custom_body: Optional[str] = None,
    sender_company: str = "LogiFast"
):
    quote_link = f"http://162.35.186.229:8000/carrier_quote/quote?token={token}"

    if not custom_body or not custom_body.strip():
        text_content = f"""Dear {carrier_name},

Please review the shipment details below and kindly complete the quotation form using the link provided.

Thank you.

Best regards,
{sender_company}"""
    else:
        text_content = custom_body
        text_content = text_content.replace("{{company_name}}", carrier_name)
        text_content = text_content.replace("{{sender_company}}", sender_company)
        text_content = text_content.replace("{{origin}}", origin)
        text_content = text_content.replace("{{destination}}", destination)

    formatted_text = text_content.replace("\n", "<br>")

    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; padding: 30px; border: 1px solid #e0e0e0;">
            <div style="font-size: 15px; color: #333333; line-height: 1.6; margin-bottom: 25px;">
                {formatted_text}
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #1a73e8; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Marşrut:</strong> {origin} ➔ {destination}</p>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{quote_link}" style="background-color: #1a73e8; color: white; padding: 12px 24px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block;">
                    👉 Təklifinizi Təqdim Edin
                </a>
            </div>
        </div>
    </div>
    """
    message = MessageSchema(
        subject=f"📦 Təklif Göndərin: {origin} - {destination}",
        recipients=[carrier_email],
        body=html_content,
        subtype=MessageType.html
    )
    try:
        await fastmail.send_message(message)
    except Exception:
        traceback.print_exc()

# ------------------------------------------------------------------
# PYDANTIC MODELLƏRİ
# ------------------------------------------------------------------
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
    carrier_ids: Optional[List[int]] = []
    
    attachment_url: Optional[str] = None
    additional_notes: Optional[str] = ""
    note: Optional[str] = ""
    email_template_type: Optional[str] = "standard"
    email_body: Optional[str] = None
    custom_email_body: Optional[str] = None

class DynamicQuoteSubmit(BaseModel):
    request_id: Optional[int] = None
    price: Optional[float] = None
    transit_time_days: Optional[int] = None
    extra_details: Optional[Dict[str, Any]] = {}

class SelectWinnerRequest(BaseModel):
    request_id: int
    quote_id: int

class DeleteCarrierRequest(BaseModel):
    customer_id: int
    carrier_id: int

class CarrierItem(BaseModel):
    name: str
    email: EmailStr

class CarrierBatchRequest(BaseModel):
    customer_id: int
    carriers: List[CarrierItem]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ------------------------------------------------------------------
# SƏHİFƏ MARŞRUTLARI (HTML PAGES)
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def get_home(): 
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
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

# ------------------------------------------------------------------
# API ENDPOINT-LƏRİ
# ------------------------------------------------------------------

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
            quotes_res = supabase.table("quotes").select("id").in_("request_id", req_ids).not_.is_("price", "null").execute()
            incoming_quotes_count = len(quotes_res.data or [])

        carriers_res = supabase.table("carriers").select("id").eq("customer_id", customer_id).execute()
        carriers_count = len(carriers_res.data or [])

        return {
            "status": "success",
            "active_rfqs": active_rfqs,
            "incoming_quotes": incoming_quotes_count,
            "completed_shipments": completed_shipments,
            "carriers_count": carriers_count
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/carriers/manual")
async def add_carriers_manual(payload: CarrierBatchRequest):
    try:
        carriers_to_insert = []
        for item in payload.carriers:
            carriers_to_insert.append({
                "customer_id": payload.customer_id,
                "company_name": item.name,
                "email": item.email
            })
        
        if carriers_to_insert:
            supabase.table("carriers").insert(carriers_to_insert).execute()
        
        return {"success": True, "message": f"{len(payload.carriers)} daşıyıcı uğurla əlavə edildi!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/carriers/upload-excel")
async def upload_carriers_excel(customer_id: int = Form(...), file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents)) if file.filename.lower().endswith('.csv') else pd.read_excel(io.BytesIO(contents))
        return process_dataframe_and_insert(df, customer_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fayl oxunarkən xəta: {str(e)}")

@app.post("/carriers/upload-text")
async def upload_carriers_text(customer_id: int = Form(...), raw_text: str = Form(...)):
    try:
        if not raw_text.strip(): raise HTTPException(status_code=400, detail="Mətn boşdur.")
        df = pd.read_csv(io.StringIO(raw_text), sep="\t")
        if len(df.columns) == 1: df = pd.read_csv(io.StringIO(raw_text), sep=",")
        return process_dataframe_and_insert(df, customer_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Xəta: {str(e)}")

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
        res = supabase.table("carriers").select("*").eq("customer_id", customer_id).execute()
        return res.data if res.data is not None else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/carriers/my-list/{customer_id}")
def get_customer_carriers_legacy(customer_id: int):
    res = supabase.table("carriers").select("*").eq("customer_id", customer_id).execute()
    return {"carriers": res.data}

@app.post("/requests/upload-attachment")
async def upload_request_attachment(file: UploadFile = File(...)):
    try:
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        contents = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
            
        return {
            "status": "success",
            "attachment_url": f"/uploads/{unique_filename}",
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fayl yüklənərkən xəta: {str(e)}")

@app.post("/requests/create")
async def create_shipment_request(
    payload: ShipmentRequestCreate,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        parsed_required = []
        for item in (payload.required_fields or []):
            if isinstance(item, dict):
                val_str = ", ".join([f"{k}: {v}" for k, v in item.items()])
                parsed_required.append(val_str)
            else:
                parsed_required.append(str(item))

        deadline_val = payload.deadline
        if deadline_val == "" or deadline_val is None:
            deadline_val = None

        stackable_val = payload.stackable
        if isinstance(stackable_val, str):
            if stackable_val.strip() == "" or stackable_val.lower() == "none":
                stackable_val = None
            else:
                stackable_val = stackable_val.lower() in ["true", "1", "yes", "on"]

        final_note = payload.additional_notes or payload.note or ""

        response = supabase.table("shipment_requests").insert({
            "customer_id": payload.customer_id,
            "origin": payload.origin,
            "destination": payload.destination,
            "cargo_type": payload.cargo_type,
            "weight_kg": payload.weight_kg,
            "volume_m3": payload.volume_m3,
            "deadline": deadline_val,
            "truck_type": payload.truck_type,
            "hs_code": payload.hs_code,
            "stackable": stackable_val,
            "shipment_type": payload.shipment_type,
            "required_fields": parsed_required,
            "attachment_url": payload.attachment_url,
            "additional_notes": final_note,
            "status": "open"
        }).execute()
        
        shipment_data = response.data[0]
        request_id = shipment_data["id"]

        cust_res = supabase.table("customers").select("*").eq("id", payload.customer_id).execute()
        sender_company = "LogiFast"
        if cust_res.data:
            c_data = cust_res.data[0]
            sender_company = c_data.get("company_name") or c_data.get("name") or "LogiFast"

        c_query = supabase.table("carriers").select("*").eq("customer_id", payload.customer_id).execute()
        all_customer_carriers = c_query.data or []

        if payload.send_to_all:
            target_carriers = all_customer_carriers
        else:
            selected_ids = set(payload.carrier_ids or [])
            target_carriers = [c for c in all_customer_carriers if c["id"] in selected_ids]

        active_custom_body = payload.custom_email_body or payload.email_body

        for carrier in target_carriers:
            unique_token = str(uuid.uuid4())
            supabase.table("quotes").insert({
                "request_id": request_id, 
                "carrier_id": carrier["id"], 
                "token": unique_token
            }).execute()
            
            carrier_name = carrier.get("company_name") or "Daşıyıcı"
            carrier_email = carrier.get("email")

            if carrier_email:
                background_tasks.add_task(
                    send_carrier_email_link,
                    carrier_email=carrier_email,
                    carrier_name=carrier_name,
                    origin=payload.origin,
                    destination=payload.destination,
                    token=unique_token,
                    custom_body=active_custom_body,
                    sender_company=sender_company
                )

        return {
            "status": "success", 
            "message": f"Sorğu #{request_id} yaradıldı. {len(target_carriers)} daşıyıcıya təklif linki göndərildi!", 
            "request_details": shipment_data
        }
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/requests/customer/{customer_id}")
def get_customer_requests(customer_id: int):
    res = supabase.table("shipment_requests").select("*, quotes(id, price)").eq("customer_id", customer_id).order("id", desc=True).execute()
    requests = res.data or []

    for req in requests:
        quotes_list = req.get("quotes") or []
        req["quotes_count"] = sum(1 for q in quotes_list if q.get("price") is not None)
        if "quotes" in req:
            del req["quotes"]

    return {"status": "success", "requests": requests}

@app.get("/requests/details/{target_id}")
def get_request_details(target_id: str):
    quote_res = supabase.table("quotes").select("*, shipment_requests(*)").eq("token", target_id).execute()
    if quote_res.data:
        quote = quote_res.data[0]
        shipment = quote.get("shipment_requests") or {}
        
        if isinstance(shipment, dict):
            note_val = shipment.get("additional_notes") or shipment.get("note") or shipment.get("customer_note") or ""
            shipment["additional_notes"] = note_val
            shipment["note"] = note_val

        return {
            "already_submitted": quote.get("price") is not None,
            "request": shipment,
            "quote": quote
        }
    
    if target_id.isdigit():
        req_res = supabase.table("shipment_requests").select("*").eq("id", int(target_id)).execute()
        if req_res.data:
            shipment = req_res.data[0]
            if isinstance(shipment, dict):
                note_val = shipment.get("additional_notes") or shipment.get("note") or shipment.get("customer_note") or ""
                shipment["additional_notes"] = note_val
                shipment["note"] = note_val
            return {"request": shipment, "already_submitted": False}

    raise HTTPException(status_code=404, detail="Sorğu və ya keçərli Token tapılmadı.")

@app.get("/quotes/form/{token}")
def get_quote_form_details(token: str):
    res = supabase.table("quotes").select("*, shipment_requests(*)").eq("token", token).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Keçərsiz link!")
    return {"already_submitted": res.data[0].get("price") is not None, "quote": res.data[0]}

@app.post("/quotes/create")
def create_quote_direct(payload: DynamicQuoteSubmit):
    if not payload.request_id:
        raise HTTPException(status_code=400, detail="request_id daxil edilməlidir.")
        
    res = supabase.table("quotes").insert({
        "request_id": payload.request_id,
        "price": payload.price,
        "transit_time_days": payload.transit_time_days,
        "extra_details": payload.extra_details,
        "currency": "AZN"
    }).execute()

    return {"status": "success", "message": "Təklif qəbul edildi!", "data": res.data}

@app.post("/quotes/submit/{token}")
async def submit_quote(
    token: str,
    price: Optional[float] = Form(None),
    transit_time_days: Optional[int] = Form(None),
    extra_details: Optional[str] = Form("{}"),
    carrier_file: Optional[UploadFile] = File(None)
):
    res = supabase.table("quotes").select("*").eq("token", token).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Xətalı link!")
    
    quote = res.data[0]
    if quote.get("price") is not None:
        raise HTTPException(status_code=400, detail="Artıq təklif göndərilib!")

    try:
        parsed_extra = json.loads(extra_details) if extra_details else {}
    except:
        parsed_extra = {}

    if carrier_file and carrier_file.filename:
        file_ext = os.path.splitext(carrier_file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await carrier_file.read())
            
        parsed_extra["carrier_attachment_url"] = f"/uploads/{unique_filename}"
        parsed_extra["carrier_attachment_name"] = carrier_file.filename

    update_res = supabase.table("quotes").update({
        "price": price,
        "transit_time_days": transit_time_days,
        "extra_details": parsed_extra,
        "currency": "AZN"
    }).eq("token", token).execute()

    return {"status": "success", "message": "Təklif qəbul edildi!", "data": update_res.data}

@app.get("/quotes/request/{request_id}")
def get_request_quotes(request_id: int):
    quotes_res = supabase.table("quotes").select("*, carriers(*)").eq("request_id", request_id).not_.is_("price", "null").execute()
    quotes_list = []
    for item in quotes_res.data or []:
        carrier_info = item.get("carriers") or {}
        
        raw_extra = item.get("extra_details") or {}
        filtered_extra = {
            k: v for k, v in raw_extra.items() 
            if normalize_text(k) not in ['company', 'sirket', 'firma', 'email', 'mail', 'name', 'ad', 'dasiyici']
        }
        
        quotes_list.append({
            "id": item.get("id"),
            "request_id": item.get("request_id"),
            "carrier_id": item.get("carrier_id"),
            "carrier_company": carrier_info.get("company_name", f"Daşıyıcı #{item.get('carrier_id')}"),
            "carrier_email": carrier_info.get("email", ""),
            "price": item.get("price"),
            "currency": item.get("currency", "AZN"),
            "transit_time_days": item.get("transit_time_days"),
            "is_winner": item.get("is_winner", False),
            "extra_details": filtered_extra,
            "extra_responses": filtered_extra
        })
    return {"status": "success", "quotes": quotes_list}

@app.post("/quotes/select-winner/{quote_id}")
def select_winner_path(quote_id: int):
    quote_res = supabase.table("quotes").select("request_id").eq("id", quote_id).execute()
    if not quote_res.data:
        raise HTTPException(status_code=404, detail="Təklif tapılmadı.")
    
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
        stored_password = user.get("password")
        
        if stored_password and pwd_context.verify(data.password, stored_password):
            return {"status": "success", "role": "customer", "user": user}
        else:
            raise HTTPException(status_code=400, detail="Yanlış e-poçt və ya parol.")
    
    carrier = supabase.table("carriers").select("*").eq("email", data.email).execute()
    if carrier.data:
        user = carrier.data[0]
        stored_password = user.get("password")
        
        if stored_password and pwd_context.verify(data.password, stored_password):
            return {"status": "success", "role": "carrier", "user": user}
        else:
            raise HTTPException(status_code=400, detail="Yanlış e-poçt və ya parol.")

    raise HTTPException(status_code=404, detail="Bu e-poçt ilə qeydiyyatlı hesab tapılmadı.")
