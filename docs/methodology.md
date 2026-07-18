**Methodology**

This document defines the experimental methodology used throughout the project. Every implementation should follow this specification unless the team agrees on a documented revision.

---

**Research Question**

To what extent do different recommendation paradigms (Popularity-Based, Content-Based Filtering, and Collaborative Filtering) affect content diversity and contribute to echo chamber formation?

---

**Experimental Objective**

The objective of this project is to compare three classical recommendation algorithms under the same controlled environment. Instead of reproducing industrial-scale recommendation systems such as YouTube, TikTok or Instagram, this project evaluates the underlying recommendation paradigms using a simplified simulation.

The experiment focuses on whether different recommendation algorithms reduce the diversity of content shown to users over repeated interactions.

---

**Experimental Design**

**Independent Variable**

Recommendation algorithm.

Three recommendation paradigms will be evaluated:

* Popularity-Based Recommendation
* Content-Based Filtering
* User-User Collaborative Filtering

---

**Dependent Variables**

Content diversity will be measured using three metrics.

* Genre Diversity
* Genre Coverage
* Shannon Entropy

These metrics are used as indicators of potential echo chamber formation.

---

**Controlled Variables**

The following conditions remain identical for every experiment.

* MovieLens dataset
* Same sampled users
* Same number of recommendation rounds
* Same recommendation list length
* Same click probability model
* Same random seed
* Same user preference generation process

Keeping these variables fixed ensures that any observed differences are caused by the recommendation algorithm rather than changes in the experimental environment.

---

**Dataset**

The MovieLens dataset is used for all experiments.

Files:

* movies.csv
* ratings.csv

Information extracted from the dataset:

movies.csv

* movieId
* title
* genres

ratings.csv

* userId
* movieId
* rating

The tag dataset is not used because the project investigates recommendation behaviour based on user ratings and movie genres.

---

**User Sampling**

A subset of users will be randomly selected from the dataset.

Current planned configuration:

* Number of users: 100
* Random seed: 42

This provides a manageable yet representative sample while keeping computation efficient.

---

**User Preference Profiles**

Each user's historical ratings are converted into a genre preference profile.

The process is:

1. Merge movie genres with user ratings.
2. Compute the average rating for every genre.
3. Normalize preference scores to the range [0, 1].

Example:

Action → 0.91

Comedy → 0.67

Romance → 0.24

These preference profiles remain fixed throughout the experiment.

Only the user's interaction history changes during the simulation.

This design isolates the effect of recommendation algorithms from changes in user preferences.

---

**Recommendation Algorithms**

Three recommendation algorithms will be implemented.

**Popularity-Based Recommendation**

Movies are ranked using a popularity score calculated from:

Average Rating × log(Number of Ratings)

Recommendations are generated using the highest-ranked unseen movies.

No personalization is performed.

---

**Content-Based Filtering**

Each movie is represented by its genres.

Each user is represented by a genre preference vector.

Cosine similarity is used to measure how well a movie matches the user's interests.

Movies with the highest similarity scores are recommended.

---

**Collaborative Filtering**

User-user collaborative filtering will be implemented.

The process consists of:

* Constructing a user-item rating matrix.
* Computing cosine similarity between users.
* Finding neighbouring users.
* Recommending highly rated unseen movies from similar users.

---

**Simulation Environment**

Each recommendation algorithm is evaluated independently.

For each algorithm:

1. Generate recommendations.
2. Simulate user interaction.
3. Record interactions.
4. Repeat for multiple rounds.

Current planned configuration:

* Recommendation list length: 10 movies
* Number of rounds: 30

---

**Click Model**

The probability that a user clicks a recommended movie depends on how closely the movie matches the user's preferences.

For each recommended movie:

1. Calculate its affinity based on the user's preferences for the movie's genres.
2. Convert the affinity into a click probability.
3. Generate a random value between 0 and 1.
4. If the random value is smaller than the click probability, the user clicks the movie.

The click model remains identical for every recommendation algorithm.

---

**Interaction History**

Clicked movies are stored as part of the user's interaction history.

Interaction history is used during the simulation.

User preference profiles are not updated after clicks.

This ensures that changes in recommendation diversity are caused by the recommendation algorithm rather than changing user preferences.

---

**Evaluation Metrics**

Three diversity metrics will be calculated after every simulation round.

**Genre Diversity**

Measures the number of unique genres appearing within the recommendation list.

Higher values indicate exposure to a wider range of content categories.

---

**Genre Coverage**

Measures the proportion of all available genres that appear in the recommendation list.

Genre Coverage = Number of Genres Recommended ÷ Total Number of Genres

Higher coverage indicates broader exposure across the available content catalogue.

---

**Shannon Entropy**

Measures how evenly recommendations are distributed across genres.

Higher entropy indicates a balanced recommendation distribution.

Lower entropy indicates recommendations concentrated around only a few genres.

---

**Experimental Workflow**

The complete experimental workflow is:

1. Load MovieLens dataset.
2. Clean and preprocess the data.
3. Generate user preference profiles.
4. Build the three recommendation models.
5. Run the simulation independently for each algorithm.
6. Record user interactions.
7. Calculate diversity metrics after every simulation round.
8. Compare diversity trends across algorithms.
9. Interpret the results in relation to echo chamber formation.

---

**Expected Outputs**

The experiment should generate:

* Recommendation history
* User interaction history
* Diversity metric results
* Visualisations comparing recommendation algorithms

These outputs will be used in the final analysis and discussion.
