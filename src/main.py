from movie_data import MovieData
from recommender import MovieRecommender
from movie_matcher import MovieMatcher
from typing import Dict, Optional

def print_movie_list(movies, header: str):
    """Helper function to print a list of movies"""
    print(f"\n=== {header} ===")
    for movie in movies:
        print(f"\nID: {movie['movieId']}")
        print(f"Title: {movie['title']}")
        print(f"Genres: {movie['genres']}")
        print("-" * 50)

def get_available_genres(movie_data: MovieData) -> set:
    """Get all unique genres from the dataset"""
    all_genres = set()
    for genres in movie_data.get_all_movies()['genres']:
        all_genres.update([g.strip() for g in genres.split('|')])
    return all_genres

def collect_initial_ratings(movie_matcher: MovieMatcher, movie_data: MovieData, user_id: int) -> int:
    """Collect initial ratings from the user"""
    print("\nTo provide better recommendations, please rate some movies (0-5):")
    print("You can skip rating a movie by pressing Enter")
    
    initial_movies = movie_matcher.get_initial_rating_movies()
    ratings_count = 0
    
    for movie in initial_movies:
        print(f"\nMovie: {movie['title']}")
        print(f"Genres: {movie['genres']}")
        
        while True:
            rating = input("Your rating (0-5) or press Enter to skip: ").strip()
            if rating == "":
                break
            try:
                rating_float = float(rating)
                if 0 <= rating_float <= 5:
                    movie_data.add_rating(user_id, movie['movieId'], rating_float)
                    ratings_count += 1
                    break
                else:
                    print("Rating must be between 0 and 5!")
            except ValueError:
                print("Please enter a valid number!")
    
    return ratings_count

def search_movie(movie_matcher: MovieMatcher) -> Optional[Dict]:
    """Search for a movie using fuzzy matching"""
    while True:
        query = input("\nEnter movie name (or part of it): ").strip()
        if not query:
            return None
        
        similar_movies = movie_matcher.find_similar_titles(query)
        if not similar_movies:
            print("No movies found! Try a different search term.")
            continue
        
        print("\nFound these movies:")
        for i, result in enumerate(similar_movies, 1):
            movie = result['movie'].to_dict()  # Convert Series to dict
            print(f"{i}. {movie['title']} ({result['similarity']:.2f} match)")
            if i >= 5:  # Show top 5 matches
                break
        
        if len(similar_movies) == 1:
            return similar_movies[0]['movie'].to_dict()  # Convert Series to dict
        
        choice = input("\nSelect a movie number (or press Enter to search again): ").strip()
        if choice == "":
            continue
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(similar_movies):
                return similar_movies[choice_num - 1]['movie'].to_dict()  # Convert Series to dict
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!")

def main():
    # Initialize movie data and recommender
    print("\nInitializing Movie Recommendation System...")
    movie_data = MovieData()
    recommender = MovieRecommender(movie_data)
    movie_matcher = MovieMatcher(movie_data.get_all_movies())

    # Use a simple user ID for demonstration
    user_id = 1

    # Collect initial ratings
    ratings_count = collect_initial_ratings(movie_matcher, movie_data, user_id)
    print(f"\nThanks! You rated {ratings_count} movies.")

    while True:
        print("\n=== Movie Recommendation System ===")
        print("1. Get personalized recommendations")
        print("2. Search and rate a movie")
        print("3. Get recommendations by genre")
        print("4. Find similar movies")
        print("5. View popular movies")
        print("6. View all movies")
        print("7. Exit")

        choice = input("\nEnter your choice (1-7): ")

        if choice == "1":
            if ratings_count < recommender.MIN_RATINGS_REQUIRED:
                print(f"\nPlease rate at least {recommender.MIN_RATINGS_REQUIRED} movies to get personalized recommendations!")
                print(f"You have rated {ratings_count} movies so far.")
            else:
                recommendations = recommender.get_personalized_recommendations(user_id)
                print_movie_list(recommendations, "Personalized Recommendations")

        elif choice == "2":
            movie = search_movie(movie_matcher)
            if movie:
                try:
                    rating = float(input(f"\nRate '{movie['title']}' (0-5): "))
                    if 0 <= rating <= 5:
                        movie_data.add_rating(user_id, movie['movieId'], rating)
                        ratings_count += 1
                        print("\nRating added successfully!")
                    else:
                        print("\nRating must be between 0 and 5!")
                except ValueError:
                    print("\nPlease enter a valid number!")

        elif choice == "3":
            genres = sorted(get_available_genres(movie_data))
            print("\nAvailable genres:")
            for i, genre in enumerate(genres, 1):
                print(f"{i}. {genre}")
            genre = input("\nEnter preferred genre: ")
            recommendations = recommender.recommend_by_genre(genre)
            if recommendations:
                print_movie_list(recommendations, f"Top Recommendations for genre: {genre}")
            else:
                print(f"\nNo movies found for genre: {genre}")

        elif choice == "4":
            movie = search_movie(movie_matcher)
            if movie:
                similar_movies = recommender.recommend_similar_movies(movie['movieId'])
                if similar_movies:
                    print(f"\nFinding movies similar to: {movie['title']}")
                    print_movie_list(similar_movies, "Similar Movies")

        elif choice == "5":
            popular_movies = recommender.get_popular_movies()
            print_movie_list(popular_movies, "Popular Movies")

        elif choice == "6":
            movies = movie_data.get_all_movies().to_dict('records')
            print_movie_list(movies[:20], "Sample of All Movies (First 20)")
            print(f"\nTotal number of movies: {len(movies)}")

        elif choice == "7":
            print("\nThank you for using the Movie Recommendation System!")
            break

        else:
            print("\nInvalid choice! Please try again.")

if __name__ == "__main__":
    main() 