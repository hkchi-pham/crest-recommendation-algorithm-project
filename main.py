"""Experiment runner.

Runs the full experiment described in docs/methodology.md: three recommendation
algorithms, the same 100 sampled users, 30 rounds each, identical click model
and seed. Writes three CSVs to results/csv/ and the figures to results/figures/.

Usage
-----
    python main.py                        full run (100 users x 30 rounds)
    python main.py --users 10 --rounds 5  quick check
    python main.py --click-scale 0.5      lower click-through rate
    python main.py --k-neighbours 5       sensitivity check (will exhaust pools)
    python main.py --no-figures           skip plotting (no matplotlib needed)

Outputs
-------
    results/csv/recommendations.csv    every recommendation made
    results/csv/interactions.csv       every recommendation + whether clicked
    results/csv/diversity_metrics.csv  the three metrics, per user per round
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import pandas as pd

import data_loader
import diversity_metrics
import user_profiles as up
import utils
from simulation import Simulation, make_affinity_click_model


def build_feedback(seen_movies, user_ratings, implicit_rating,
                   feed_clicks_to_ratings):
    """Return the per-round callback that closes the feedback loop.

    Two effects, both applied after every round:

      1. Every movie SHOWN is added to the user's seen set, so it is not
         recommended again. Without this each round returns an identical list
         and every metric is flat across all 30 rounds.

      2. Every movie CLICKED is added to the user's rating history as implicit
         positive feedback. This only changes behaviour for collaborative
         filtering, where it shifts which neighbours the user is matched to —
         the mechanism by which collaborative filtering can narrow over time.

    Preference profiles are never touched, per the methodology.
    """
    def on_round(user_id, recommendations, clicks):
        seen_movies.setdefault(user_id, set()).update(recommendations)

        if feed_clicks_to_ratings:
            history = user_ratings.setdefault(user_id, {})
            for movie_id in clicks:
                history.setdefault(movie_id, implicit_rating)

    return on_round


def run_experiment(num_users, num_rounds, top_n, click_scale,
                   feed_clicks_to_ratings, normalize, k_neighbours):
    print("Loading data...")
    movies_df, ratings_df = data_loader.load_data()

    all_genres = utils.get_all_genres(movies_df)
    movie_genres = utils.build_movie_genres(movies_df)
    genre_index = up.build_genre_index(all_genres)
    ratings_records = utils.build_ratings_records(ratings_df)

    print("Building profiles...")
    profiles = up.build_user_profiles(
        movies_df, ratings_df, all_genres, normalize=normalize
    )
    movie_profiles = up.build_movie_profiles(movies_df, all_genres)
    users = up.sample_users(profiles, n=num_users, seed=utils.RANDOM_SEED)

    print(f"  {len(movie_genres)} movies, {len(all_genres)} genres, "
          f"{len(users)} users, {num_rounds} rounds, N={top_n}")

    click_model = make_affinity_click_model(
        profiles, movie_genres, genre_index, scale=click_scale
    )

    recommendation_rows = []
    interaction_rows = []
    metric_rows = []

    for algorithm in utils.ALGORITHMS:
        started = time.time()

        # Rebuilt per algorithm so each arm starts from the same clean state:
        # no seen history, and the original ratings. Sharing them would let one
        # arm's feedback contaminate the next.
        seen_movies = {}
        user_ratings = utils.build_user_ratings(ratings_df)

        if algorithm == "popularity":
            recommender = utils.make_popularity_recommender(
                ratings_records, seen_movies
            )
        elif algorithm == "content_based":
            recommender = utils.make_content_based_recommender(
                profiles, movie_profiles, seen_movies
            )
        elif algorithm == "collaborative":
            recommender = utils.make_collaborative_recommender(
                {u: user_ratings[u] for u in users},
                k_neighbours=k_neighbours,
                seen_movies=seen_movies
            )
        else:
            raise ValueError(f"unknown algorithm: {algorithm}")

        feedback = build_feedback(
            seen_movies, user_ratings,
            implicit_rating=utils.IMPLICIT_CLICK_RATING,
            feed_clicks_to_ratings=feed_clicks_to_ratings,
        )

        for position, user_id in enumerate(users, start=1):
            simulation = Simulation(
                recommender,
                user_id,
                n=top_n,
                click_model=click_model,
                # Seed per (algorithm, user) so click draws are reproducible
                # and independent, but identical across arms for a given user.
                seed=utils.RANDOM_SEED + user_id,
                on_round=feedback,
            )
            simulation.run(num_rounds)

            for row in simulation.interaction:
                interaction_rows.append({"algorithm": algorithm, **row})

            for round_index, recommendations in enumerate(
                simulation.recommended_history, start=1
            ):
                # An algorithm that could return nothing this round has no
                # diversity to measure. Scoring that as 0 would count
                # "candidate pool exhausted" as "maximally narrow" and drag
                # the arm's mean down — see dev_log problem 25. Recorded as
                # NaN so it is excluded from means rather than silently
                # counted as zero. list_size makes it auditable.
                if recommendations:
                    genres = utils.genres_of(recommendations, movie_genres)
                    scores = diversity_metrics.compute_all(genres, all_genres)
                else:
                    scores = {
                        "genre_diversity": float("nan"),
                        "genre_coverage": float("nan"),
                        "shannon_entropy": float("nan"),
                    }

                metric_rows.append({
                    "algorithm": algorithm,
                    "userId": user_id,
                    "round": round_index,
                    "list_size": len(recommendations),
                    **scores,
                })

                for rank, movie_id in enumerate(recommendations, start=1):
                    recommendation_rows.append({
                        "algorithm": algorithm,
                        "userId": user_id,
                        "round": round_index,
                        "rank": rank,
                        "movieId": movie_id,
                    })

            if position % 25 == 0 or position == len(users):
                print(f"  {algorithm:<14} {position}/{len(users)} users "
                      f"({time.time() - started:.0f}s)")

    return (
        pd.DataFrame(recommendation_rows),
        pd.DataFrame(interaction_rows),
        pd.DataFrame(metric_rows),
    )


def write_outputs(recommendations, interactions, metrics):
    utils.ensure_output_dirs()

    targets = [
        ("recommendations.csv", recommendations),
        ("interactions.csv", interactions),
        ("diversity_metrics.csv", metrics),
    ]

    for filename, frame in targets:
        path = os.path.join(utils.RESULTS_CSV_DIR, filename)
        frame.to_csv(path, index=False)
        print(f"  {filename:<24} {len(frame):>7,} rows")


def make_figures(metrics):
    try:
        import visualization
    except ImportError as error:
        print(f"  skipped ({error}). Run: pip install -r requirements.txt")
        return

    visualization.plot_diversity(metrics)
    visualization.plot_coverage(metrics)
    visualization.plot_entropy(metrics)
    visualization.plot_final_comparison(metrics)
    print(f"  4 figures written to {utils.RESULTS_FIGURES_DIR}")


def summarise(metrics):
    """Round 1 vs final round, averaged over users. Falling values = narrowing."""
    first = metrics["round"].min()
    last = metrics["round"].max()
    columns = ["genre_diversity", "genre_coverage", "shannon_entropy"]

    print(f"\n{'algorithm':<15} {'metric':<17} {'round ' + str(first):>9} "
          f"{'round ' + str(last):>9} {'change':>9}")
    print("-" * 63)

    for algorithm in utils.ALGORITHMS:
        arm = metrics[metrics["algorithm"] == algorithm]
        if arm.empty:
            continue

        start = arm[arm["round"] == first][columns].mean()
        end = arm[arm["round"] == last][columns].mean()

        for column in columns:
            print(f"{algorithm:<15} {column:<17} {start[column]:>9.2f} "
                  f"{end[column]:>9.2f} {end[column] - start[column]:>+9.2f}")


def report_exhaustion(metrics):
    """Rounds where an arm returned fewer than N movies, or nothing at all.

    A short or empty list depresses every diversity metric mechanically, so
    this has to be reported alongside the trends rather than buried.
    """
    print()
    for algorithm in utils.ALGORITHMS:
        arm = metrics[metrics["algorithm"] == algorithm]
        if arm.empty:
            continue

        empty = int((arm["list_size"] == 0).sum())
        short = int(((arm["list_size"] > 0) & (arm["list_size"] < 10)).sum())

        if empty or short:
            users_hit = arm[arm["list_size"] < 10]["userId"].nunique()
            print(f"WARNING  {algorithm}: {empty} empty and {short} short "
                  f"lists across {users_hit} users - candidate pool exhausted. "
                  f"Empty rounds excluded from means.")
        else:
            print(f"OK       {algorithm}: all lists full length")


def main():
    parser = argparse.ArgumentParser(description="Run the echo chamber experiment.")
    parser.add_argument("--users", type=int, default=utils.NUM_USERS)
    parser.add_argument("--rounds", type=int, default=utils.NUM_ROUNDS)
    parser.add_argument("--top-n", type=int, default=utils.TOP_N)
    parser.add_argument("--click-scale", type=float, default=1.0,
                        help="multiplier on affinity to get click probability")
    parser.add_argument("--normalize", default="minmax", choices=["minmax", "scale"])
    parser.add_argument("--k-neighbours", type=int, default=utils.K_NEIGHBOURS,
                        help="neighbours consulted by collaborative filtering. "
                             "Sets the candidate pool size: only movies rated "
                             "by these k users can be recommended. Below 20 the "
                             "pool runs dry mid-experiment for some users and "
                             "the diversity trend is contaminated by empty "
                             "lists. Default 20.")
    parser.add_argument("--no-click-feedback", action="store_true",
                        help="do not add clicked movies to rating history")
    parser.add_argument("--no-figures", action="store_true")
    args = parser.parse_args()

    started = time.time()

    recommendations, interactions, metrics = run_experiment(
        num_users=args.users,
        num_rounds=args.rounds,
        top_n=args.top_n,
        click_scale=args.click_scale,
        feed_clicks_to_ratings=not args.no_click_feedback,
        normalize=args.normalize,
        k_neighbours=args.k_neighbours,
    )

    print("\nWriting results...")
    write_outputs(recommendations, interactions, metrics)

    print("\nFigures...")
    if args.no_figures:
        print("  skipped (--no-figures)")
    else:
        make_figures(metrics)

    clicked = interactions["clicked"].mean() * 100
    summarise(metrics)
    report_exhaustion(metrics)
    print(f"\nClick-through rate: {clicked:.1f}%")
    print(f"Done in {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
