from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Yeni sorğu yaradılarkən tələb olunan məlumatlar
class ShipmentRequestCreate(BaseModel):
    customer_id: int
    origin: str
    destination: str
    weight_kg: float
    volume_m3: float
    deadline: datetime

# Daşıyıcının qiymət daxil edərkən göndərəcəyi məlumatlar
class QuoteSubmit(BaseModel):
    token: str
    price: float
    transit_time_days: int