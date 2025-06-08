from typing import List, Dict, Tuple, Set
import pandas as pd
from collections import defaultdict
from movie_data import MovieData

class MovieRecommender:
    def __init__(self, movie_data: MovieData):
        self.movie_data = movie_data
        self.MIN_RATINGS_REQUIRED = 5  # Minimum number of ratings needed for personalized recommendations

    def get_user_genre_preferences(self, user_id: int) -> Dict[str, float]:
        """Calculate user's genre preferences based on their ratings"""
        genre_scores = defaultdict(list)
        genre_counts = defaultdict(int)

        # Collect ratings for each genre
        for movie_id, ratings in self.movie_data.ratings.items():
            if user_id in ratings:
                movie = self.movie_data.get_movie_by_id(movie_id)
                if movie is not None:
                    user_rating = ratings[user_id]
                    for genre in movie['genres'].split('|'):
                        genre_scores[genre].append(user_rating)
                        genre_counts[genre] += 1

        # Calculate weighted average rating for each genre
        genre_preferences = {}
        total_ratings = sum(genre_counts.values())
        for genre, scores in genre_scores.items():
            if genre_counts[genre] >= 1:  # Require at least 1 rating per genre
                avg_score = sum(scores) / len(scores)
                # Weight by both the average rating and how many times the user has rated this genre
                weight = genre_counts[genre] / total_ratings
                genre_preferences[genre] = (avg_score * 0.7 + weight * 0.3) * 5  # Scale back to 5-point scale
        
        return genre_preferences

    def get_movie_average_rating(self, movie_id: int) -> Tuple[float, int]:
        """Get movie's average rating and number of ratings"""
        ratings = self.movie_data.get_movie_ratings(movie_id)
        if not ratings:
            return 0.0, 0
        return sum(ratings.values()) / len(ratings), len(ratings)

    def get_genre_diversity_score(self, recommended_movies: List[Dict], new_movie: Dict) -> float:
        """Calculate how much a new movie would add to genre diversity"""
        if not recommended_movies:
            return 1.0

        existing_genres = set()
        for movie in recommended_movies:
            existing_genres.update(movie['genres'].split('|'))
        
        new_genres = set(new_movie['genres'].split('|'))
        unique_new_genres = new_genres - existing_genres
        
        return len(unique_new_genres) / (len(new_genres) + 0.1)  # Add 0.1 to avoid division by zero

    def recommend_by_genre(self, preferred_genre: str, n: int = 5) -> List[Dict]:
        """Recommend movies based on genre preference"""
        genre_movies = self.movie_data.get_movies_by_genre(preferred_genre)
        movies_with_ratings = []
        
        for _, movie in genre_movies.iterrows():
            avg_rating, num_ratings = self.get_movie_average_rating(movie['movieId'])
            if num_ratings >= 5:  # Minimum ratings threshold
                movies_with_ratings.append((movie, avg_rating, num_ratings))
        
        # Sort by rating and number of ratings
        movies_with_ratings.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return [movie.to_dict() for movie, _, _ in movies_with_ratings[:n]]

    def get_personalized_recommendations(self, user_id: int, n: int = 5) -> List[Dict]:
        """Get personalized movie recommendations based on user's ratings"""
        user_ratings = []
        for movie_id, ratings in self.movie_data.ratings.items():
            if user_id in ratings:
                user_ratings.append((movie_id, ratings[user_id]))

        if len(user_ratings) < self.MIN_RATINGS_REQUIRED:
            return []

        # Get user's genre preferences
        genre_preferences = self.get_user_genre_preferences(user_id)
        
        # Get all movies user hasn't rated
        all_movies = self.movie_data.get_all_movies()
        candidate_movies = []
        recommended_movies = []

        for _, movie in all_movies.iterrows():
            movie_dict = movie.to_dict()
            movie_id = movie_dict['movieId']
            
            # Skip if user has already rated this movie
            if movie_id in self.movie_data.ratings and user_id in self.movie_data.ratings[movie_id]:
                continue

            # Calculate genre score
            genre_score = 0
            movie_genres = movie_dict['genres'].split('|')
            matching_genres = 0
            for genre in movie_genres:
                if genre in genre_preferences:
                    genre_score += genre_preferences[genre]
                    matching_genres += 1
            if matching_genres > 0:
                genre_score /= matching_genres

            # Get average rating from other users
            avg_rating, num_ratings = self.get_movie_average_rating(movie_id)
            if num_ratings < 5:  # Skip movies with too few ratings
                continue

            # Calculate diversity score
            diversity_score = self.get_genre_diversity_score(recommended_movies, movie_dict)

            # Combine scores (40% genre preference, 30% average rating, 30% diversity)
            final_score = (
                (genre_score / 5.0) * 0.4 +  # Normalize to 0-1 range
                (avg_rating / 5.0) * 0.3 +   # Normalize to 0-1 range
                diversity_score * 0.3         # Already in 0-1 range
            )

            candidate_movies.append((movie_dict, final_score, diversity_score))

        # Sort by final score
        candidate_movies.sort(key=lambda x: x[1], reverse=True)
        
        # Select top N movies while maintaining genre diversity
        recommended_movies = []
        for movie, score, diversity in candidate_movies:
            if len(recommended_movies) >= n:
                break
                
            # Add movie if it's one of the first picks or adds sufficient genre diversity
            if len(recommended_movies) < 2 or diversity > 0.2:
                recommended_movies.append(movie)

        return recommended_movies

    def recommend_similar_movies(self, movie_id: int, n: int = 5) -> List[Dict]:
        """Recommend similar movies based on genre similarity and ratings"""
        target_movie = self.movie_data.get_movie_by_id(movie_id)
        if target_movie is None:
            return []

        all_movies = self.movie_data.get_all_movies()
        similarities = []
        target_genres = set(target_movie['genres'].split('|'))

        for _, movie in all_movies.iterrows():
            if movie['movieId'] != movie_id:
                movie_dict = movie.to_dict()
                movie_genres = set(movie_dict['genres'].split('|'))
                
                # Calculate genre similarity using Jaccard similarity
                intersection = len(target_genres & movie_genres)
                union = len(target_genres | movie_genres)
                genre_similarity = intersection / union if union > 0 else 0

                # Get average rating and rating count
                avg_rating, num_ratings = self.get_movie_average_rating(movie_dict['movieId'])
                
                if num_ratings >= 5:  # Only consider movies with sufficient ratings
                    # Combine similarity with rating for better recommendations
                    # 60% genre similarity, 40% rating
                    score = (genre_similarity * 0.6) + ((avg_rating / 5.0) * 0.4)
                    similarities.append((movie_dict, score))

        # Sort by combined score
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, _ in similarities[:n]]

    def get_popular_movies(self, n: int = 5) -> List[Dict]:
        """Get popular movies based on user ratings"""
        movie_scores = []
        
        for movie_id in self.movie_data.ratings:
            avg_rating, num_ratings = self.get_movie_average_rating(movie_id)
            if num_ratings >= 20:  # Require more ratings for popular movies
                # Calculate popularity score combining rating and number of ratings
                popularity_score = (avg_rating * 0.7) + (min(num_ratings / 100, 1.0) * 0.3)
                movie = self.movie_data.get_movie_by_id(movie_id)
                if movie is not None:
                    movie_scores.append((movie.to_dict(), popularity_score))

        # Sort by popularity score
        movie_scores.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, _ in movie_scores[:n]] 