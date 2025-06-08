from difflib import SequenceMatcher
from typing import List, Dict, Tuple
import pandas as pd

def get_string_similarity(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

class MovieMatcher:
    def __init__(self, movies_df: pd.DataFrame):
        self.movies_df = movies_df

    def find_similar_titles(self, query: str, threshold: float = 0.6) -> List[Dict]:
        """Find movies with similar titles"""
        similar_movies = []
        for _, movie in self.movies_df.iterrows():
            title = movie['title']
            # Remove year from title for better matching
            title_no_year = title.rsplit('(', 1)[0].strip()
            similarity = get_string_similarity(query, title_no_year)
            if similarity >= threshold:
                similar_movies.append({
                    'movie': movie,
                    'similarity': similarity
                })
        
        # Sort by similarity score
        similar_movies.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_movies

    def get_initial_rating_movies(self, n: int = 10) -> List[Dict]:
        """Get diverse set of popular movies for initial rating"""
        # Get movies with different genres and good number of ratings
        diverse_movies = []
        seen_genres = set()
        
        for _, movie in self.movies_df.iterrows():
            primary_genre = movie['genres'].split('|')[0]
            if primary_genre not in seen_genres and len(diverse_movies) < n:
                diverse_movies.append(movie.to_dict())
                seen_genres.add(primary_genre)
            elif len(diverse_movies) >= n:
                break
        
        return diverse_movies 