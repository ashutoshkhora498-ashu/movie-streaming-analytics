"""Apache Spark Batch Processing for Movie Streaming Analytics"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum, count, window, desc, hour, dayofweek
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkStreamingProcessor:
    """Simulates Apache Spark Batch and Streaming Processing"""
    
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("MovieStreamingAnalytics") \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark Session initialized")
    
    def batch_process_viewing_patterns(self, sessions_data):
        """Batch processing: Analyze viewing patterns"""
        logger.info("Starting Spark batch processing for viewing patterns...")
        
        if not sessions_data:
            logger.warning("No session data provided")
            return None
        
        # Create DataFrame
        df = self.spark.createDataFrame(sessions_data)
        
        # Window function example: Ranking movies by views
        from pyspark.sql.window import Window
        from pyspark.sql.functions import rank, row_number
        
        window_spec = Window.partitionBy("device_type").orderBy(desc("watch_duration_minutes"))
        
        ranked_df = df.withColumn("rank", rank().over(window_spec)) \
                      .withColumn("row_num", row_number().over(window_spec))
        
        # Aggregate by device type
        device_analytics = df.groupBy("device_type") \
            .agg(
                count("*").alias("total_sessions"),
                avg("watch_duration_minutes").alias("avg_watch_duration"),
                avg("completion_rate").alias("avg_completion_rate"),
                sum("buffering_count").alias("total_buffering")
            ) \
            .orderBy(desc("total_sessions"))
        
        logger.info("Device Analytics:")
        device_analytics.show()
        
        # Time-based analysis (CTE equivalent using temp views)
        df.createOrReplaceTempView("sessions")
        
        # Complex SQL with CTEs
        time_analysis = self.spark.sql("""
            WITH hourly_stats AS (
                SELECT 
                    hour(start_time) as hour_of_day,
                    COUNT(*) as session_count,
                    AVG(completion_rate) as avg_completion,
                    AVG(watch_duration_minutes) as avg_duration
                FROM sessions
                GROUP BY hour(start_time)
            ),
            peak_hours AS (
                SELECT 
                    hour_of_day,
                    session_count,
                    avg_completion,
                    RANK() OVER (ORDER BY session_count DESC) as popularity_rank
                FROM hourly_stats
            )
            SELECT * FROM peak_hours
            ORDER BY popularity_rank
        """)
        
        logger.info("Peak Viewing Hours:")
        time_analysis.show()
        
        return {
            'device_analytics': device_analytics.collect(),
            'time_analysis': time_analysis.collect()
        }
    
    def batch_process_content_performance(self, movies_data, ratings_data, sessions_data):
        """Batch processing: Content performance analysis"""
        logger.info("Analyzing content performance with Spark...")
        
        if not movies_data or not sessions_data:
            return None
        
        movies_df = self.spark.createDataFrame(movies_data)
        sessions_df = self.spark.createDataFrame(sessions_data)
        
        # Join operations (similar to Snowflake joins)
        content_performance = sessions_df.groupBy("movie_id") \
            .agg(
                count("*").alias("view_count"),
                avg("completion_rate").alias("avg_completion"),
                sum("watch_duration_minutes").alias("total_watch_time")
            ) \
            .join(movies_df, sessions_df.movie_id == movies_df.id, "inner") \
            .select(
                movies_df.title,
                movies_df.genre,
                col("view_count"),
                col("avg_completion"),
                col("total_watch_time")
            ) \
            .orderBy(desc("view_count")) \
            .limit(20)
        
        logger.info("Top Performing Content:")
        content_performance.show()
        
        return content_performance.collect()
    
    def simulate_streaming_analytics(self, sessions_data):
        """Simulates streaming processing for real-time analytics"""
        logger.info("Simulating Spark Streaming for real-time analytics...")
        
        if not sessions_data:
            return None
        
        df = self.spark.createDataFrame(sessions_data)
        
        # Simulate streaming window aggregations
        # In real streaming, this would process micro-batches
        
        # Real-time quality monitoring
        quality_monitoring = df.groupBy("quality", "device_type") \
            .agg(
                count("*").alias("session_count"),
                avg("buffering_count").alias("avg_buffering"),
                avg("completion_rate").alias("avg_completion")
            ) \
            .orderBy(desc("session_count"))
        
        logger.info("Real-time Quality Monitoring:")
        quality_monitoring.show()
        
        # Geographic distribution
        geo_distribution = df.groupBy("user_country") \
            .agg(
                count("*").alias("total_views"),
                avg("completion_rate").alias("avg_engagement")
            ) \
            .orderBy(desc("total_views"))
        
        logger.info("Geographic Distribution:")
        geo_distribution.show()
        
        return {
            'quality_monitoring': quality_monitoring.collect(),
            'geo_distribution': geo_distribution.collect()
        }
    
    def close(self):
        """Close Spark session"""
        self.spark.stop()
        logger.info("Spark session closed")


if __name__ == "__main__":
    processor = SparkStreamingProcessor()
    logger.info("Spark processor initialized for batch and streaming analytics")
    processor.close()
