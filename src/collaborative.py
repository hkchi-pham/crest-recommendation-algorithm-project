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


def recommend(
    userId: int,
    userRatings: dict[int, dict[int, float]],
    allMovieIds: list[int],
    n: int = 10,
    kNeighbours: int = 5,
) -> list[int]:
    if userId not in userRatings:
        return []

    userVectors: dict[int, list[float]] = {}
    for uid, ratings in userRatings.items():
        userVectors[uid] = [ratings.get(movieId, 0.0) for movieId in allMovieIds]

    targetVector = userVectors[userId]

    userSimilarities: list[tuple[float, int]] = []
    for otherId, otherVector in userVectors.items():
        if otherId == userId:
            continue

        sim = cosine_similarity(targetVector, otherVector)
        if sim > 0:
            userSimilarities.append((sim, otherId))

    userSimilarities.sort(reverse=True)
    nearestNeighbours = userSimilarities[:kNeighbours]

    if not nearestNeighbours:
        return []

    seenMovies = set(userRatings[userId].keys())
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