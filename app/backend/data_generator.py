"""Data Generator for Movie Streaming Platform Analytics"""
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid

fake = Faker()

# Movie data
MOVIE_GENRES = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Romance', 'Thriller', 'Documentary', 'Animation', 'Fantasy']
MOVIE_RATINGS = ['G', 'PG', 'PG-13', 'R', 'NC-17']
COUNTRIES = ['USA', 'UK', 'India', 'Canada', 'Australia', 'Germany', 'France', 'Japan', 'Brazil', 'Mexico']
DEVICE_TYPES = ['Mobile', 'Desktop', 'Tablet', 'Smart TV', 'Gaming Console']

class StreamingDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.movies = []
        self.users = []
        
    def generate_movies(self, count=200):
        """Generate movie catalog data"""
        movies = []
        for i in range(count):
            release_date = self.fake.date_between(start_date='-10y', end_date='today')
            movie = {
                'id': str(uuid.uuid4()),
                'title': f"{self.fake.catch_phrase()} {random.choice(['Movie', 'Story', 'Adventure', 'Chronicles', 'Legacy'])}",
                'genre': random.choice(MOVIE_GENRES),
                'sub_genres': random.sample(MOVIE_GENRES, k=random.randint(1, 3)),
                'duration_minutes': random.randint(80, 180),
                'release_date': release_date.isoformat(),
                'rating': random.choice(MOVIE_RATINGS),
                'director': self.fake.name(),
                'cast': [self.fake.name() for _ in range(random.randint(3, 8))],
                'production_budget': random.randint(1000000, 200000000),
                'description': self.fake.text(max_nb_chars=200),
                'language': random.choice(['English', 'Spanish', 'French', 'Hindi', 'Japanese']),
                'country': random.choice(COUNTRIES),
                'avg_rating': round(random.uniform(3.0, 9.5), 1),
                'total_views': 0,
                'created_at': datetime.utcnow().isoformat()
            }
            movies.append(movie)
        self.movies = movies
        return movies
    
    def generate_users(self, count=5000):
        """Generate user demographics data"""
        users = []
        for i in range(count):
            signup_date = self.fake.date_between(start_date='-3y', end_date='today')
            user = {
                'id': str(uuid.uuid4()),
                'username': self.fake.user_name(),
                'email': self.fake.email(),
                'age': random.randint(18, 65),
                'gender': random.choice(['Male', 'Female', 'Other']),
                'country': random.choice(COUNTRIES),
                'subscription_type': random.choice(['Free', 'Basic', 'Premium', 'Family']),
                'signup_date': signup_date.isoformat(),
                'is_active': random.choice([True, True, True, False]),
                'preferred_genres': random.sample(MOVIE_GENRES, k=random.randint(2, 4)),
                'created_at': datetime.utcnow().isoformat()
            }
            users.append(user)
        self.users = users
        return users
    
    def generate_viewing_sessions(self, count=50000):
        """Generate viewing session data (fact table)"""
        if not self.movies or not self.users:
            raise ValueError("Generate movies and users first")
        
        sessions = []
        for i in range(count):
            movie = random.choice(self.movies)
            user = random.choice(self.users)
            start_time = self.fake.date_time_between(start_date='-90d', end_date='now')
            
            # Calculate watch duration (some users don't finish)
            completion_rate = random.uniform(0.1, 1.0)
            watch_duration = int(movie['duration_minutes'] * completion_rate)
            
            session = {
                'id': str(uuid.uuid4()),
                'user_id': user['id'],
                'movie_id': movie['id'],
                'start_time': start_time.isoformat(),
                'end_time': (start_time + timedelta(minutes=watch_duration)).isoformat(),
                'watch_duration_minutes': watch_duration,
                'completion_rate': round(completion_rate, 2),
                'device_type': random.choice(DEVICE_TYPES),
                'quality': random.choice(['SD', 'HD', 'FHD', '4K']),
                'buffering_count': random.randint(0, 5) if random.random() < 0.3 else 0,
                'user_country': user['country'],
                'subscription_type': user['subscription_type'],
                'created_at': datetime.utcnow().isoformat()
            }
            sessions.append(session)
        
        return sessions
    
    def generate_ratings(self, count=20000):
        """Generate user ratings and reviews"""
        if not self.movies or not self.users:
            raise ValueError("Generate movies and users first")
        
        ratings = []
        used_combinations = set()
        
        for i in range(count):
            # Ensure unique user-movie combinations
            while True:
                user = random.choice(self.users)
                movie = random.choice(self.movies)
                combo = f"{user['id']}_{movie['id']}"
                if combo not in used_combinations:
                    used_combinations.add(combo)
                    break
            
            rating_date = self.fake.date_time_between(start_date='-2y', end_date='now')
            rating = {
                'id': str(uuid.uuid4()),
                'user_id': user['id'],
                'movie_id': movie['id'],
                'rating': random.randint(1, 10),
                'review_text': self.fake.text(max_nb_chars=300) if random.random() < 0.4 else None,
                'helpful_count': random.randint(0, 500),
                'rating_date': rating_date.isoformat(),
                'created_at': datetime.utcnow().isoformat()
            }
            ratings.append(rating)
        
        return ratings


if __name__ == "__main__":
    generator = StreamingDataGenerator()
    
    print("Generating movies...")
    movies = generator.generate_movies(200)
    print(f"Generated {len(movies)} movies")
    
    print("Generating users...")
    users = generator.generate_users(5000)
    print(f"Generated {len(users)} users")
    
    print("Generating viewing sessions...")
    sessions = generator.generate_viewing_sessions(50000)
    print(f"Generated {len(sessions)} viewing sessions")
    
    print("Generating ratings...")
    ratings = generator.generate_ratings(20000)
    print(f"Generated {len(ratings)} ratings")
