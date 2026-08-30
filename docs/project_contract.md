# Echo Chamber Recommendation System Project Contract

This document serves as the shared agreement for our project. Before anyone starts coding, everyone should read the whole document once so we all understand the research goal. After that, each member should mainly focus on the sections related to their responsibilities.

## Research objective

Research question: To what extent do different recommendation paradigms (Popularity-Based, Content-Based Filtering and Collaborative Filtering) affect content diversity and contribute to echo chamber formation?

The goal is not to recreate YouTube, TikTok or Instagram. We are implementing standard textbook recommendation algorithms in a controlled simulation so we can compare their behaviour fairly.

## Experimental design

- Independent variable: Recommendation algorithm (Popularity-Based, Content-Based, Collaborative Filtering).
- Dependent variables: Genre Diversity, Genre Coverage and Shannon Entropy.
- Controlled variables: MovieLens dataset, same sampled users, same number of recommendations per round, same simulation rounds, same click model, same random seed.

## Dataset

We will use MovieLens (movies.csv and ratings.csv).
- movies.csv provides movieId, title and genres.
- ratings.csv provides userId, movieId and rating.
- tags.csv and timestamps will **not** be used.

## User profiles

Historical ratings are converted into genre preference scores between 0 and 1. These preference profiles stay fixed throughout the experiment. User interaction history changes during the simulation, but user preferences do not.

## Recommendation algorithms

- Popularity-Based: Recommend globally popular unseen movies.
- Content-Based Filtering: Recommend movies with genres similar to the user's preference profile.
- Collaborative Filtering: Recommend movies liked by users with similar rating behaviour.

## Simulation
For each algorithm independently: generate recommendations, simulate clicks based on genre preference, record interaction history, repeat for 30 rounds.

## Click model

Each recommended movie receives an affinity score based on the user's preferences for its genres. This affinity becomes the probability of clicking the movie. A random number determines whether the click occurs.

## Evaluation metrics

- Genre Diversity: Number of unique genres in the recommendation list.
- Genre Coverage: Percentage of all genres exposed to the user.
- Shannon Entropy: Measures how evenly recommendations are distributed across genres.

Metrics are calculated after every round and compared across all three algorithms.

## Project architecture

MovieLens -> data_loader -> user_profiles -> recommendation algorithms -> simulation -> diversity metrics -> analysis notebook -> report.

## Member responsibilities
- Khanh Chi (Project Lead / Research): literature review, methodology, hypotheses, experimental design, choosing metrics, interpreting results, coordinating the project.
- Nhat Minh (Data & Recommenders): data loading, preprocessing, user profile generation, popularity recommender, content-based recommender, collaborative recommender.
- Hong Anh (Simulation & Analysis): simulation engine, diversity metric implementation, visualisations, experiment execution and analysis notebook.

## Development workflow
Nobody should change another member's module without discussing it first. Use GitHub, commit regularly, and merge only after testing. Before coding begins, everyone should agree on the methodology so all modules are compatible.
Expected outputs
recommendations.csv, interactions.csv, diversity_metrics.csv, analysis graphs and the final research report.


