"""Shared integration layer.

Every module in this project speaks one of a small number of agreed data
shapes. They are defined and built here so that no module has to guess what
another module hands it.

Canonical shapes
----------------
movies_df            DataFrame: movieId, title, genres (genres is a list[str])
ratings_df           DataFrame: userId, movieId, rating, timestamp
movie_genres         dict[int, list[str]]          movieId -> its genres
all_genres           list[str]                     the 20 genres in the dataset
ratings_records      list[dict]                    ratings_df.to_dict("records")
user_ratings         dict[int, dict[int, float]]   userId -> {movieId: rating}
recommender          Callable[[int, int], list[int]]   (user_id, n) -> movieIds

Column names follow MovieLens exactly (userId, movieId, rating). Nothing in
this project renames them.
"""

import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
RESULTS_CSV_DIR = os.path.join(PROJECT_ROOT, "results", "csv")
RESULTS_FIGURES_DIR = os.path.join(PROJECT_ROOT, "results", "figures")

# Controlled variables (docs/methodology.md). Import these; do not retype them.
RANDOM_SEED = 42
NUM_USERS = 100
NUM_ROUNDS = 30
TOP_N = 10

ALGORITHMS = ["popularity", "content_based", "collaborative"]

# Rating assigned to a clicked movie when it enters the user's history as
# implicit positive feedback. 4.0 = "liked", below the 5.0 ceiling so a click
# is not treated as stronger evidence than an actual top rating.
IMPLICIT_CLICK_RATING = 4.0

# Neighbours consulted by collaborative filtering. Sets the candidate pool
# size, since only movies rated by these k users can be recommended. 20 is the
# smallest value at which no user's pool runs dry over 30 rounds; the original
# value of 5 left 31 of 100 users short. See collaborative.recommend().
K_NEIGHBOURS = 20


# --------------------------------------------------------------------------
# Shape builders: DataFrame -> the plain-Python shapes the algorithms want
# --------------------------------------------------------------------------

def get_all_genres(movies_df):
    """Every genre present in the dataset, sorted. 20 for MovieLens small."""
    genres = set()
    for genre_list in movies_df["genres"]:
        genres.update(genre_list)
    return sorted(genres)


def build_movie_genres(movies_df):
    """movieId -> list of genre names."""
    return dict(zip(movies_df["movieId"], movies_df["genres"]))


def build_ratings_records(ratings_df):
    """ratings_df as a list of dicts, keyed userId / movieId / rating."""
    return ratings_df.to_dict("records")


def build_user_ratings(ratings_df):
    """userId -> {movieId: rating}."""
    user_ratings = {}
    for user_id, movie_id, rating in zip(
        ratings_df["userId"], ratings_df["movieId"], ratings_df["rating"]
    ):
        user_ratings.setdefault(user_id, {})[movie_id] = rating
    return user_ratings


def build_seen_movies(user_ratings):
    """userId -> set of movieIds that user has already rated."""
    return {user_id: set(ratings) for user_id, ratings in user_ratings.items()}


def genres_of(movie_ids, movie_genres):
    """Bridge: a recommendation list (movieIds) -> what the metrics want.

    diversity_metrics operates on a list of genre lists, but the recommenders
    return a list of movieIds. Every caller must cross this bridge.
    """
    return [movie_genres.get(movie_id, []) for movie_id in movie_ids]


# --------------------------------------------------------------------------
# Recommender adapters
#
# The three algorithm modules each need different inputs, so they cannot be
# swapped for one another directly. Each factory below pre-binds the dataset
# and returns the uniform recommender callable (user_id, n) -> list[movieId],
# which is the only shape Simulation ever sees.
# --------------------------------------------------------------------------

def make_popularity_recommender(ratings_records, seen_movies=None):
    """Unpersonalised popularity. Ranking is global, so it is built once.

    seen_movies is read on every call, not copied, so the feedback loop can
    grow it between rounds and the next call sees the update.
    """
    import popularity

    ranking = popularity.build_popularity_ranking(ratings_records)
    seen_movies = {} if seen_movies is None else seen_movies

    def recommender(user_id, n=TOP_N):
        return popularity.recommend_from_ranking(
            ranking, seen_movies.get(user_id, set()), n=n
        )

    return recommender


def make_content_based_recommender(user_profiles, movie_profiles, seen_movies=None):
    import content_based

    seen_movies = {} if seen_movies is None else seen_movies

    def recommender(user_id, n=TOP_N):
        return content_based.recommend(
            user_id,
            user_profiles,
            movie_profiles,
            n=n,
            excludeMovieIds=seen_movies.get(user_id),
        )

    return recommender


def make_collaborative_recommender(user_ratings, all_movie_ids=None,
                                   k_neighbours=5, seen_movies=None):
    """User-user CF over sparse rating dicts.

    user_ratings is held by reference: when the feedback loop adds a clicked
    movie to a user's ratings, the next call recomputes neighbours against the
    updated history. That is the collaborative echo chamber mechanism.

    k_neighbours defaults to 5 (the original implementation's value), but the
    experiment runs at 20. Only movies rated by the k nearest neighbours can be
    recommended, so k sets the candidate pool size. At k=5 that pool ran dry
    mid-experiment for 20 of 100 users and the empty lists were being scored as
    zero diversity — a false narrowing signal. See collaborative.recommend()
    for the full justification and the measured sweep.
    """
    import collaborative

    seen_movies = {} if seen_movies is None else seen_movies

    def recommender(user_id, n=TOP_N):
        return collaborative.recommend(
            user_id,
            user_ratings,
            all_movie_ids,
            n=n,
            kNeighbours=k_neighbours,
            excludeMovieIds=seen_movies.get(user_id),
        )

    return recommender


def ensure_output_dirs():
    os.makedirs(RESULTS_CSV_DIR, exist_ok=True)
    os.makedirs(RESULTS_FIGURES_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
