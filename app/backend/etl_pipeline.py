"""ETL/ELT Pipeline for Movie Streaming Analytics"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timedelta
from data_generator import StreamingDataGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingETLPipeline:
    def __init__(self, mongo_url, db_name):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
        self.generator = StreamingDataGenerator()
    
    async def create_indexes(self):
        """Create indexes for optimization (simulating Snowflake clustering)"""
        logger.info("Creating indexes for performance optimization...")
        
        # Movies indexes
        await self.db.movies.create_index('genre')
        await self.db.movies.create_index('release_date')
        await self.db.movies.create_index([('avg_rating', -1)])
        await self.db.movies.create_index('country')
        
        # Users indexes
        await self.db.users.create_index('country')
        await self.db.users.create_index('subscription_type')
        await self.db.users.create_index('signup_date')
        await self.db.users.create_index('is_active')
        
        # Viewing sessions indexes (partitioning simulation)
        await self.db.viewing_sessions.create_index([('start_time', -1)])
        await self.db.viewing_sessions.create_index('user_id')
        await self.db.viewing_sessions.create_index('movie_id')
        await self.db.viewing_sessions.create_index('device_type')
        await self.db.viewing_sessions.create_index('user_country')
        await self.db.viewing_sessions.create_index([('movie_id', 1), ('start_time', -1)])
        
        # Ratings indexes
        await self.db.ratings.create_index([('movie_id', 1), ('rating', -1)])
        await self.db.ratings.create_index('user_id')
        await self.db.ratings.create_index([('rating_date', -1)])
        
        logger.info("Indexes created successfully")
    
    async def extract_and_load_data(self):
        """Extract and Load phase - Generate and load data into MongoDB"""
        logger.info("Starting ETL Pipeline - Extract & Load phase...")
        
        # Check if data already exists
        movie_count = await self.db.movies.count_documents({})
        if movie_count > 0:
            logger.info(f"Data already exists. Movies: {movie_count}")
            return
        
        # Generate data
        logger.info("Generating movies...")
        movies = self.generator.generate_movies(200)
        await self.db.movies.insert_many(movies)
        logger.info(f"Loaded {len(movies)} movies")
        
        logger.info("Generating users...")
        users = self.generator.generate_users(5000)
        await self.db.users.insert_many(users)
        logger.info(f"Loaded {len(users)} users")
        
        logger.info("Generating viewing sessions...")
        sessions = self.generator.generate_viewing_sessions(50000)
        # Batch insert for performance
        batch_size = 5000
        for i in range(0, len(sessions), batch_size):
            await self.db.viewing_sessions.insert_many(sessions[i:i+batch_size])
        logger.info(f"Loaded {len(sessions)} viewing sessions")
        
        logger.info("Generating ratings...")
        ratings = self.generator.generate_ratings(20000)
        for i in range(0, len(ratings), batch_size):
            await self.db.ratings.insert_many(ratings[i:i+batch_size])
        logger.info(f"Loaded {len(ratings)} ratings")
    
    async def transform_and_aggregate(self):
        """Transform phase - Create aggregated analytics (ELT approach)"""
        logger.info("Starting Transform phase - Creating analytics...")
        
        # 1. Update movie view counts
        pipeline = [
            {'$group': {
                '_id': '$movie_id',
                'total_views': {'$sum': 1},
                'avg_completion_rate': {'$avg': '$completion_rate'},
                'total_watch_time': {'$sum': '$watch_duration_minutes'}
            }}
        ]
        
        async for result in self.db.viewing_sessions.aggregate(pipeline):
            await self.db.movies.update_one(
                {'id': result['_id']},
                {'$set': {
                    'total_views': result['total_views'],
                    'avg_completion_rate': round(result['avg_completion_rate'], 2),
                    'total_watch_time_minutes': result['total_watch_time']
                }}
            )
        
        logger.info("Movie statistics updated")
        
        # 2. Create daily analytics cache
        await self.create_daily_analytics()
        
        # 3. Create genre analytics
        await self.create_genre_analytics()
        
        logger.info("Transform phase completed")
    
    async def create_daily_analytics(self):
        """Create daily aggregated analytics for dashboard performance"""
        logger.info("Creating daily analytics cache...")
        
        # Clear existing cache
        await self.db.daily_analytics.delete_many({})
        
        # Aggregate by date
        pipeline = [
            {'$addFields': {
                'date': {'$dateFromString': {'dateString': '$start_time'}}
            }},
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$date'}},
                'total_views': {'$sum': 1},
                'unique_users': {'$addToSet': '$user_id'},
                'total_watch_time': {'$sum': '$watch_duration_minutes'},
                'avg_completion_rate': {'$avg': '$completion_rate'},
                'device_breakdown': {'$push': '$device_type'}
            }},
            {'$project': {
                'date': '$_id',
                'total_views': 1,
                'unique_users': {'$size': '$unique_users'},
                'total_watch_time': 1,
                'avg_completion_rate': 1,
                'device_breakdown': 1
            }},
            {'$sort': {'_id': 1}}
        ]
        
        results = []
        async for doc in self.db.viewing_sessions.aggregate(pipeline):
            results.append({
                'id': doc['_id'],
                'date': doc['_id'],
                'total_views': doc['total_views'],
                'unique_users': doc['unique_users'],
                'total_watch_time': doc['total_watch_time'],
                'avg_completion_rate': round(doc.get('avg_completion_rate', 0), 2),
                'created_at': datetime.utcnow().isoformat()
            })
        
        if results:
            await self.db.daily_analytics.insert_many(results)
            logger.info(f"Created {len(results)} daily analytics records")
    
    async def create_genre_analytics(self):
        """Create genre performance analytics"""
        logger.info("Creating genre analytics...")
        
        # Clear existing
        await self.db.genre_analytics.delete_many({})
        
        # Aggregate by genre
        pipeline = [
            {'$lookup': {
                'from': 'movies',
                'localField': 'movie_id',
                'foreignField': 'id',
                'as': 'movie_info'
            }},
            {'$unwind': '$movie_info'},
            {'$group': {
                '_id': '$movie_info.genre',
                'total_views': {'$sum': 1},
                'avg_watch_time': {'$avg': '$watch_duration_minutes'},
                'avg_completion_rate': {'$avg': '$completion_rate'},
                'unique_users': {'$addToSet': '$user_id'}
            }},
            {'$project': {
                'genre': '$_id',
                'total_views': 1,
                'avg_watch_time': {'$round': ['$avg_watch_time', 2]},
                'avg_completion_rate': {'$round': ['$avg_completion_rate', 2]},
                'unique_users': {'$size': '$unique_users'}
            }},
            {'$sort': {'total_views': -1}}
        ]
        
        results = []
        async for doc in self.db.viewing_sessions.aggregate(pipeline):
            results.append({
                'id': doc['_id'],
                'genre': doc['_id'],
                'total_views': doc['total_views'],
                'avg_watch_time': doc['avg_watch_time'],
                'avg_completion_rate': doc['avg_completion_rate'],
                'unique_users': doc['unique_users'],
                'created_at': datetime.utcnow().isoformat()
            })
        
        if results:
            await self.db.genre_analytics.insert_many(results)
            logger.info(f"Created {len(results)} genre analytics records")
    
    async def run_full_pipeline(self):
        """Run complete ETL pipeline"""
        logger.info("=" * 50)
        logger.info("STARTING FULL ETL/ELT PIPELINE")
        logger.info("=" * 50)
        
        try:
            # Extract & Load
            await self.extract_and_load_data()
            
            # Create indexes (optimization)
            await self.create_indexes()
            
            # Transform & Aggregate
            await self.transform_and_aggregate()
            
            logger.info("=" * 50)
            logger.info("ETL/ELT PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
        finally:
            self.client.close()


async def main():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'streaming_analytics')
    
    pipeline = StreamingETLPipeline(mongo_url, db_name)
    await pipeline.run_full_pipeline()

if __name__ == "__main__":
    asyncio.run(main())
