import pandas as pd
import os
from typing import List, Dict, Optional
import requests
import zipfile
import io
import shutil

class MovieData:
    def __init__(self):
        self.movies_df = None
        self.ratings = {}  # User ratings dictionary: {movie_id: {user_id: rating}}
        self._load_movielens_data()

    def _load_movielens_data(self):
        """Load MovieLens small dataset"""
        # Create data directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')

        # Download MovieLens small dataset if not already present
        if not (os.path.exists('data/movies.csv') and os.path.exists('data/ratings.csv')):
            print("Downloading MovieLens dataset...")
            try:
                url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
                response = requests.get(url, timeout=30)
                response.raise_for_status()  # Raise an error for bad status codes
                
                # Create a temporary directory for extraction
                temp_dir = 'data/temp'
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)

                # Extract to temp directory
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Move needed files to data directory
                dataset_dir = os.path.join(temp_dir, 'ml-latest-small')
                for file in ['movies.csv', 'ratings.csv']:
                    src = os.path.join(dataset_dir, file)
                    dst = os.path.join('data', file)
                    if os.path.exists(src):
                        shutil.move(src, dst)

                # Clean up temp directory
                shutil.rmtree(temp_dir)
                print("Dataset downloaded successfully!")
            except Exception as e:
                print(f"Error downloading dataset: {e}")
                print("Falling back to sample data...")
                self._load_sample_data()
                return

        # Load movies and ratings
        try:
            self.movies_df = pd.read_csv('data/movies.csv')
            ratings_df = pd.read_csv('data/ratings.csv')
            
            # Convert ratings to our internal format
            for _, row in ratings_df.iterrows():
                movie_id = int(row['movieId'])  # Ensure movie_id is int
                user_id = int(row['userId'])    # Ensure user_id is int
                rating = float(row['rating'])    # Ensure rating is float
                if movie_id not in self.ratings:
                    self.ratings[movie_id] = {}
                self.ratings[movie_id][user_id] = rating

            print(f"Loaded {len(self.movies_df)} movies and {len(ratings_df)} ratings!")
        except Exception as e:
            print(f"Error loading dataset: {e}")
            print("Falling back to sample data...")
            self._load_sample_data()

    def _load_sample_data(self):
        """Initialize with sample movie data (fallback if online data fails)"""
        data = {
            'movieId': range(1, 11),
            'title': [
                'The Shawshank Redemption (1994)', 'The Godfather (1972)', 
                'The Dark Knight (2008)', 'Pulp Fiction (1994)',
                'Fight Club (1999)', 'Inception (2010)',
                'The Matrix (1999)', 'Goodfellas (1990)',
                'The Silence of the Lambs (1991)', 'Interstellar (2014)'
            ],
            'genres': [
                'Drama', 'Crime|Drama', 
                'Action|Crime|Drama', 'Crime|Drama',
                'Drama|Thriller', 'Action|Sci-Fi|Thriller',
                'Action|Sci-Fi', 'Biography|Crime|Drama',
                'Crime|Drama|Thriller', 'Adventure|Drama|Sci-Fi'
            ]
        }
        self.movies_df = pd.DataFrame(data)

    def get_all_movies(self) -> pd.DataFrame:
        """Return all movies"""
        return self.movies_df

    def get_movie_by_id(self, movie_id: int) -> Optional[pd.Series]:
        """Get movie details by ID"""
        movie = self.movies_df[self.movies_df['movieId'] == movie_id]
        return movie.iloc[0] if not movie.empty else None

    def get_movies_by_genre(self, genre: str) -> pd.DataFrame:
        """Get all movies that contain the specified genre"""
        return self.movies_df[self.movies_df['genres'].str.contains(genre, case=False, na=False)]

    def add_rating(self, user_id: int, movie_id: int, rating: float) -> None:
        """Add a user rating for a movie"""
        if movie_id not in self.ratings:
            self.ratings[movie_id] = {}
        self.ratings[movie_id][user_id] = rating

    def get_movie_ratings(self, movie_id: int) -> Dict[int, float]:
        """Get all ratings for a specific movie"""
        return self.ratings.get(movie_id, {}) 