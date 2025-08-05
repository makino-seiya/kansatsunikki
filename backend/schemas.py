from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class WeatherEnum(str, Enum):
    sunny = "sunny"
    cloudy = "cloudy"
    rainy = "rainy"
    thunder = "thunder"

# Plant schemas
class PlantBase(BaseModel):
    name: str
    display_order: int = 0
    is_active: bool = True

class PlantCreate(PlantBase):
    pass

class PlantUpdate(PlantBase):
    pass

class Plant(PlantBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Plant Record schemas
class PlantRecordBase(BaseModel):
    plant_id: int
    height: Optional[Decimal] = None
    comment: Optional[str] = None

class PlantRecordCreate(PlantRecordBase):
    image_file: Optional[str] = None  # Will be handled separately

class PlantRecordUpdate(PlantRecordBase):
    image_file: Optional[str] = None

class PlantRecord(PlantRecordBase):
    id: int
    record_id: int
    image_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    plant: Plant
    
    class Config:
        from_attributes = True

# Record schemas
class RecordBase(BaseModel):
    record_date: date
    weather: WeatherEnum
    temperature: Decimal

class RecordCreate(RecordBase):
    plant_records: List[PlantRecordCreate] = []

class RecordUpdate(RecordBase):
    plant_records: List[PlantRecordUpdate] = []

class Record(RecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    plant_records: List[PlantRecord] = []
    
    class Config:
        from_attributes = True

# Response schemas
class RecordResponse(BaseModel):
    id: int
    record_date: date
    weather: WeatherEnum
    temperature: Decimal
    created_at: datetime
    updated_at: datetime
    plant_records: List[PlantRecord] = []
    
    class Config:
        from_attributes = True

class RecordListResponse(BaseModel):
    records: List[RecordResponse]
    total: int
    page: int
    per_page: int

# User schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None