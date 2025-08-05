from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime, timezone, timedelta

# JST時刻を取得する関数
def get_jst_now():
    """Get current time in JST"""
    utc_now = datetime.now(timezone.utc)
    jst = timezone(timedelta(hours=9))
    return utc_now.astimezone(jst)

class WeatherEnum(enum.Enum):
    sunny = "sunny"
    cloudy = "cloudy"
    rainy = "rainy"
    thunder = "thunder"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=get_jst_now)
    updated_at = Column(DateTime, default=get_jst_now, onupdate=get_jst_now)

class Plant(Base):
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_jst_now)
    updated_at = Column(DateTime, default=get_jst_now, onupdate=get_jst_now)
    
    # Relationship
    plant_records = relationship("PlantRecord", back_populates="plant")

class Record(Base):
    __tablename__ = "records"
    
    id = Column(Integer, primary_key=True, index=True)
    record_date = Column(Date, nullable=False, unique=True, index=True)
    weather = Column(Enum(WeatherEnum), nullable=False)
    temperature = Column(DECIMAL(4, 1), nullable=False)
    created_at = Column(DateTime, default=get_jst_now)
    updated_at = Column(DateTime, default=get_jst_now, onupdate=get_jst_now)
    
    # Relationship
    plant_records = relationship("PlantRecord", back_populates="record", cascade="all, delete-orphan")

class PlantRecord(Base):
    __tablename__ = "plant_records"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("records.id", ondelete="CASCADE"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False)
    height = Column(DECIMAL(5, 1))
    image_filename = Column(String(255))
    comment = Column(Text)
    created_at = Column(DateTime, default=get_jst_now)
    updated_at = Column(DateTime, default=get_jst_now, onupdate=get_jst_now)
    
    # Relationships
    record = relationship("Record", back_populates="plant_records")
    plant = relationship("Plant", back_populates="plant_records")
    
    # Composite index for performance
    __table_args__ = (
        {"mysql_engine": "InnoDB"},
    )