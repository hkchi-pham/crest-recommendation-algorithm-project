"""Diversity metrics.

Input contract: every function takes `recommendations` as a list of genre
lists, one inner list per recommended movie, e.g.

    [["Action", "Adventure"], ["Action", "Romance"], ["Thriller"]]

The recommenders return movieIds, not genres. Use utils.genres_of() to cross
that gap before calling anything here.
"""

from collections import Counter
import math


def genre_diversity(recommendations):
    """Number of distinct genres in the recommendation list."""
    unique_genres = set()
    for genres in recommendations:
        unique_genres.update(genres)

    return len(unique_genres)


def genre_coverage(recommendations, all_genres):
    """Percentage of the dataset's genres that appear in the list.

    all_genres must be passed in from utils.get_all_genres(movies_df). It used
    to be a hardcoded list of 5 names, which reported coverage above 100%
    because MovieLens actually has 20 genres.
    """
    if not all_genres:
        return 0.0

    genres_seen = set()
    for genres in recommendations:
        genres_seen.update(genres)

    return len(genres_seen) / len(all_genres) * 100


def shannon_entropy(recommendations):
    """How evenly the recommendations spread across genres. Higher = broader."""
    entropy = 0
    genre_counter = Counter()
    for genres in recommendations:
        genre_counter.update(genres)

    total = sum(genre_counter.values())

    if total == 0:
        return 0.0

    for count in genre_counter.values():
        p = count / total
        entropy -= p * math.log2(p)

    return entropy


def compute_all(recommendations, all_genres):
    """All three metrics at once, keyed to match visualization.py's columns."""
    return {
        "genre_diversity": genre_diversity(recommendations),
        "genre_coverage": genre_coverage(recommendations, all_genres),
        "shannon_entropy": shannon_entropy(recommendations),
    }


if __name__ == "__main__":
    testlist = [["Action", "Adventure"], ["Action", "Romance"], ["Thriller", "Romance"]]
    demo_genres = ["Action", "Adventure", "Romance", "Sci-Fi", "Thriller"]
    print("Genre diversity: ", genre_diversity(testlist))
    print("Genre coverage: ", genre_coverage(testlist, demo_genres))
    print("Shannon entropy: ", shannon_entropy(testlist))
