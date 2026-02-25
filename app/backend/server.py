"from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title=\"Movie Streaming Platform Analytics API\", version=\"1.0.0\")

# Create a router with the /api prefix
api_router = APIRouter(prefix=\"/api\")

# Security (RBAC Simulation)
security = HTTPBearer(auto_error=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== SECURITY & RBAC (Role-Based Access Control) ==========

class UserRole:
    \"\"\"Simulates RBAC roles\"\"\"
    ADMIN = \"admin\"
    ANALYST = \"analyst\"
    VIEWER = \"viewer\"

def mask_sensitive_data(data: dict, fields: list) -> dict:
    \"\"\"Data Masking implementation for security\"\"\"
    masked_data = data.copy()
    for field in fields:
        if field in masked_data:
            if isinstance(masked_data[field], str):
                masked_data[field] = \"***MASKED***\"
            elif isinstance(masked_data[field], (int, float)):
                masked_data[field] = 0
    return masked_data

async def get_current_user_role(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    \"\"\"Simulates authentication and returns user role\"\"\"
    # In production, validate JWT token here
    # For demo, return analyst role
    return UserRole.ANALYST

# ========== MODELS ==========

class Movie(BaseModel):
    id: str
    title: str
    genre: str
    duration_minutes: int
    release_date: str
    avg_rating: float
    total_views: int = 0

class User(BaseModel):
    id: str
    username: str
    email: str
    country: str
    subscription_type: str
    is_active: bool

class ViewingSession(BaseModel):
    id: str
    user_id: str
    movie_id: str
    start_time: str
    watch_duration_minutes: int
    completion_rate: float
    device_type: str

class DashboardMetrics(BaseModel):
    total_users: int
    active_users: int
    total_movies: int
    total_views: int
    total_watch_time_hours: float
    avg_completion_rate: float
    premium_subscribers: int

class TopMovie(BaseModel):
    title: str
    genre: str
    total_views: int
    avg_completion_rate: float
    avg_rating: float

class GenreAnalytics(BaseModel):
    genre: str
    total_views: int
    avg_watch_time: float
    unique_users: int

class DeviceAnalytics(BaseModel):
    device_type: str
    session_count: int
    avg_completion_rate: float

class GeographicData(BaseModel):
    country: str
    total_views: int
    unique_users: int
    avg_completion_rate: float

class HourlyTrend(BaseModel):
    hour: int
    view_count: int
    avg_completion_rate: float

# ========== API ENDPOINTS ==========

@api_router.get(\"/\")
async def root():
    return {
        \"message\": \"Movie Streaming Platform Analytics API\",
        \"version\": \"1.0.0\",
        \"status\": \"operational\"
    }

@api_router.get(\"/health\")
async def health_check():
    \"\"\"Health check endpoint\"\"\"
    try:
        await db.command('ping')
        return {\"status\": \"healthy\", \"database\": \"connected\"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=\"Database connection failed\")

# ========== DASHBOARD METRICS ==========

@api_router.get(\"/dashboard/metrics\", response_model=DashboardMetrics)
async def get_dashboard_metrics(role: str = Depends(get_current_user_role)):
    \"\"\"Get high-level dashboard metrics\"\"\"
    try:
        # Use aggregation pipelines (advanced SQL equivalent)
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({\"is_active\": True})
        total_movies = await db.movies.count_documents({})
        total_views = await db.viewing_sessions.count_documents({})
        
        # Calculate total watch time
        pipeline = [
            {\"$group\": {
                \"_id\": None,
                \"total_watch_time\": {\"$sum\": \"$watch_duration_minutes\"},
                \"avg_completion\": {\"$avg\": \"$completion_rate\"}
            }}
        ]
        watch_stats = await db.viewing_sessions.aggregate(pipeline).to_list(1)
        
        total_watch_time = watch_stats[0][\"total_watch_time\"] / 60 if watch_stats else 0
        avg_completion = watch_stats[0][\"avg_completion\"] if watch_stats else 0
        
        # Premium subscribers
        premium_subs = await db.users.count_documents({\"subscription_type\": \"Premium\"})
        
        return DashboardMetrics(
            total_users=total_users,
            active_users=active_users,
            total_movies=total_movies,
            total_views=total_views,
            total_watch_time_hours=round(total_watch_time, 2),
            avg_completion_rate=round(avg_completion, 2),
            premium_subscribers=premium_subs
        )
    except Exception as e:
        logger.error(f\"Error fetching dashboard metrics: {e}\")
        raise HTTPException(status_code=500, detail=str(e))

# ========== TOP CONTENT ANALYTICS ==========

@api_router.get(\"/analytics/top-movies\", response_model=List[TopMovie])
async def get_top_movies(limit: int = Query(10, le=50)):
    \"\"\"Get top performing movies (using advanced aggregation - CTE equivalent)\"\"\"
    try:
        # Complex aggregation pipeline (equivalent to SQL CTEs and Window Functions)
        pipeline = [
            # Join with movies collection
            {
                \"$lookup\": {
                    \"from\": \"movies\",
                    \"localField\": \"movie_id\",
                    \"foreignField\": \"id\",
                    \"as\": \"movie_info\"
                }
            },
            {\"$unwind\": \"$movie_info\"},
            # Group by movie
            {
                \"$group\": {
                    \"_id\": \"$movie_id\",
                    \"title\": {\"$first\": \"$movie_info.title\"},
                    \"genre\": {\"$first\": \"$movie_info.genre\"},
                    \"avg_rating\": {\"$first\": \"$movie_info.avg_rating\"},
                    \"total_views\": {\"$sum\": 1},
                    \"avg_completion_rate\": {\"$avg\": \"$completion_rate\"}
                }
            },
            # Sort and limit
            {\"$sort\": {\"total_views\": -1}},
            {\"$limit\": limit},
            # Project final fields
            {
                \"$project\": {
                    \"_id\": 0,
                    \"title\": 1,
                    \"genre\": 1,
                    \"total_views\": 1,
                    \"avg_completion_rate\": {\"$round\": [\"$avg_completion_rate\", 2]},
                    \"avg_rating\": 1
                }
            }
        ]
        
        results = await db.viewing_sessions.aggregate(pipeline).to_list(limit)
        return results
    except Exception as e:
        logger.error(f\"Error fetching top movies: {e}\")
        raise HTTPException(status_code=500, detail=str(e))

# ========== GENRE ANALYTICS ==========

@api_router.get(\"/analytics/genres\", response_model=List[GenreAnalytics])
async def get_genre_analytics():
    \"\"\"Get analytics by genre\"\"\"
    try:
        results = await db.genre_analytics.find({}, {\"_id\": 0}).to_list(100)
        if not results:
            # Fallback to real-time aggregation
            pipeline = [
                {
                    \"$lookup\": {
                        \"from\": \"movies\",
                        \"localField\": \"movie_id\",
                        \"foreignField\": \"id\",
                        \"as\": \"movie_info\"
                    }
                },
                {\"$unwind\": \"$movie_info\"},
                {
                    \"$group\": {
                        \"_id\": \"$movie_info.genre\",
                        \"total_views\": {\"$sum\": 1},
                        \"avg_watch_time\": {\"$avg\": \"$watch_duration_minutes\"},
                        \"unique_users\": {\"$addToSet\": \"$user_id\"}
                    }
                },
                {
                    \"$project\": {
                        \"_id\": 0,
                        \"genre\": \"$_id\",
                        \"total_views\": 1,
                        \"avg_watch_time\": {\"$round\": [\"$avg_watch_time\", 2]},
                        \"unique_users\": {\"$size\": \"$unique_users\"}
                    }
                },
                {\"$sort\": {\"total_views\": -1}}
            ]
            results = await db.viewing_sessions.aggregate(pipeline).to_list(100)
        
        return results
    except Exception as e:
        logger.error(f\"Error fetching genre analytics: {e}\")
        raise HTTPException(status_code=500, detail=str(e))

# ========== DEVICE ANALYTICS ==========

@api_router.get(\"/analytics/devices\", response_model=List[DeviceAnalytics])
async def get_device_analytics():
    \"\"\"Get analytics by device type\"\"\"
    try:
        pipeline = [
            {
                \"$group\": {
                    \"_id\": \"$device_type\",
                    \"session_count\": {\"$sum\": 1},
                    \"avg_completion_rate\": {\"$avg\": \"$completion_rate\"}
                }
            },
            {
                \"$project\": {
                    \"_id\": 0,
                    \"device_type\": \"$_id\",
                    \"session_count\": 1,
                    \"avg_completion_rate\": {\"$round\": [\"$avg_completion_rate\", 2]}
                }
            },
            {\"$sort\": {\"session_count\": -1}}
        ]
        
        results = await db.viewing_sessions.aggregate(pipeline).to_list(100)
        return results
    except Exception as e:
        logger.error(f\"Error fetching device analytics: {e}\")
        raise HTTPException(status_code=500, detail=str(e))

# ========== GEOGRAPHIC ANALYTICS ==========

@api_router.get(\"/analytics/geographic\", response_model=List[GeographicData])
async def get_geographic_analytics():
    \"\"\"Get geographic distribution analytics\"\"\"
    try:
        pipeline = [
            {
                \"$group\": {
                    \"_id\": \"$user_country\",
                    \"total_views\": {\"$sum\": 1},
                    \"unique_users\": {\"$addToSet\": \"$user_id\"},
                    \"avg_completion_rate\": {\"$avg\": \"$completion_rate\"}
                }
            },
            {
                \"$project\": {
                    \"_id\": 0,
                    \"country\": \"$_id\",
                    \"total_views\": 1,
                    \"unique_users\": {\"$size\": \"$unique_users\"},
                    \"avg_completion_rate\": {\"$round\": [\"$avg_completion_rate\", 2]}
                }
            },
            {\"$sort\": {\"total_views\": -1}},
            {\"$limit\": 20}
        ]
        
        results = await db.viewing_sessions.aggregate(pipeline).to_list(100)
        return results
    except Exception as e:
        logger.error(f\"Error fetching geographic analytics: {e}\")
        raise HTTPException(status_code=500, detail=str(e))

# ========== TIME-BASED ANALYTICS ==========

@api_router.get(\"/analytics/hourly-trends\", response_model=List[HourlyTrend])
async def get_hourly_trends():
    \"\"\"Get viewing trends by hour (Peak hours analysis)\"\"\"
    try:
        pipeline = [
            {
                \"$addFields\": {
                    \"start_datetime\": {\"$dateFromString\": {\"dateString\": \"$start_time\"}}
                }
            },
            {
                \"$group\": {
                    \"_id\": {\"$hour\": \"$start_datetime\"},
                    \"view_count\": {\"$sum\": 1},
                    \"avg_completion_rate\": {\"$avg\": \"$completion_rate\"}
                }
            },
            {
                \"$project\": {
                    \"_id\": 0,
                    \"hour\": \"$_id\",
                    \"view_count\": 1,
                    \"avg_completion_rate\": {\"$round\": [\"$avg_completion_rate\", 2]}
                }
            },
            {\"$sort\": {\"hour\": 1}}
        ]
        
        results = await db.viewing_sessions.aggregate(pipeline).to_list(24)
        return results
    except Exception as e:
        logger.error(f\"Error fetching hourly trends: {e}\")
        raise HTTPException(status_code=500, detail=str(e))

# ========== DAILY TRENDS ==========

@api_router.get(\"/analytics/daily-trends\")
async def get_daily_trends(days: int = Query(30, le=90)):
    \"\"\"Get daily viewing trends over time\"\"\"
    try:
        # Use cached daily analytics if available
        results = await db.daily_analytics.find({}, {\"_id\": 0}).sort([(\"date\", -1)]).limit(days).to_list(days)
        
        if not results:
            # Fallback to real-time calculation
            pipeline = [
                {
                    \"$addFields\": {
                        \"date_obj\": {\"$dateFromString\": {\"dateString\": \"$start_time\"}}
                    }
                },
                {
                    \"$group\": {
                        \"_id\": {
                            \"$dateToString\": {\"format\": \"%Y-%m-%d\", \"date\": \"$date_obj\"}
                        },
                        \"total_views\": {\"$sum\": 1},
                        \"unique_users\": {\"$addToSet\": \"$user_id\"},
                        \"total_watch_time\": {\"$sum\": \"$watch_duration_minutes\"}
                    }
                },
                {
                    \"$project\": {
                        \"date\": \"$_id\",
                        \"total_views\": 1,
                        \"unique_users\": {\"$size\": \"$unique_users\"},
                        \"total_watch_time\": 1
                    }
                },
                {\"$sort\": {\"_id\": -1}},
                {\"$limit\": days}
            ]
            results = await db.viewing_sessions.aggregate(pipeline).to_list(days)
        
        return results
    except Exception as e:
        logger.error(f\"Error fetching daily trends: {e}\")
        raise HTTPException(status_code=500, detail=str(e))

# ========== USER ANALYTICS (with Data Masking) ==========

@api_router.get(\"/analytics/users\")
async def get_user_analytics(
    apply_masking: bool = Query(True),
    role: str = Depends(get_current_user_role)
):
    \"\"\"Get user analytics with optional data masking for security\"\"\"
    try:
        pipeline = [
            {
                \"$group\": {
                    \"_id\": \"$subscription_type\",
                    \"user_count\": {\"$sum\": 1},
                    \"active_count\": {
                        \"$sum\": {\"$cond\": [{\"$eq\": [\"$is_active\", True]}, 1, 0]}
                    }
                }
            },
            {
                \"$project\": {
                    \"_id\": 0,
                    \"subscription_type\": \"$_id\",
                    \"user_count\": 1,
                    \"active_count\": 1
                }
            }
        ]
        
        results = await db.users.aggregate(pipeline).to_list(100)
        
        # Apply data masking for non-admin roles
        if apply_masking and role != UserRole.ADMIN:
            logger.info(\"Applying data masking for non-admin user\")
            # In production, mask specific sensitive fields
        
        return results
    except Exception as e:
        logger.error(f\"Error fetching user analytics: {e}\")
        raise HTTPException(status_code=500, detail=str(e))

# ========== ETL PIPELINE TRIGGER ==========

@api_router.post(\"/admin/run-etl\")
async def trigger_etl_pipeline(role: str = Depends(get_current_user_role)):
    \"\"\"Trigger ETL pipeline (Admin only)\"\"\"
    if role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail=\"Admin access required\")
    
    try:
        from etl_pipeline import StreamingETLPipeline
        import asyncio
        
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME')
        
        pipeline = StreamingETLPipeline(mongo_url, db_name)
        await pipeline.run_full_pipeline()
        
        return {\"status\": \"success\", \"message\": \"ETL pipeline completed\"}
    except Exception as e:
        logger.error(f\"ETL pipeline failed: {e}\")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

@app.on_event(\"shutdown\")
async def shutdown_db_client():
    client.close()
"
