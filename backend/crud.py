from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from models import Record, PlantRecord, Plant, User
from schemas import RecordCreate, RecordUpdate, PlantRecordCreate, PlantRecordUpdate
from typing import List, Optional
from datetime import date

# Record CRUD operations
def get_record(db: Session, record_id: int) -> Optional[Record]:
    return db.query(Record).filter(Record.id == record_id).first()

def get_record_by_date(db: Session, record_date: date) -> Optional[Record]:
    return db.query(Record).filter(Record.record_date == record_date).first()

def get_records(db: Session, skip: int = 0, limit: int = 100, plant_id: Optional[int] = None) -> List[Record]:
    query = db.query(Record).order_by(desc(Record.record_date))
    
    if plant_id:
        query = query.join(PlantRecord).filter(PlantRecord.plant_id == plant_id)
    
    return query.offset(skip).limit(limit).all()

def create_record(db: Session, record: RecordCreate) -> Record:
    # Check if record already exists for this date
    existing_record = get_record_by_date(db, record.record_date)
    if existing_record:
        raise ValueError(f"Record already exists for date {record.record_date}")
    
    # Create main record
    db_record = Record(
        record_date=record.record_date,
        weather=record.weather,
        temperature=record.temperature
    )
    db.add(db_record)
    db.flush()  # Get the ID
    
    # Create plant records
    for plant_record_data in record.plant_records:
        if plant_record_data.height is not None or plant_record_data.comment:
            db_plant_record = PlantRecord(
                record_id=db_record.id,
                plant_id=plant_record_data.plant_id,
                height=plant_record_data.height,
                comment=plant_record_data.comment,
                image_filename=plant_record_data.image_file
            )
            db.add(db_plant_record)
    
    db.commit()
    db.refresh(db_record)
    return db_record

def update_record(db: Session, record_id: int, record: RecordUpdate) -> Optional[Record]:
    db_record = get_record(db, record_id)
    if not db_record:
        return None
    
    # Update main record
    db_record.weather = record.weather
    db_record.temperature = record.temperature
    
    # Delete existing plant records
    db.query(PlantRecord).filter(PlantRecord.record_id == record_id).delete()
    
    # Create new plant records
    for plant_record_data in record.plant_records:
        if plant_record_data.height is not None or plant_record_data.comment:
            db_plant_record = PlantRecord(
                record_id=record_id,
                plant_id=plant_record_data.plant_id,
                height=plant_record_data.height,
                comment=plant_record_data.comment,
                image_filename=plant_record_data.image_file
            )
            db.add(db_plant_record)
    
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_record(db: Session, record_id: int) -> bool:
    db_record = get_record(db, record_id)
    if not db_record:
        return False
    
    db.delete(db_record)
    db.commit()
    return True

# Plant CRUD operations
def get_plants(db: Session, active_only: bool = True) -> List[Plant]:
    query = db.query(Plant).order_by(Plant.display_order)
    if active_only:
        query = query.filter(Plant.is_active == True)
    return query.all()

def get_plant(db: Session, plant_id: int) -> Optional[Plant]:
    return db.query(Plant).filter(Plant.id == plant_id).first()

# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()