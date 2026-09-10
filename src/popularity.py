import math

def recommend(userId: int, ratingsData: list, n: int = 10) -> list[int]:
    movieTotals = {}  
    movieCounts = {}  
    seenMovieIds = set()   
    
    for record in ratingsData:
        currentMovieId = record['movieId']
        currentUserId = record['userId']
        currentRating = record['rating']
        
        if currentUserId == userId:
            seenMovieIds.add(currentMovieId)
            
        if currentMovieId not in movieCounts:
            movieTotals[currentMovieId] = 0
            movieCounts[currentMovieId] = 0
            
            
        movieTotals[currentMovieId] = movieTotals[currentMovieId] + currentRating
        movieCounts[currentMovieId] = movieCounts[currentMovieId] + 1
        
    movieScores = [] 
    
    for movieId in movieCounts:
        if movieId in seenMovieIds:
            continue
        averageRating = movieTotals[movieId] / movieCounts[movieId]
        score = averageRating * math.log(movieCounts[movieId])
        
        movieScores.append((score, movieId))
        
    movieScores.sort(reverse=True)
    
    topMovieIds = []
    
    for i in range(min(n, len(movieScores))):
        topMovieIds.append(movieScores[i][1])
        
    return topMovieIds


def build_popularity_ranking(ratingsData: list) -> list[tuple[float, int]]:
    """Global popularity ranking, computed once.

    The score is unpersonalised and never changes during the experiment, so
    rescanning all 100,836 rating records on every call is pure waste.
    Same formula as recommend(): average rating * log(number of ratings).
    """
    movieTotals = {}
    movieCounts = {}

    for record in ratingsData:
        currentMovieId = record['movieId']
        currentRating = record['rating']

        if currentMovieId not in movieCounts:
            movieTotals[currentMovieId] = 0
            movieCounts[currentMovieId] = 0

        movieTotals[currentMovieId] += currentRating
        movieCounts[currentMovieId] += 1

    ranking = []
    for movieId in movieCounts:
        averageRating = movieTotals[movieId] / movieCounts[movieId]
        score = averageRating * math.log(movieCounts[movieId])
        ranking.append((score, movieId))

    ranking.sort(reverse=True)
    return ranking


def recommend_from_ranking(
    ranking: list[tuple[float, int]],
    excludeMovieIds: set[int] | None = None,
    n: int = 10,
) -> list[int]:
    """Top n unseen movies from a prebuilt ranking."""
    excludeMovieIds = excludeMovieIds or set()

    topMovieIds = []
    for _, movieId in ranking:
        if movieId in excludeMovieIds:
            continue

        topMovieIds.append(movieId)
        if len(topMovieIds) == n:
            break

    return topMovieIds
