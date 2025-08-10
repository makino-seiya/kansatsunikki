from fastapi import FastAPI, Depends, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import logging
import traceback
from typing import List, Dict, Any

from database import get_db
from init_data import main as init_database
from admin import setup_admin
from minio_client import minio_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Custom exception handler
class APIException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code

def create_error_response(status_code: int, message: str, error_code: str = None, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """統一されたエラーレスポンス形式"""
    response = {
        "success": False,
        "error": {
            "code": error_code or f"ERROR_{status_code}",
            "message": message,
            "status_code": status_code
        }
    }
    if details:
        response["error"]["details"] = details
    return response

def create_success_response(data: Any = None, message: str = None) -> Dict[str, Any]:
    """統一された成功レスポンス形式"""
    response = {
        "success": True
    }
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return response

# Create FastAPI app
app = FastAPI(
    title="Plant Growth Tracker API",
    description="API for tracking plant growth records",
    version="1.0.0"
)

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=exc.detail,
            error_code=getattr(exc, 'error_code', None)
        )
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            status_code=500,
            message="内部サーバーエラーが発生しました",
            error_code="INTERNAL_SERVER_ERROR"
        )
    )

# Session middleware for admin authentication
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key")
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://kansatsu.astra-bc.co.jp",
        "https://kansatsu.astra-bc.co.jp"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup admin interface
admin = setup_admin(app)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

@app.get("/")
async def root():
    return {"message": "Plant Growth Tracker API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/plants")
async def get_plants(db: Session = Depends(get_db)):
    """Get all active plants"""
    from models import Plant
    plants = db.query(Plant).filter(Plant.is_active == True).order_by(Plant.display_order).all()
    return [{"id": p.id, "name": p.name, "display_order": p.display_order} for p in plants]

@app.get("/api/records")
async def get_records(db: Session = Depends(get_db)):
    """Get all records with plant data"""
    from models import Record, PlantRecord, Plant
    
    records = db.query(Record).order_by(Record.record_date.desc()).all()
    result = []
    
    for record in records:
        plants_data = []
        for plant_record in record.plant_records:
            plants_data.append({
                "type": plant_record.plant.name,
                "height": float(plant_record.height) if plant_record.height else None,
                "comment": plant_record.comment or "",
                "image": f"/api/images/{plant_record.image_filename}" if plant_record.image_filename else None
            })
        
        result.append({
            "id": record.id,
            "date": record.record_date.isoformat(),
            "createdAt": record.created_at.isoformat(),
            "weather": record.weather.value,
            "temperature": float(record.temperature),
            "plants": plants_data
        })
    
    return result

@app.get("/api/records/today")
async def get_today_record(db: Session = Depends(get_db), force_date: str = None):
    """Check if today's record exists"""
    from models import Record
    from datetime import date, datetime
    import os
    
    # タイムゾーン情報を取得
    timezone_info = os.environ.get('TZ', 'システムデフォルト')
    
    if force_date:
        try:
            today = datetime.strptime(force_date, '%Y-%m-%d').date()
            logger.info(f"強制指定された日付を使用: {today}")
        except ValueError:
            logger.error(f"無効な日付形式: {force_date}")
            # JST時刻を計算
            from datetime import timezone, timedelta
            jst = timezone(timedelta(hours=9))
            today = datetime.now(jst).date()
    else:
        # JST時刻を計算
        from datetime import timezone, timedelta
        jst = timezone(timedelta(hours=9))
        today = datetime.now(jst).date()
        logger.info(f"JST時刻から計算された日付: {today}")
    
    current_time = datetime.now()
    logger.info(f"=== 今日の記録チェック開始 ===")
    logger.info(f"サーバー時刻: {current_time}")
    logger.info(f"サーバー日付: {date.today()}")
    logger.info(f"検索対象日付: {today}")
    logger.info(f"タイムゾーン: {timezone_info}")
    logger.info(f"force_date パラメータ: {force_date}")
    
    # 全ての記録を確認（デバッグ用）
    all_records = db.query(Record).order_by(Record.record_date.desc()).limit(10).all()
    logger.info(f"データベース内の最新10件の記録:")
    for record in all_records:
        logger.info(f"  ID={record.id}, 日付={record.record_date}, 作成日時={record.created_at}")
    
    # 今日の日付で検索
    existing_record = db.query(Record).filter(Record.record_date == today).first()
    logger.info(f"今日の日付({today})での検索結果: {'見つかった' if existing_record else '見つからない'}")
    
    if existing_record:
        logger.info(f"!!! 警告: 今日の記録が見つかりました !!!")
        logger.info(f"記録ID: {existing_record.id}")
        logger.info(f"記録日付: {existing_record.record_date}")
        logger.info(f"今日の日付: {today}")
        logger.info(f"日付が一致: {existing_record.record_date == today}")
        
        # 日付が本当に今日と一致するかを再確認
        if existing_record.record_date != today:
            logger.error(f"!!! 重大なエラー: 記録の日付({existing_record.record_date})が今日({today})と一致しません !!!")
            return {"exists": False}
        
        plants_data = []
        for plant_record in existing_record.plant_records:
            plants_data.append({
                "type": plant_record.plant.id,  # 植物IDを返す
                "height": float(plant_record.height) if plant_record.height else None,
                "comment": plant_record.comment or "",
                "image": f"/api/images/{plant_record.image_filename}" if plant_record.image_filename else None
            })
        
        logger.info(f"今日の記録を返します: 日付={existing_record.record_date.isoformat()}")
        return {
            "exists": True,
            "record": {
                "id": existing_record.id,
                "date": existing_record.record_date.isoformat(),
                "createdAt": existing_record.created_at.isoformat(),
                "weather": existing_record.weather.value,
                "temperature": float(existing_record.temperature),
                "plants": plants_data
            }
        }
    else:
        logger.info(f"今日({today})の記録は存在しません - 新規入力可能")
        return {"exists": False}

@app.get("/api/records/{record_id}")
async def get_record(record_id: int, db: Session = Depends(get_db)):
    """Get a specific record by ID"""
    from models import Record, PlantRecord, Plant
    from fastapi import HTTPException
    
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="記録が見つかりません")
    
    plants_data = []
    for plant_record in record.plant_records:
        plants_data.append({
            "type": plant_record.plant.id,  # 植物IDを返す
            "height": float(plant_record.height) if plant_record.height else None,
            "comment": plant_record.comment or "",
            "image": f"/api/images/{plant_record.image_filename}" if plant_record.image_filename else None
        })
    
    return {
        "id": record.id,
        "date": record.record_date.isoformat(),
        "createdAt": record.created_at.isoformat(),
        "weather": record.weather.value,
        "temperature": float(record.temperature),
        "plants": plants_data
    }

@app.post("/api/records")
async def create_record(record_data: dict, db: Session = Depends(get_db)):
    """Create a new record"""
    from models import Record, PlantRecord, Plant, WeatherEnum
    from datetime import date, datetime, timezone, timedelta
    from fastapi import HTTPException
    
    try:
        logger.info("=== 記録作成API開始 ===")
        logger.info(f"受信データ: {record_data}")
        
        # JST時刻を使用
        jst = timezone(timedelta(hours=9))
        record_date = datetime.now(jst).date()
        logger.info(f"使用する日付（JST）: {record_date}")
        
        # Check if record already exists for today
        existing_record = db.query(Record).filter(Record.record_date == record_date).first()
        if existing_record:
            logger.error(f"重複エラー: 日付 {record_date} の記録が既に存在します (ID: {existing_record.id})")
            logger.error(f"既存記録の詳細: 作成日時={existing_record.created_at}, 天気={existing_record.weather.value}")
            
            # より詳細なエラーメッセージを返す
            error_detail = {
                "error": "DUPLICATE_RECORD",
                "message": "今日の記録は既に存在します",
                "existing_record": {
                    "id": existing_record.id,
                    "date": existing_record.record_date.isoformat(),
                    "created_at": existing_record.created_at.isoformat()
                }
            }
            raise HTTPException(status_code=400, detail=error_detail)
        
        # Validate required fields
        if 'weather' not in record_data:
            logger.error("天気データが不足しています")
            raise HTTPException(status_code=400, detail="天気データが必要です")
        
        if 'temperature' not in record_data:
            logger.error("気温データが不足しています")
            raise HTTPException(status_code=400, detail="気温データが必要です")
        
        # Create main record
        weather_map = {
            'sunny': WeatherEnum.sunny,
            'cloudy': WeatherEnum.cloudy,
            'rainy': WeatherEnum.rainy,
            'thunder': WeatherEnum.thunder,
            '晴れ': WeatherEnum.sunny,
            '曇り': WeatherEnum.cloudy,
            '雨': WeatherEnum.rainy,
            '雷': WeatherEnum.thunder
        }
        
        weather_value = record_data['weather']
        if weather_value not in weather_map:
            logger.error(f"無効な天気値: {weather_value}")
            raise HTTPException(status_code=400, detail=f"無効な天気値: {weather_value}")
        
        try:
            temperature_value = float(record_data['temperature'])
        except (ValueError, TypeError):
            logger.error(f"無効な気温値: {record_data['temperature']}")
            raise HTTPException(status_code=400, detail=f"無効な気温値: {record_data['temperature']}")
        
        logger.info(f"メインレコード作成: 日付={record_date}, 天気={weather_value}, 気温={temperature_value}")
        
        db_record = Record(
            record_date=record_date,
            weather=weather_map[weather_value],
            temperature=temperature_value
        )
        db.add(db_record)
        db.flush()  # Get the ID
        
        # Create plant records
        plants = db.query(Plant).all()
        plant_name_to_id = {p.name: p.id for p in plants}
        
        for plant_name, plant_data in record_data['plantRecords'].items():
            # Check if there's any meaningful data for this plant
            height_value = plant_data.get('height')
            comment_value = plant_data.get('comment')
            
            # Convert empty strings to None
            if height_value == '':
                height_value = None
            if comment_value == '':
                comment_value = None
                
            # Only create record if there's meaningful data
            if height_value or comment_value:
                # Map plant names to IDs
                plant_id = None
                if plant_name == '1':  # ひまわり
                    plant_id = plant_name_to_id.get('向日葵（ひまわり）')
                elif plant_name == '2':  # コスモス
                    plant_id = plant_name_to_id.get('秋桜（コスモス）')
                elif plant_name == '3':  # 朝顔（あさがお）
                    plant_id = plant_name_to_id.get('朝顔（あさがお）')
                
                if plant_id:
                    try:
                        height_float = float(height_value) if height_value else None
                    except (ValueError, TypeError):
                        height_float = None
                        
                    # Get image filename if provided
                    image_filename = plant_data.get('imageFilename')
                    
                    db_plant_record = PlantRecord(
                        record_id=db_record.id,
                        plant_id=plant_id,
                        height=height_float,
                        comment=comment_value,
                        image_filename=image_filename
                    )
                    db.add(db_plant_record)
        
        db.commit()
        db.refresh(db_record)
        
        return {"message": "記録を保存しました", "id": db_record.id}
        
    except HTTPException:
        # Re-raise HTTP exceptions (like duplicate record)
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        import traceback
        logger.error(f"Error creating record: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Record data: {record_data}")
        raise HTTPException(status_code=500, detail=f"記録の保存に失敗しました: {str(e)}")

@app.put("/api/records/{record_id}")
async def update_record(record_id: int, record_data: dict, db: Session = Depends(get_db)):
    """Update an existing record"""
    from models import Record, PlantRecord, Plant, WeatherEnum
    from fastapi import HTTPException
    
    try:
        # Get existing record
        db_record = db.query(Record).filter(Record.id == record_id).first()
        if not db_record:
            raise HTTPException(status_code=404, detail="記録が見つかりません")
        
        # Update main record fields
        if 'weather' in record_data:
            weather_map = {
                '晴れ': WeatherEnum.sunny,
                '曇り': WeatherEnum.cloudy,
                '雨': WeatherEnum.rainy,
                '雷': WeatherEnum.thunder,
                'sunny': WeatherEnum.sunny,
                'cloudy': WeatherEnum.cloudy,
                'rainy': WeatherEnum.rainy,
                'thunder': WeatherEnum.thunder
            }
            db_record.weather = weather_map.get(record_data['weather'], WeatherEnum.sunny)
        
        if 'temperature' in record_data:
            db_record.temperature = float(record_data['temperature'])
        
        if 'date' in record_data:
            from datetime import datetime
            db_record.record_date = datetime.fromisoformat(record_data['date']).date()
        
        # Update plant records
        if 'plantRecords' in record_data:
            # Get all plants for mapping
            plants = db.query(Plant).all()
            plant_id_to_name = {p.id: p.name for p in plants}
            
            # Delete existing plant records
            db.query(PlantRecord).filter(PlantRecord.record_id == record_id).delete()
            
            # Create new plant records
            for plant_id_str, plant_data in record_data['plantRecords'].items():
                plant_id = int(plant_id_str)
                height = plant_data.get('height')
                comment = plant_data.get('comment', '')
                image_filename = plant_data.get('imageFilename')
                
                # Only create record if there's meaningful data
                if height is not None or comment or image_filename:
                    # Check if plant exists
                    if plant_id in plant_id_to_name:
                        db_plant_record = PlantRecord(
                            record_id=record_id,
                            plant_id=plant_id,
                            height=float(height) if height is not None and height != '' else None,
                            comment=comment,
                            image_filename=image_filename
                        )
                        db.add(db_plant_record)
        
        db.commit()
        db.refresh(db_record)
        
        return {"message": "記録を更新しました", "id": db_record.id}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        import traceback
        logger.error(f"Error updating record: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"記録の更新に失敗しました: {str(e)}")

@app.delete("/api/records/{record_id}")
async def delete_record(record_id: int, db: Session = Depends(get_db)):
    """Delete a record"""
    from models import Record, PlantRecord
    from fastapi import HTTPException
    
    try:
        # Get existing record
        db_record = db.query(Record).filter(Record.id == record_id).first()
        if not db_record:
            raise HTTPException(status_code=404, detail="記録が見つかりません")
        
        # Delete plant records first (due to foreign key constraint)
        db.query(PlantRecord).filter(PlantRecord.record_id == record_id).delete()
        
        # Delete main record
        db.delete(db_record)
        db.commit()
        
        return {"message": "記録を削除しました"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        import traceback
        logger.error(f"Error deleting record: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"記録の削除に失敗しました: {str(e)}")

@app.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image to MinIO"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="画像ファイルのみアップロード可能です")
        
        # Validate file size (3MB)
        file_data = await file.read()
        if len(file_data) > 3 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ファイルサイズは3MB以下にしてください")
        
        # Get file extension
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        
        # Upload to MinIO
        filename = minio_client.upload_image(file_data, file_extension)
        
        return {
            "filename": filename,
            "url": minio_client.get_image_url(filename)
        }
        
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="画像のアップロードに失敗しました")

@app.get("/api/images/{filename}")
async def get_image(filename: str):
    """Get image directly from MinIO"""
    from fastapi.responses import StreamingResponse
    from io import BytesIO
    import mimetypes
    
    try:
        # Get image data from MinIO
        image_data = minio_client.get_image(filename)
        
        # Determine content type based on file extension
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type or not content_type.startswith('image/'):
            content_type = 'image/jpeg'  # Default fallback
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(image_data),
            media_type=content_type
        )
    except Exception as e:
        logger.error(f"Error getting image: {e}")
        raise HTTPException(status_code=404, detail="画像が見つかりません")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)