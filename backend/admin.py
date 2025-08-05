from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import User, Plant, Record, PlantRecord
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        
        # Check credentials
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user and pwd_context.verify(password, user.password_hash):
                # Store user info in session
                request.session.update({"user": username})
                return True
        finally:
            db.close()
        
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("user") is not None

# Authentication backend
authentication_backend = AdminAuth(secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key"))

# Admin views
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.created_at]
    column_searchable_list = [User.username]
    column_sortable_list = [User.id, User.username, User.created_at]
    can_create = True
    can_edit = True
    can_delete = True
    name = "ユーザー"
    name_plural = "ユーザー管理"

class PlantAdmin(ModelView, model=Plant):
    column_list = [Plant.id, Plant.name, Plant.display_order, Plant.is_active, Plant.created_at]
    column_searchable_list = [Plant.name]
    column_sortable_list = [Plant.id, Plant.name, Plant.display_order, Plant.created_at]
    can_create = True
    can_edit = True
    can_delete = True
    name = "植物種類"
    name_plural = "植物種類管理"

class RecordAdmin(ModelView, model=Record):
    column_list = [Record.id, Record.record_date, Record.weather, Record.temperature, Record.created_at]
    column_searchable_list = [Record.record_date]
    column_sortable_list = [Record.id, Record.record_date, Record.created_at]
    column_filters = [Record.weather, Record.record_date]
    can_create = True
    can_edit = True
    can_delete = True
    name = "記録"
    name_plural = "記録管理"

class PlantRecordAdmin(ModelView, model=PlantRecord):
    column_list = [PlantRecord.id, PlantRecord.record_id, PlantRecord.plant_id, 
                   PlantRecord.height, PlantRecord.comment, PlantRecord.created_at]
    column_sortable_list = [PlantRecord.id, PlantRecord.record_id, PlantRecord.created_at]
    can_create = True
    can_edit = True
    can_delete = True
    name = "植物記録"
    name_plural = "植物記録管理"

def setup_admin(app):
    """Setup SQLAdmin"""
    admin = Admin(
        app, 
        engine, 
        authentication_backend=authentication_backend,
        title="植物成長記録 管理画面",
        logo_url=None,
    )
    
    # Add views
    admin.add_view(UserAdmin)
    admin.add_view(PlantAdmin)
    admin.add_view(RecordAdmin)
    admin.add_view(PlantRecordAdmin)
    
    return admin