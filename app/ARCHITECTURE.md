# Architecture Diagrams - Movie Streaming Platform Analytics

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                               │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     React Dashboard (Port 3000)                       │  │
│  │                                                                        │  │
│  │  Components:                                                          │  │
│  │  • Metric Cards (Users, Views, Watch Time, Completion)               │  │
│  │  • Area Chart (Daily Trends)                                         │  │
│  │  • Bar Charts (Hourly, Device Analytics)                             │  │
│  │  • Pie Chart (Genre Distribution)                                    │  │
│  │  • Geographic List View                                              │  │
│  │  • Top Movies Table                                                  │  │
│  │                                                                        │  │
│  │  Libraries: Recharts, Lucide Icons, Tailwind CSS                    │  │
│  └────────────────────────────┬───────────────────────────────────────────┘  │
└────────────────────────────────┼──────────────────────────────────────────────┘
                                 │ HTTPS/REST API
                                 │
┌────────────────────────────────▼──────────────────────────────────────────────┐
│                          API / APPLICATION LAYER                              │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                  FastAPI Backend (Port 8001)                          │  │
│  │                                                                        │  │
│  │  API Endpoints:                                                       │  │
│  │  ├─ /api/dashboard/metrics     → Key metrics                         │  │
│  │  ├─ /api/analytics/top-movies  → Top performing content              │  │
│  │  ├─ /api/analytics/genres      → Genre performance                   │  │
│  │  ├─ /api/analytics/devices     → Device breakdown                    │  │
│  │  ├─ /api/analytics/geographic  → Geographic distribution             │  │
│  │  ├─ /api/analytics/hourly-trends → Peak viewing hours                │  │
│  │  └─ /api/analytics/daily-trends → Time series data                   │  │
│  │                                                                        │  │
│  │  Security: RBAC, Data Masking, Bearer Auth                          │  │
│  └────────────────────────────┬───────────────────────────────────────────┘  │
└────────────────────────────────┼──────────────────────────────────────────────┘
                                 │ Async Queries
                                 │
┌────────────────────────────────▼──────────────────────────────────────────────┐
│                       DATA PROCESSING LAYER                                   │
│                                                                               │
│  ┌────────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │   Apache Spark (PySpark)        │  │   ETL/ELT Pipeline               │  │
│  │                                 │  │                                  │  │
│  │  • Batch Processing             │  │  Extract:                        │  │
│  │  • Window Functions             │  │  └─ Data Generation (Faker)      │  │
│  │  • Complex Aggregations         │  │                                  │  │
│  │  • SQL Interface (CTEs)         │  │  Load:                           │  │
│  │  • Streaming Simulation         │  │  └─ Batch Insert (5K/batch)     │  │
│  │                                 │  │                                  │  │
│  │  Use Cases:                     │  │  Transform:                      │  │
│  │  • Viewing patterns             │  │  └─ Aggregate analytics          │  │
│  │  • Device rankings              │  │  └─ Update metrics               │  │
│  │  • Quality monitoring           │  │  └─ Create caches                │  │
│  └────────────────────────────────┘  └──────────────────────────────────┘  │
└────────────────────────────────┬──────────────────────────────────────────────┘
                                 │ Read/Write
                                 │
┌────────────────────────────────▼──────────────────────────────────────────────┐
│                          DATA STORAGE LAYER                                   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                   MongoDB (Port 27017)                                │  │
│  │                                                                        │  │
│  │  Collections (Star Schema):                                           │  │
│  │                                                                        │  │
│  │  FACT TABLE:                        DIMENSION TABLES:                 │  │
│  │  • viewing_sessions (50K)           • movies (200)                    │  │
│  │    - user_id, movie_id              • users (5K)                      │  │
│  │    - watch_duration                 • ratings (20K)                   │  │
│  │    - completion_rate                                                  │  │
│  │    - device_type                    AGGREGATE TABLES:                 │  │
│  │    - timestamps                     • daily_analytics (91)            │  │
│  │                                     • genre_analytics (10)            │  │
│  │                                                                        │  │
│  │  Indexes (15+ for optimization):                                      │  │
│  │  • genre, release_date, country                                       │  │
│  │  • start_time, user_id, movie_id                                      │  │
│  │  • device_type, subscription_type                                     │  │
│  │                                                                        │  │
│  │  Features:                                                            │  │
│  │  • Aggregation Pipelines (CTEs)                                       │  │
│  │  • $lookup (Joins)                                                    │  │
│  │  • $group (Window Functions)                                          │  │
│  │  • Compound Indexes (Partitioning)                                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
```

## 2. Data Flow Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Data      │      │  ETL/ELT     │      │   MongoDB       │
│ Generation  │─────►│  Pipeline    │─────►│   Storage       │
│  (Faker)    │      │  (Python)    │      │ (Star Schema)   │
└─────────────┘      └──────────────┘      └────────┬────────┘
                                                     │
                                                     │ Read
                                                     │
                                            ┌────────▼────────┐
                                            │  Apache Spark   │
                                            │   Processing    │
                                            │  (Batch/Stream) │
                                            └────────┬────────┘
                                                     │
                                                     │ Analyze
                                                     │
                                            ┌────────▼────────┐
                                            │   FastAPI       │
                                            │   Analytics     │
                                            │      API        │
                                            └────────┬────────┘
                                                     │
                                                     │ Serve
                                                     │
                                            ┌────────▼────────┐
                                            │     React       │
                                            │   Dashboard     │
                                            │ (Visualizations)│
                                            └─────────────────┘
```

## 3. Star Schema Design (Data Warehouse)

```
                        FACT TABLE: viewing_sessions
                ┌──────────────────────────────────────────┐
                │  id                    PK                 │
                │  user_id               FK → users         │
                │  movie_id              FK → movies        │
                │  start_time            TIMESTAMP          │
                │  end_time              TIMESTAMP          │
                │  watch_duration_min    INTEGER            │
                │  completion_rate       FLOAT (0-1)        │
                │  device_type           VARCHAR            │
                │  quality               VARCHAR            │
                │  buffering_count       INTEGER            │
                │  user_country          VARCHAR            │
                │  subscription_type     VARCHAR            │
                └────┬─────────────────────────┬────────────┘
                     │                         │
        ┌────────────┴─────────┐   ┌──────────┴────────────┐
        │                      │   │                       │
┌───────▼────────┐  ┌──────────▼───────┐  ┌───────────────▼──────┐
│ DIM: users     │  │  DIM: movies      │  │  DIM: ratings        │
├────────────────┤  ├───────────────────┤  ├──────────────────────┤
│ id          PK │  │  id            PK │  │  id              PK  │
│ username       │  │  title            │  │  user_id         FK  │
│ email          │  │  genre            │  │  movie_id        FK  │
│ age            │  │  duration_min     │  │  rating (1-10)       │
│ gender         │  │  release_date     │  │  review_text         │
│ country        │  │  director         │  │  helpful_count       │
│ subscription   │  │  cast             │  │  rating_date         │
│ signup_date    │  │  avg_rating       │  └──────────────────────┘
│ is_active      │  │  total_views      │
│ preferred_genre│  │  country          │
└────────────────┘  │  language         │
                    └───────────────────┘

         ┌────────────────────────────────────────┐
         │  AGGREGATE TABLES (Performance)        │
         ├────────────────────────────────────────┤
         │  • daily_analytics                     │
         │    - date, total_views, unique_users  │
         │  • genre_analytics                     │
         │    - genre, views, avg_watch_time     │
         │  • hourly_analytics (cached)           │
         └────────────────────────────────────────┘
```

## 4. ETL/ELT Pipeline Flow

```
STEP 1: EXTRACT
┌──────────────────────────────────────┐
│   Data Generation (Faker)            │
│   • Generate 200 movies              │
│   • Generate 5,000 users             │
│   • Generate 50,000 sessions         │
│   • Generate 20,000 ratings          │
└──────────────┬───────────────────────┘
               │
               ▼
STEP 2: LOAD
┌──────────────────────────────────────┐
│   Batch Insert into MongoDB          │
│   • Batch size: 5,000 records        │
│   • Async operations                 │
│   • Error handling                   │
└──────────────┬───────────────────────┘
               │
               ▼
STEP 3: INDEX (Optimization)
┌──────────────────────────────────────┐
│   Create Indexes                     │
│   • Single field indexes             │
│   • Compound indexes                 │
│   • Sort order optimization          │
└──────────────┬───────────────────────┘
               │
               ▼
STEP 4: TRANSFORM (ELT)
┌──────────────────────────────────────┐
│   Aggregate Analytics                │
│   • Update movie view counts         │
│   • Create daily analytics           │
│   • Create genre analytics           │
│   • Calculate completion rates       │
└──────────────────────────────────────┘
```

## 5. Advanced Query Patterns

### Aggregation Pipeline (CTE Equivalent)
```javascript
// Complex aggregation with joins and grouping
[
  // Stage 1: Lookup (JOIN)
  {
    $lookup: {
      from: 'movies',
      localField: 'movie_id',
      foreignField: 'id',
      as: 'movie_info'
    }
  },
  
  // Stage 2: Unwind
  { $unwind: '$movie_info' },
  
  // Stage 3: Group (Aggregation)
  {
    $group: {
      _id: '$movie_info.genre',
      total_views: { $sum: 1 },
      avg_completion: { $avg: '$completion_rate' },
      unique_users: { $addToSet: '$user_id' }
    }
  },
  
  // Stage 4: Project (Select)
  {
    $project: {
      genre: '$_id',
      total_views: 1,
      avg_completion: { $round: ['$avg_completion', 2] },
      unique_users: { $size: '$unique_users' }
    }
  },
  
  // Stage 5: Sort
  { $sort: { total_views: -1 } }
]
```

### Spark SQL (Window Functions)
```sql
-- CTE with Window Functions
WITH hourly_stats AS (
  SELECT 
    hour(start_time) as hour_of_day,
    COUNT(*) as session_count,
    AVG(completion_rate) as avg_completion
  FROM sessions
  GROUP BY hour(start_time)
),
peak_hours AS (
  SELECT 
    hour_of_day,
    session_count,
    RANK() OVER (ORDER BY session_count DESC) as popularity_rank
  FROM hourly_stats
)
SELECT * FROM peak_hours
ORDER BY popularity_rank;
```

## 6. Security Architecture (RBAC)

```
┌──────────────────────────────────────────────────────┐
│                   Authentication Layer                │
│              (HTTP Bearer Token)                      │
└─────────────────────┬────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │  Role Determination     │
         │  • Admin                │
         │  • Analyst              │
         │  • Viewer               │
         └────────────┬────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼────┐      ┌─────▼─────┐    ┌────▼─────┐
│ Admin  │      │  Analyst  │    │  Viewer  │
├────────┤      ├───────────┤    ├──────────┤
│ • Full │      │ • Read    │    │ • Read   │
│ Access │      │ • Write   │    │ • Limited│
│ • ETL  │      │ • Analyze │    │ • Masked │
│ Trigger│      │           │    │ Data     │
└────────┘      └───────────┘    └──────────┘
        │              │               │
        └──────────────┼───────────────┘
                       │
        ┌──────────────▼───────────────┐
        │    Data Masking Layer        │
        │  • Email masking             │
        │  • Sensitive field hiding    │
        │  • PII protection            │
        └──────────────────────────────┘
```

## 7. Performance Optimization Strategy

```
┌────────────────────────────────────────────────────┐
│            Query Optimization                       │
│                                                     │
│  1. Indexing Strategy                              │
│     • Single field indexes (genre, country)        │
│     • Compound indexes (movie_id + start_time)     │
│     • Sort order indexes (timestamp DESC)          │
│                                                     │
│  2. Aggregation Optimization                       │
│     • Pre-computed analytics tables                │
│     • Caching frequently accessed data             │
│     • Batch operations                             │
│                                                     │
│  3. Query Patterns                                 │
│     • Projection to reduce data transfer           │
│     • Limit results                                │
│     • Covered queries (index-only)                 │
│                                                     │
│  4. Data Partitioning (Simulated)                  │
│     • Time-based partitioning (start_time)         │
│     • Compound indexes simulate partitions         │
│                                                     │
│  5. Caching Strategy                               │
│     • Daily analytics cache                        │
│     • Genre analytics cache                        │
│     • Refresh on ETL runs                          │
└────────────────────────────────────────────────────┘
```

## 8. Dashboard Component Architecture

```
┌───────────────────────────────────────────────────────┐
│                    App Component                      │
│                                                       │
│  State Management:                                    │
│  • metrics, topMovies, genreData                     │
│  • deviceData, geoData, hourlyData                   │
│  • dailyTrends, loading                              │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │           Header Component                   │    │
│  │  • Title, Logo, Refresh Button              │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │       Metrics Cards (4 columns)             │    │
│  │  • Total Users  • Total Views              │    │
│  │  • Watch Time   • Completion Rate          │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │       Charts Row 1 (2 columns)              │    │
│  │  • Daily Trends (Area)                      │    │
│  │  • Peak Hours (Bar)                         │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │       Charts Row 2 (3 columns)              │    │
│  │  • Genre (Pie)                              │    │
│  │  • Devices (Bar)                            │    │
│  │  • Geographic (List)                        │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │       Top Movies Table                       │    │
│  │  • Rank, Title, Genre                       │    │
│  │  • Views, Completion, Rating                │    │
│  └─────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────┘
```

---

**All diagrams are part of the Movie Streaming Platform Analytics architecture documentation.**
