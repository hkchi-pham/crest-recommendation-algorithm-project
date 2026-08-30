import math


def cosine_similarity(userVector: list[float], movieVector: list[float]) -> float:
    dotProduct = 0.0
    sumSqUser = 0.0
    sumSqMovie = 0.0

    vectorLength = len(userVector)

    for i in range(vectorLength):
        dotProduct += userVector[i] * movieVector[i]
        sumSqUser += userVector[i] * userVector[i]
        sumSqMovie += movieVector[i] * movieVector[i]

    userMagnitude = math.sqrt(sumSqUser)
    movieMagnitude = math.sqrt(sumSqMovie)

    if userMagnitude == 0 or movieMagnitude == 0:
        return 0.0

    return dotProduct / (userMagnitude * movieMagnitude)


def recommend(
    userId: int,
    userProfiles: dict[int, list[float]],
    movieProfiles: dict[int, list[float]],
    n: int = 10,
) -> list[int]:
    if userId not in userProfiles:
        return []

    currentUserVector = userProfiles[userId]
    movieScores = []

    for movieId, currentMovieVector in movieProfiles.items():
        similarityScore = cosine_similarity(currentUserVector, currentMovieVector)
        movieScores.append((similarityScore, movieId))

    movieScores.sort(reverse=True)

    topMovies = []

    for i in range(min(n, len(movieScores))):
        topMovies.append(movieScores[i][1])

    return topMovies