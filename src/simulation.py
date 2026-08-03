class Simulation:
    def __init__(self, recommender, user_id):
        self.recommender = recommender
        self.user_id = user_id
        self.interaction = []
        self.recommended_history = []
        self.round_num = 0
    def generate_recs(self): # generate recs for current user
        pass
        # take in recommender algorithm to generate recs
        # return recommendations
    def simulate_clicks(self):
        pass
        # simulate which item the user clicks
        # return clicks
    def record_interaction(self, recommendations, clicks):
        pass
        # save recs and user clicks for later
    def run(self, num_rounds): # execute num_rounds rounds
        pass
        # for loop
        # generate recs
        # simulate user clicks
        # record interactions
        # update round_num
    

