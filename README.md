# Movie Recommendation System

A non-ML based movie recommendation system that suggests movies based on user preferences, genre similarity, and collaborative filtering techniques.

## Features
- Personalized movie recommendations based on user ratings
- Smart genre-based recommendations with diversity
- Similar movie suggestions using content similarity
- Fuzzy movie name search with spell correction
- Popular movies ranking system
- Interactive command-line interface

## Project Structure
```
.
├── data/               # Directory for MovieLens dataset
├── src/
│   ├── main.py        # Main application entry point
│   ├── movie_data.py  # Movie data handling and dataset management
│   ├── recommender.py # Core recommendation algorithms
│   └── movie_matcher.py # Fuzzy movie name matching
└── requirements.txt    # Python dependencies
```

## Setup
1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
.\venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the program:
```bash
python src/main.py
```

## How it Works
The system uses several techniques to provide recommendations:

1. **Personalized Recommendations**:
   - Analyzes user's genre preferences from ratings
   - Considers rating patterns and genre diversity
   - Balances between preferences and new discoveries

2. **Genre-Based Recommendations**:
   - Finds movies matching preferred genres
   - Considers both ratings and popularity
   - Ensures quality with minimum rating thresholds

3. **Similar Movies**:
   - Uses genre similarity (Jaccard similarity)
   - Considers user ratings and popularity
   - Provides diverse but relevant suggestions

4. **Movie Search**:
   - Fuzzy string matching for movie titles
   - Handles spelling mistakes and variations
   - Shows similarity scores for matches 