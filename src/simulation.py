import random

class Simulation:
    def __init__(self, recommender, user_id):
        self.recommender = recommender
        self.user_id = user_id
        self.interaction = []
        self.recommended_history = []
        self.round_num = 0
    def generate_recs(self): # generate recs for current user
        rcm = self.recommender(self.user_id, self.ratings_data, n=10)
        return rcm
    def simulate_clicks(self, recommendations): # Position-Based Model
        clicks = []
        for position, movie_id in enumerate(recommendations):
            position_probability = 1 / (position + 1)
            attractiveness = 0.5 # NOT THE FINAL VALUE. DETERMINE THE VALUE FOR THIS ONE
            click_probability = position_probability * attractiveness
            if random.random() < click_probability: # simulate which item the user clicks
                clicks.append(movie_id)
        return clicks
    def record_interaction(self, recommendations, clicks): # save recs and user clicks for later
        for movie_id in recommendations:
            interaction = {
                "round": self.round_num,
                "userId": self.user_id,
                "movieId": movie_id,
                "clicked": movie_id in clicks
            }
            self.interaction.append(interaction)
        self.recommended_history.append(recommendations)
    def run(self, num_rounds): # execute num_rounds rounds
        for i in range (num_rounds): # for loop
            self.round_num +=1 # update round_num
            recommendations = self.generate_recs() # generate recs
            clicks = self.simulate_clicks() # simulate user clicks
            self.record_interaction(recommendations, clicks) # record interactions
            return self.interaction
        
# To run in another file:
# from simulation import Simulation
# import popularity
# user_id = 0
# simul1 = Simulation(recommender=popularity.recommend, user_id=user_id, ratings_data=ratings_df.to_dict("records"))
# simul1.run(30)
