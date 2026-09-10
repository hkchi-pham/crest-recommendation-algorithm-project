"""Simulation engine.

Contract: `recommender` is a callable (user_id, n) -> list[movieId].

The three algorithm modules do not share a signature, so they cannot be handed
here directly. Build the callable with one of the utils.make_*_recommender()
factories, which pre-bind whatever dataset that algorithm needs.
"""

import random


class Simulation:
    def __init__(self, recommender, user_id, n=10, click_model=None, seed=None,
                 on_round=None):
        self.recommender = recommender
        self.user_id = user_id
        self.n = n
        self.click_model = click_model or position_based_click_model
        self.rng = random.Random(seed)
        # Feedback hook: called after each round with
        # (user_id, recommendations, clicks). This is what lets interaction
        # history influence the next round.
        self.on_round = on_round

        self.interaction = []
        self.recommended_history = []
        self.clicked_history = []
        self.round_num = 0

    def generate_recs(self):
        """Top-N recommendations for this user, this round."""
        return self.recommender(self.user_id, self.n)

    def simulate_clicks(self, recommendations):
        """Which of the recommended movies the user clicks."""
        return self.click_model(recommendations, self.user_id, self.rng)

    def record_interaction(self, recommendations, clicks):
        """Save recs and user clicks for later."""
        clicked = set(clicks)
        for position, movie_id in enumerate(recommendations):
            self.interaction.append({
                "round": self.round_num,
                "userId": self.user_id,
                "movieId": movie_id,
                "position": position,
                "clicked": movie_id in clicked,
            })
        self.recommended_history.append(recommendations)
        self.clicked_history.append(clicks)

    def run(self, num_rounds):
        """Execute num_rounds rounds and return the full interaction log."""
        for _ in range(num_rounds):
            self.round_num += 1
            recommendations = self.generate_recs()
            clicks = self.simulate_clicks(recommendations)
            self.record_interaction(recommendations, clicks)

            if self.on_round:
                self.on_round(self.user_id, recommendations, clicks)

        return self.interaction


def position_based_click_model(recommendations, user_id, rng):
    """PLACEHOLDER click model. Not the one the methodology specifies.

    docs/methodology.md requires click probability to come from the user's
    genre affinity for the movie. That needs user_profiles.py, which is not
    written yet. Until then this position-based stand-in keeps the simulation
    runnable, but it makes clicks independent of preference, so any result
    produced with it is NOT a valid experimental result.

    Swap it by passing click_model= to Simulation; nothing else changes.
    """
    clicks = []
    for position, movie_id in enumerate(recommendations):
        position_probability = 1 / (position + 1)
        attractiveness = 0.5
        if rng.random() < position_probability * attractiveness:
            clicks.append(movie_id)
    return clicks


def make_affinity_click_model(user_profiles, movie_genres, genre_index, scale=1.0):
    """The click model docs/methodology.md specifies.

        1. Calculate the movie's affinity from the user's genre preferences.
        2. Convert the affinity into a click probability.
        3. Draw a random number; click if it falls below the probability.

    P(click) = affinity * scale, where affinity is the mean of the user's
    preference scores across the movie's genres.

    scale=1.0 is the literal reading of the methodology. Because affinity
    averages roughly 0.5-0.7 under min-max profiles, that yields ~5-7 clicks
    per 10 recommendations, which is high for a real feed but keeps the model
    faithful as written. Lower it for a more realistic click-through rate; it
    applies identically to all three arms either way, so the comparison
    between algorithms is unaffected.

    Unlike the position-based placeholder, clicks here depend on preference,
    which is what the echo chamber mechanism requires.
    """
    from user_profiles import genre_affinity

    def click_model(recommendations, user_id, rng):
        user_vector = user_profiles.get(user_id)
        if user_vector is None:
            return []

        clicks = []
        for movie_id in recommendations:
            affinity = genre_affinity(
                user_vector, movie_genres.get(movie_id, []), genre_index
            )
            if rng.random() < affinity * scale:
                clicks.append(movie_id)

        return clicks

    return click_model
