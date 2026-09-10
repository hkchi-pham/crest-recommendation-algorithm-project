import math


def cosine_similarity(vectorA: list[float], vectorB: list[float]) -> float:
    dotProduct = 0.0
    sumSqA = 0.0
    sumSqB = 0.0

    vectorLength = len(vectorA)

    for i in range(vectorLength):
        dotProduct += vectorA[i] * vectorB[i]
        sumSqA += vectorA[i] * vectorA[i]
        sumSqB += vectorB[i] * vectorB[i]

    magnitudeA = math.sqrt(sumSqA)
    magnitudeB = math.sqrt(sumSqB)

    if magnitudeA == 0.0 or magnitudeB == 0.0:
        return 0.0

    return dotProduct / (magnitudeA * magnitudeB)


def build_user_vectors(
    userRatings: dict[int, dict[int, float]],
    allMovieIds: list[int],
) -> dict[int, list[float]]:
    """Build the user-item rating matrix once.

    Separated from recommend() so callers can build it a single time and reuse
    it across every user and every round. Rebuilding it per call is 610 x 9708
    floats each time, which the 30-round simulation cannot afford.
    """
    userVectors: dict[int, list[float]] = {}
    for uid, ratings in userRatings.items():
        userVectors[uid] = [ratings.get(movieId, 0.0) for movieId in allMovieIds]
    return userVectors


def sparse_cosine(ratingsA: dict[int, float], ratingsB: dict[int, float]) -> float:
    """Cosine similarity between two users, computed over rated items only.

    Mathematically identical to cosine_similarity() on the dense vectors:
    unrated items are 0.0 and contribute nothing to either the dot product or
    the magnitudes. Iterating the rating dicts costs ~165 operations (the
    average user's rating count) instead of 9,708.
    """
    if len(ratingsA) > len(ratingsB):
        ratingsA, ratingsB = ratingsB, ratingsA

    dotProduct = 0.0
    for movieId, rating in ratingsA.items():
        other = ratingsB.get(movieId)
        if other is not None:
            dotProduct += rating * other

    if dotProduct == 0.0:
        return 0.0

    magnitudeA = math.sqrt(sum(r * r for r in ratingsA.values()))
    magnitudeB = math.sqrt(sum(r * r for r in ratingsB.values()))

    if magnitudeA == 0.0 or magnitudeB == 0.0:
        return 0.0

    return dotProduct / (magnitudeA * magnitudeB)


def recommend(
    userId: int,
    userRatings: dict[int, dict[int, float]],
    allMovieIds: list[int] | None = None,
    n: int = 10,
    kNeighbours: int = 5,
    userVectors: dict[int, list[float]] | None = None,
    excludeMovieIds: set[int] | None = None,
) -> list[int]:
    """Recommend n unseen movies liked by the user's k most similar neighbours.

    kNeighbours (k) — how many of the most similar users are consulted.

    WHAT IT CONTROLS
        Only movies rated by these k neighbours can ever be recommended. The
        union of their rated movies, minus what the user has already seen, is
        the entire candidate pool. k therefore sets the pool size directly:
        small k = few contributors = small pool.

    WHY IT MATTERS HERE
        A 30-round run at N=10 consumes 300 movies per user. At k=5 the pool
        for low-activity users had a median of ~100 movies, because users with
        few ratings are most similar to other users with few ratings. Those
        users ran out mid-experiment and recommend() returned an empty list —
        which, scored as diversity 0, produced a false echo chamber signal.
        Raising k widens the pool because each extra neighbour contributes
        their own rated movies to the union.

    WHY k=20
        Measured over the 100 sampled users: k=5 left 31 users with a pool
        under the 300 needed, k=10 left 19, k=20 left 1, k=30 left none.
        k=20 is the smallest value at which the experiment completes for
        essentially every user, and the measured diversity result is stable
        from k=20 upward (+1.57, +1.17, +1.21 at k=20/30/50) while being
        depressed below it by truncation (+0.68 at k=5, +0.14 at k=10).

        Critically, round-1 diversity barely moves with k (10.58 to 11.30
        across k=5..50), so raising k does NOT inflate the metric — it only
        determines whether the run can finish. That is what makes k=20 a
        measurement fix rather than a thumb on the scale.

        Larger k is not automatically better: it averages over more people, so
        recommendations drift toward the crowd and collaborative filtering
        starts behaving like popularity. The smallest k that removes the
        artefact is the right choice, not the largest.
    """
    if userId not in userRatings:
        return []

    excludeMovieIds = excludeMovieIds or set()

    targetRatings = userRatings[userId]

    userSimilarities: list[tuple[float, int]] = []
    for otherId, otherRatings in userRatings.items():
        if otherId == userId:
            continue

        sim = sparse_cosine(targetRatings, otherRatings)
        if sim > 0:
            userSimilarities.append((sim, otherId))

    userSimilarities.sort(reverse=True)
    nearestNeighbours = userSimilarities[:kNeighbours]

    if not nearestNeighbours:
        return []

    seenMovies = set(userRatings[userId].keys()) | excludeMovieIds
    candidateScores: dict[int, float] = {}

    for sim, neighbourId in nearestNeighbours:
        for movieId, rating in userRatings[neighbourId].items():
            if movieId not in seenMovies:
                candidateScores[movieId] = (
                    candidateScores.get(movieId, 0.0) + sim * rating
                )

    rankedMovies = [
        (score, movieId) for movieId, score in candidateScores.items()
    ]
    rankedMovies.sort(reverse=True)

    topMovies: list[int] = []
    for i in range(min(n, len(rankedMovies))):
        topMovies.append(rankedMovies[i][1])

    return topMovies