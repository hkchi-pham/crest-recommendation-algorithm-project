import math

def recommend(userId: int, ratingsData: list, n: int = 10) -> list[int]:
    movieTotals = {}  
    movieCounts = {}  
    seenMovieIds = []   
    
    for record in ratingsData:
        currentMovieId = record['movie_id']
        currentUserId = record['user_id']
        currentRating = record['rating']
        
        if currentUserId == userId:
            seenMovieIds.append(currentMovieId)
            
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
