ALL_GENRES = ["Action","Sci-fi","Adventure","Romance", "Thriller"]

# Assuming:
# recommendations is a list of movies, each movie contains another list of genres


from collections import Counter
import math

def genre_diversity(recommendations):
    unique_genres = set()
    for genres in recommendations:
        unique_genres.update(genres)

    return len(unique_genres)

def genre_coverage(recommendations): # % of all genres
    genres_seen = set()
    for genres in recommendations:
         genres_seen.update(genres)

    return len(genres_seen) / len(ALL_GENRES) * 100

def shannon_entropy(recommendations): # higher return -> recs are more evenly spread
    entropy = 0
    genre_counter = Counter()
    for genres in recommendations:
        genre_counter.update(genres)

    total = sum(genre_counter.values())

    for count in genre_counter.values():
        p = count / total
        entropy -= p * math.log2(p)

    return entropy

# !! TEST !!
testlist = [["Action","Adventure"],["Action", "Romance"],["Thriller", "Romance"]]
print("Genre diversity: ", genre_diversity(testlist))
print("Genre coverage: ", genre_coverage(testlist))
print("Shannon entropy: ", shannon_entropy(testlist))