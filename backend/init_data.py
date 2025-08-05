from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Plant
from passlib.context import CryptContext
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully")

def init_plants(db: Session):
    """Initialize default plants"""
    plants_data = [
        {"name": "向日葵（ひまわり）", "display_order": 1},
        {"name": "秋桜（コスモス）", "display_order": 2},
        {"name": "朝顔（あさがお）", "display_order": 3},
    ]
    
    for plant_data in plants_data:
        existing_plant = db.query(Plant).filter(Plant.name == plant_data["name"]).first()
        if not existing_plant:
            plant = Plant(**plant_data)
            db.add(plant)
            logger.info(f"Added plant: {plant_data['name']}")
    
    db.commit()

def init_admin_user(db: Session):
    """Initialize admin user"""
    admin_username = "admin"
    admin_password = "admin123"
    
    existing_user = db.query(User).filter(User.username == admin_username).first()
    if not existing_user:
        hashed_password = pwd_context.hash(admin_password)
        admin_user = User(
            username=admin_username,
            password_hash=hashed_password
        )
        db.add(admin_user)
        db.commit()
        logger.info(f"Admin user created: {admin_username}")
    else:
        logger.info("Admin user already exists")

def main():
    """Main initialization function"""
    logger.info("Starting database initialization...")
    
    # Create tables
    create_tables()
    
    # Initialize data
    db = SessionLocal()
    try:
        init_plants(db)
        init_admin_user(db)
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()