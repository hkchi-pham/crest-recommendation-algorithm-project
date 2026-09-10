import pandas as pd
import ast
import os

from utils import RAW_DIR, PROCESSED_DIR


def load_data(movies_path=None,
              ratings_path=None,
              save_processed=True,
              processed_dir=None):
    # Paths are resolved from the repo root (utils.PROJECT_ROOT) so the loader
    # works on every team member's machine.
    movies_path = movies_path or os.path.join(RAW_DIR, "movies.csv")
    ratings_path = ratings_path or os.path.join(RAW_DIR, "ratings.csv")
    processed_dir = processed_dir or PROCESSED_DIR

    movies_df = pd.read_csv(movies_path)
    ratings_df = pd.read_csv(ratings_path)

    movies_df = movies_df.dropna().reset_index(drop=True)
    ratings_df = ratings_df.dropna().reset_index(drop=True)

    def parse_genres(genres):

        if pd.isna(genres):
            return []

        genres = str(genres)

        if genres.startswith("["):
            try:
                return ast.literal_eval(genres)
            except:
                return []

        return genres.split("|")

    movies_df['genres'] = movies_df['genres'].apply(parse_genres)

    # Movies with no genre listed carry no diversity signal and would inflate
    # the genre universe with a fake 21st genre.
    movies_df = movies_df[
        movies_df['genres'].apply(lambda g: g != ["(no genres listed)"])
    ].reset_index(drop=True)

    if save_processed:
        os.makedirs(processed_dir, exist_ok=True)

        movies_df.to_csv(os.path.join(processed_dir, "movies_df.csv"), index=False)
        ratings_df.to_csv(os.path.join(processed_dir, "ratings_df.csv"), index=False)

    return movies_df, ratings_df


if __name__ == "__main__":
    movies_df, ratings_df = load_data()

    print("Movies shape:", movies_df.shape)
    print("Ratings shape:", ratings_df.shape)

    print("\nMovies:")
    print(movies_df.head())

    print("\nRatings:")
    print(ratings_df.head())
