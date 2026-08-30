import pandas as pd
import matplotlib.pyplot as plt
import os


os.makedirs("results/figures", exist_ok=True)


def plot_diversity(metrics): # Average diversity across users for each round and algorithm over time
    data = (
        metrics
        .groupby(["round", "algorithm"])["genre_diversity"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(10, 6))

    for algorithm in data["algorithm"].unique():
        algorithm_data = data[data["algorithm"] == algorithm]

        plt.plot(
            algorithm_data["round"],
            algorithm_data["genre_diversity"],
            label=algorithm
        )

    plt.xlabel("Round")
    plt.ylabel("Genre Diversity")
    plt.title("Genre Diversity Over Time")
    plt.legend()
    plt.tight_layout()

    plt.savefig("results/figures/diversity_over_time.png")
    plt.close()


def plot_coverage(metrics): # Average coverage across users for each round and algorithm
    data = (
        metrics
        .groupby(["round", "algorithm"])["genre_coverage"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(10, 6))

    for algorithm in data["algorithm"].unique():
        algorithm_data = data[data["algorithm"] == algorithm]

        plt.plot(
            algorithm_data["round"],
            algorithm_data["genre_coverage"],
            label=algorithm
        )

    plt.xlabel("Round")
    plt.ylabel("Genre Coverage (%)")
    plt.title("Genre Coverage Over Time")
    plt.legend()
    plt.tight_layout()

    plt.savefig("results/figures/coverage_over_time.png")
    plt.close()


def plot_entropy(metrics): # Average entropy across users for each round and algorithm
    data = (
        metrics
        .groupby(["round", "algorithm"])["shannon_entropy"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(10, 6))

    for algorithm in data["algorithm"].unique():
        algorithm_data = data[data["algorithm"] == algorithm]

        plt.plot(
            algorithm_data["round"],
            algorithm_data["shannon_entropy"],
            label=algorithm
        )

    plt.xlabel("Round")
    plt.ylabel("Shannon Entropy")
    plt.title("Shannon Entropy Over Time")
    plt.legend()
    plt.tight_layout()

    plt.savefig("results/figures/shannon_entropy_over_time.png")
    plt.close()


def plot_final_comparison(metrics): # Get the final round, Average final metrics across users
    final_round = metrics["round"].max()

    final_data = metrics[metrics["round"] == final_round]

    final_data = (
        final_data
        .groupby("algorithm")[
            ["genre_diversity", "genre_coverage", "shannon_entropy"]
        ]
        .mean()
        .reset_index()
    )

    algorithms = final_data["algorithm"]
    x = range(len(algorithms))
    width = 0.25

    plt.figure(figsize=(10, 6))

    plt.bar(
        [i - width for i in x],
        final_data["genre_diversity"],
        width=width,
        label="Genre Diversity"
    )

    plt.bar(
        x,
        final_data["genre_coverage"],
        width=width,
        label="Genre Coverage"
    )

    plt.bar(
        [i + width for i in x],
        final_data["shannon_entropy"],
        width=width,
        label="Shannon Entropy"
    )

    plt.xlabel("Algorithm")
    plt.ylabel("Metric Value")
    plt.title("Final Comparison Between Algorithms")
    plt.xticks(x, algorithms)
    plt.legend()
    plt.tight_layout()

    plt.savefig("results/figures/final_comparison.png")
    plt.close()