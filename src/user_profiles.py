"""User genre preference profiles.

Implements docs/methodology.md, "User Preference Profiles":

    1. Merge movie genres with user ratings.
    2. Compute the average rating for every genre.
    3. Normalize preference scores to the range [0, 1].

Profiles are FIXED for the whole experiment. Only interaction history changes
during the simulation. This is what isolates the effect of the recommendation
algorithm from changes in user taste.

Output contract
---------------
user_profiles   dict[int, list[float]]   userId  -> genre vector, values [0,1]
movie_profiles  dict[int, list[float]]   movieId -> genre vector, values {0,1}

Both vectors are indexed by the SAME genre ordering, produced by
utils.get_all_genres(movies_df). content_based.recommend() takes the cosine
similarity between one of each, so if the two orderings ever diverged the
similarity scores would be silently meaningless.
"""

import random

from utils import RANDOM_SEED, NUM_USERS


def build_genre_index(all_genres):
    """genre name -> its position in every profile vector."""
    return {genre: i for i, genre in enumerate(all_genres)}


def build_movie_profiles(movies_df, all_genres):
    """movieId -> binary genre vector.

    A movie is represented purely by which genres it belongs to, per the
    methodology ("Each movie is represented by its genres").
    """
    genre_index = build_genre_index(all_genres)
    movie_profiles = {}

    for movie_id, genres in zip(movies_df["movieId"], movies_df["genres"]):
        vector = [0.0] * len(all_genres)
        for genre in genres:
            if genre in genre_index:
                vector[genre_index[genre]] = 1.0
        movie_profiles[movie_id] = vector

    return movie_profiles


def build_user_profiles(movies_df, ratings_df, all_genres, normalize="minmax"):
    """userId -> genre preference vector in [0, 1].

    Each rating a user gave contributes to every genre of the movie rated, so
    a 5.0 on a Comedy|Romance film raises both averages. Genres the user has
    never rated score 0.0.

    normalize:
      "minmax"  per-user min-max across that user's own genre averages.
                Default. Spreads each user's preferences across the full [0,1]
                range, which is what makes the cosine similarity in
                content_based discriminate between genres.
      "scale"   average rating / 5.0. Keeps absolute rating level and stays
                comparable between users, but compresses everything into
                roughly [0.6, 1.0] because MovieLens averages cluster at 3-4.
    """
    genre_index = build_genre_index(all_genres)
    movie_genres = dict(zip(movies_df["movieId"], movies_df["genres"]))

    # userId -> per-genre [running total, count]
    totals = {}

    for user_id, movie_id, rating in zip(
        ratings_df["userId"], ratings_df["movieId"], ratings_df["rating"]
    ):
        genres = movie_genres.get(movie_id)
        if not genres:
            # Movie was dropped at load time (no genres listed). Skip it
            # rather than let it pull averages toward nothing.
            continue

        if user_id not in totals:
            totals[user_id] = [[0.0, 0] for _ in all_genres]

        user_totals = totals[user_id]
        for genre in genres:
            i = genre_index.get(genre)
            if i is not None:
                user_totals[i][0] += rating
                user_totals[i][1] += 1

    user_profiles = {}

    for user_id, user_totals in totals.items():
        averages = [
            (total / count) if count else 0.0 for total, count in user_totals
        ]
        rated = [avg for avg, (_, count) in zip(averages, user_totals) if count]

        if normalize == "scale":
            vector = [avg / 5.0 for avg in averages]

        elif normalize == "minmax":
            if not rated:
                vector = [0.0] * len(all_genres)
            else:
                low = min(rated)
                high = max(rated)
                span = high - low

                if span == 0:
                    # User rated everything identically: no genre preference
                    # signal. Flat 0.5 rather than all-zero, which would make
                    # the cosine similarity undefined.
                    vector = [0.5 if count else 0.0
                              for _, count in user_totals]
                else:
                    vector = [
                        ((avg - low) / span) if count else 0.0
                        for avg, (_, count) in zip(averages, user_totals)
                    ]
        else:
            raise ValueError(f"unknown normalize mode: {normalize!r}")

        user_profiles[user_id] = vector

    return user_profiles


def sample_users(user_profiles, n=NUM_USERS, seed=RANDOM_SEED):
    """The fixed experimental sample: n users, drawn reproducibly.

    Sorted before sampling so the result depends only on the seed, never on
    dict insertion order.
    """
    candidates = sorted(user_profiles)

    if n >= len(candidates):
        return candidates

    return random.Random(seed).sample(candidates, n)


def genre_affinity(user_vector, genres, genre_index):
    """How well a movie matches a user's taste, in [0, 1].

    The methodology's click model: "Calculate its affinity based on the user's
    preferences for the movie's genres." Taken as the mean preference across
    the movie's genres, so a film matching one loved genre and one disliked
    genre lands in the middle.
    """
    scores = [
        user_vector[genre_index[genre]]
        for genre in genres
        if genre in genre_index
    ]

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


if __name__ == "__main__":
    import data_loader
    import utils

    movies_df, ratings_df = data_loader.load_data(save_processed=False)
    all_genres = utils.get_all_genres(movies_df)

    profiles = build_user_profiles(movies_df, ratings_df, all_genres)
    movie_profiles = build_movie_profiles(movies_df, all_genres)
    sample = sample_users(profiles)

    print(f"genres        : {len(all_genres)}")
    print(f"user profiles : {len(profiles)}")
    print(f"movie profiles: {len(movie_profiles)}")
    print(f"sampled users : {len(sample)} (seed {utils.RANDOM_SEED})")
    print(f"first 10      : {sample[:10]}")

    example = sample[0]
    ranked = sorted(
        zip(all_genres, profiles[example]), key=lambda pair: -pair[1]
    )
    print(f"\nuser {example} top 5 genres:")
    for genre, score in ranked[:5]:
        print(f"  {genre:<12} {score:.2f}")
    print(f"user {example} bottom 3 rated genres:")
    for genre, score in [p for p in ranked if p[1] > 0][-3:]:
        print(f"  {genre:<12} {score:.2f}")
