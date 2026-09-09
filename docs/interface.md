## data_loader.py

- Load data from file movies.csv and ratings csv in data/raw
- Clear null data items
- Parse genre into array/list format
- Create movies_df and ratings_df for later use
- Also store movies_df and ratings_df as csv files in data/processed

## simulation.py
- Contains the Simulation class that is used to simulate user interaction
- Generate Top-N movie recommendations for a single user
- Simulate user clicks
- Record recommended movies for user interactions
- Repeat the recommendation and interaction process for the agreed number of 30 rounds
- Store interaction history for later analysis

## diversity_metrics.py
- Calculate the diversity of genres in recommendation lists
- Calculate genre coverage across all available genres
- Calculate Shannon entropy to measure how evenly genres are spread
- Provide separate functions for each diversity metric
- Return metric values for use in analysis

## visualisation.py
- Generate visualisations from calculated results
- Create line chart to show genre diversity over 30 rounds
- Create line chart to show genre coverage over 30 rounds
- Create line chart to show Shannon entropy over 30 rounds
- Save all generated figures in results/figures