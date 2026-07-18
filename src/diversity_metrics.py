from collections import Counter
import math

def genre_diversity(recommendations):
    genres = []
    for movie in recommendations:
        