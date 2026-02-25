# Movie Streaming Platform Analytics - Project #25

## 🎯 Project Overview

A comprehensive data analytics platform for movie streaming services, implementing enterprise-grade data engineering practices including ETL/ELT pipelines, batch processing, advanced analytics, and real-time visualization.

## 📊 Architecture Overview

### Data Architecture (Star/Snowflake Schema)

```
                    ┌─────────────────────────────────────┐
                    │    FACT TABLE                       │
                    │    viewing_sessions                 │
                    │  ┌─────────────────────────────┐   │
                    │  │ - id (PK)                    │   │
                    │  │ - user_id (FK)              │   │
                    │  │ - movie_id (FK)             │   │
                    │  │ - start_time                │   │
                    │  │ - watch_duration_minutes    │   │
                    │  │ - completion_rate           │   │
                    │  │ - device_type               │   │
                    │  │ - quality                   │   │
                    │  │ - buffering_count           │   │
                    │  └─────────────────────────────┘   │
                    └──────────┬──────────────┬───────────┘
                               │              │
              ┌────────────────┴───┐     ┌────┴────────────────┐
              │                    │     │                     │
    ┌─────────▼────────┐  ┌────────▼─────────┐  ┌────────────▼─────────┐
    │ DIMENSION TABLE  │  │ DIMENSION TABLE   │  │ DIMENSION TABLE      │
    │ users            │  │ movies            │  │ ratings              │
    │ ┌──────────────┐ │  │ ┌───────────────┐ │  │ ┌──────────────────┐ │
    │ │- id (PK)     │ │  │ │- id (PK)      │ │  │ │- id (PK)         │ │
    │ │- username    │ │  │ │- title        │ │  │ │- user_id (FK)    │ │
    │ │- email       │ │  │ │- genre        │ │  │ │- movie_id (FK)   │ │
    │ │- country     │ │  │ │- duration     │ │  │ │- rating          │ │
    │ │- subscription│ │  │ │- release_date │ │  │ │- review_text     │ │
    │ │- age         │ │  │ │- director     │ │  │ │- rating_date     │ │
    │ │- gender      │ │  │ │- avg_rating   │ │  │ └──────────────────┘ │
    │ └──────────────┘ │  │ └───────────────┘ │  └──────────────────────┘
    └──────────────────┘  └───────────────────┘

            ┌──────────────────────────────────────┐
            │  AGGREGATE TABLES (Pre-computed)     │
            │  - daily_analytics                   │
            │  - genre_analytics                   │
            │  - hourly_analytics                  │
            └──────────────────────────────────────┘
```

### System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ User Actions │  │ Movie Catalog│  │ Rating System│            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          │                  ▼                  │
          │        ┌──────────────────┐         │
          └───────►│  DATA GENERATOR  │◄────────┘
                   │   (Python/Faker) │
                   └─────────┬────────┘
                             │
                             ▼
          ┌──────────────────────────────────────────┐
          │       ETL/ELT PIPELINE (Python)          │
          │  ┌────────────────────────────────────┐  │
          │  │ 1. Extract - Generate/Load Data    │  │
          │  │ 2. Load - Insert into MongoDB      │  │
          │  │ 3. Transform - Aggregate Analytics │  │
          │  └────────────────────────────────────┘  │
          └─────────────────┬────────────────────────┘
                            │
                            ▼
          ┌──────────────────────────────────────────┐
          │    APACHE SPARK PROCESSING (PySpark)     │
          │  ┌────────────────────────────────────┐  │
          │  │ - Batch Processing                 │  │
          │  │ - Window Functions                 │  │
          │  │ - Complex Aggregations             │  │
          │  │ - Streaming Simulation             │  │
          │  └────────────────────────────────────┘  │
          └─────────────────┬────────────────────────┘
                            │
                            ▼
          ┌──────────────────────────────────────────┐
          │      DATA WAREHOUSE (MongoDB)            │
          │  ┌────────────────────────────────────┐  │
          │  │ - Indexed Collections               │  │
          │  │ - Optimized Queries                │  │
          │  │ - Aggregation Pipelines            │  │
          │  │ - Pre-computed Analytics           │  │
          │  └────────────────────────────────────┘  │
          └─────────────────┬────────────────────────┘
                            │
                            ▼
          ┌──────────────────────────────────────────┐
          │      ANALYTICS API (FastAPI)             │
          │  ┌────────────────────────────────────┐  │
          │  │ - Advanced SQL-like Queries        │  │
          │  │ - RBAC Security                    │  │
          │  │ - Data Masking                     │  │
          │  │ - REST Endpoints                   │  │
          │  └────────────────────────────────────┘  │
          └─────────────────┬────────────────────────┘
                            │
                            ▼
          ┌──────────────────────────────────────────┐
          │   VISUALIZATION DASHBOARD (React)        │
          │  ┌────────────────────────────────────┐  │
          │  │ - Real-time Metrics                │  │
          │  │ - Interactive Charts (Recharts)    │  │
          │  │ - Geographic Analytics             │  │
          │  │ - Trend Analysis                   │  │
          │  └────────────────────────────────────┘  │
          └──────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Backend & Data Engineering
- **Python 3.11** - Core programming language
- **FastAPI** - High-performance REST API framework
- **Apache Spark (PySpark)** - Big data processing (batch + streaming)
- **MongoDB** - Document database (simulating Snowflake patterns)
- **Motor** - Async MongoDB driver
- **Faker** - Realistic data generation

### Frontend
- **React 19** - UI framework
- **Recharts** - Data visualization library
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Modern icon library
- **Axios** - HTTP client

### Data Engineering Concepts Implemented
- ✅ Star/Snowflake Schema Design
- ✅ ETL/ELT Pipelines
- ✅ Batch Processing (Apache Spark)
- ✅ Streaming Analytics (Simulated)
- ✅ Advanced SQL Queries (CTEs, Window Functions via Aggregation)
- ✅ Indexing & Query Optimization
- ✅ Data Partitioning Patterns
- ✅ RBAC (Role-Based Access Control)
- ✅ Data Masking for Security
- ✅ Performance Tuning

## 📈 Features Implemented

### 1. Data Warehouse Design (Star Schema)
- **Fact Table**: `viewing_sessions` - 50,000+ records
- **Dimension Tables**: 
  - `movies` - 200 movies
  - `users` - 5,000 users
  - `ratings` - 20,000 ratings
- **Aggregate Tables**: Pre-computed analytics for performance

### 2. Advanced SQL Queries
- **CTEs (Common Table Expressions)**: Implemented via Spark SQL
- **Window Functions**: Ranking, Row Number in Spark
- **Aggregation Pipelines**: Complex multi-stage aggregations
- **Joins**: Lookup operations across collections

### 3. ETL/ELT Pipeline (`etl_pipeline.py`)
- **Extract**: Generate realistic streaming data
- **Load**: Batch insert into MongoDB (5000 records/batch)
- **Transform**: Create aggregated analytics
- **Indexing**: Automatic index creation for optimization

### 4. Apache Spark Processing (`spark_processor.py`)
- **Batch Processing**: Viewing pattern analysis
- **Window Functions**: Device-based rankings
- **Streaming Simulation**: Real-time quality monitoring
- **Geographic Analysis**: User distribution analytics

### 5. Security & Governance
- **RBAC**: Role-based access (Admin, Analyst, Viewer)
- **Data Masking**: Sensitive field protection
- **Authentication**: HTTP Bearer token support
- **Audit Logging**: Request tracking

### 6. Performance Optimization
- **Indexing Strategy**: 15+ indexes on key fields
- **Query Optimization**: Aggregation pipelines
- **Caching**: Pre-computed daily/genre analytics
- **Batch Operations**: Efficient bulk inserts

### 7. Interactive Dashboard
- **Real-time Metrics**: Users, views, watch time
- **Daily Trends**: Time-series visualization
- **Peak Hours**: Hourly viewing patterns
- **Genre Performance**: Pie chart distribution
- **Device Analytics**: Platform breakdown
- **Geographic Distribution**: Top 10 countries
- **Top Content**: Ranked movie table with ratings

## 📊 Data Statistics

- **Total Movies**: 200
- **Total Users**: 5,000
- **Viewing Sessions**: 50,000+
- **Ratings**: 20,000
- **Date Range**: Last 90 days
- **Daily Analytics**: 91 days
- **Genres**: 10 categories
- **Countries**: 10 regions
- **Devices**: 5 types

## 🚀 API Endpoints

### Dashboard
- `GET /api/dashboard/metrics` - Key performance metrics
- `GET /api/health` - Health check

### Analytics
- `GET /api/analytics/top-movies?limit=10` - Top performing content
- `GET /api/analytics/genres` - Genre performance
- `GET /api/analytics/devices` - Device breakdown
- `GET /api/analytics/geographic` - Geographic distribution
- `GET /api/analytics/hourly-trends` - Peak viewing hours
- `GET /api/analytics/daily-trends?days=30` - Daily trends
- `GET /api/analytics/users` - User analytics with masking

### Admin
- `POST /api/admin/run-etl` - Trigger ETL pipeline (Admin only)

## 🎨 Dashboard Features

### Key Metrics Cards
- Total Users (with active count)
- Total Views (90-day trend)
- Total Watch Time (hours)
- Average Completion Rate

### Visualizations
1. **Area Chart**: Daily viewing trends (30 days)
2. **Bar Chart**: Peak viewing hours (24-hour breakdown)
3. **Pie Chart**: Genre performance distribution
4. **Horizontal Bar**: Device analytics
5. **List View**: Geographic distribution with user counts
6. **Data Table**: Top 10 movies with ratings and completion

### Interactive Features
- Real-time data refresh
- Responsive design
- Smooth animations
- Gradient backgrounds
- Hover effects
- Custom scrollbars

## 🔧 Installation & Setup

### Backend Dependencies
```bash
cd /app/backend
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd /app/frontend
yarn install
```

### Run ETL Pipeline
```bash
cd /app/backend
python etl_pipeline.py
```

### Start Services
```bash
sudo supervisorctl restart all
```

## 📝 Project Files Structure

```
/app/
├── backend/
│   ├── server.py              # FastAPI application with analytics APIs
│   ├── data_generator.py      # Fake data generation
│   ├── etl_pipeline.py        # ETL/ELT pipeline implementation
│   ├── spark_processor.py     # Apache Spark processing
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main dashboard component
│   │   ├── App.css           # Styles
│   │   └── index.js          # Entry point
│   ├── package.json          # Node dependencies
│   └── .env                  # Frontend config
│
└── README.md                 # This file
```

## 🎯 Key Concepts Demonstrated

### 1. Data Warehouse Design
- Star schema with fact and dimension tables
- Denormalized structures for query performance
- Aggregate tables for fast dashboards

### 2. ETL vs ELT
- **ETL**: Transform before loading (data generation)
- **ELT**: Load then transform (analytics aggregation)

### 3. Snowflake Features (Simulated)
- **Clustering**: MongoDB indexes
- **Time Travel**: Document versioning patterns
- **Semi-Structured Data**: JSON/BSON support
- **Performance**: Query optimization

### 4. Apache Spark Capabilities
- Distributed processing (local mode)
- SQL interface with CTEs
- Window functions for rankings
- Batch and streaming patterns

### 5. Advanced SQL Techniques
- Common Table Expressions (CTEs)
- Window Functions (RANK, ROW_NUMBER)
- Complex aggregations ($group, $lookup)
- Subqueries via pipelines

### 6. Security Best Practices
- Role-Based Access Control (RBAC)
- Data masking for sensitive fields
- Authentication middleware
- Audit logging

### 7. Performance Optimization
- Strategic indexing
- Query plan analysis
- Caching strategies
- Batch operations

## 🎓 Learning Outcomes

This project demonstrates:
- End-to-end data pipeline design
- Big data processing with Spark
- Advanced analytics implementation
- Real-time dashboard development
- Security and governance practices
- Performance optimization techniques
- Modern full-stack development

## 📌 Future Enhancements

- Real Snowflake integration
- Apache Airflow for orchestration
- Machine learning predictions
- A/B testing framework
- Real-time streaming with Kafka
- Advanced recommendation engine
- More granular RBAC
- Data quality monitoring

## 👨‍💻 Technical Highlights

### Backend Excellence
- Async/await patterns throughout
- Type hints with Pydantic
- Comprehensive error handling
- Structured logging
- RESTful API design

### Frontend Excellence
- Modern React 19 features
- Responsive design
- Professional UI/UX
- Loading states
- Error handling
- Performance optimized

### Data Engineering Excellence
- Scalable architecture
- Optimized queries
- Proper indexing
- Batch processing
- Data quality patterns

---

## 🏆 Project Completion Status

✅ Data Warehouse (Star/Snowflake Schema) - **COMPLETE**  
✅ Advanced SQL Queries (CTE, Window Functions, Indexing, Partitioning) - **COMPLETE**  
✅ Python-based ETL/ELT Pipelines - **COMPLETE**  
✅ Apache Spark (Batch + Streaming) - **COMPLETE**  
✅ Store and Optimize Data (Clustering, Time Travel, Semi-Structured) - **COMPLETE**  
✅ Security (RBAC, Data Masking, Governance) - **COMPLETE**  
✅ Performance Tuning and Optimization - **COMPLETE**  
✅ Interactive Data Visualization Dashboard - **COMPLETE**  
✅ Architecture Diagram and Documentation - **COMPLETE**  

---

**Built with ❤️ for Project #25 - Movie Streaming Platform Analytics**
