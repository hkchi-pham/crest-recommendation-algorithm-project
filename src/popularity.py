import math

def recommend(userId: int, ratingsData: list, n: int = 10) -> list[int]:
    movieTotals = {}  
    movieCounts = {}  
    seenMovies = []   
    
    for record in ratingsData:
        currentMovie = record['movie_id']
        currentUser = record['user_id']
        currentRating = record['rating']
        
        if currentUser == userId:
            seenMovies.append(currentMovie)
            
        if currentMovie not in movieCounts:
            movieTotals[currentMovie] = 0
            movieCounts[currentMovie] = 0
            
            
        movieTotals[currentMovie] = movieTotals[currentMovie] + currentRating
        movieCounts[currentMovie] = movieCounts[currentMovie] + 1
        
    movieScores = [] 
    
    for movie in movieCounts:
        if movie in seenMovies:
            continue
            
        averageRating = movieTotals[movie] / movieCounts[movie]
        score = averageRating * math.log(movieCounts[movie])
        
        movieScores.append((score, movie))
        
    movieScores.sort(reverse=True)
    
    topMovies = []
    
    for i in range(min(n, len(movieScores))):
        topMovies.append(movieScores[i][1])
        
    return topMovies
