import pandas as pd
import matplotlib.pyplot as plt
import os

from utils import RESULTS_FIGURES_DIR

# Absolute, resolved from the repo root: saving used to depend on the current
# working directory, so figures landed wherever the script happened to be run.
os.makedirs(RESULTS_FIGURES_DIR, exist_ok=True)


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

    plt.savefig(os.path.join(RESULTS_FIGURES_DIR, "diversity_over_time.png"))
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

    plt.savefig(os.path.join(RESULTS_FIGURES_DIR, "coverage_over_time.png"))
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

    plt.savefig(os.path.join(RESULTS_FIGURES_DIR, "shannon_entropy_over_time.png"))
    plt.close()


def plot_final_comparison(metrics): # Get the final round, Average final metrics across users
    """One subplot per metric, each with its own y-axis.

    A single shared axis made this chart unusable: coverage runs 0-100 while
    entropy runs 0-4.25, so the entropy bars were flat against the baseline
    and the diversity bars were barely legible. The three metrics are on
    different scales and cannot share an axis.

    Each metric shows round 1 beside the final round, so the direction of
    change - the actual finding - is visible rather than just the end state.
    """
    first_round = metrics["round"].min()
    final_round = metrics["round"].max()

    columns = [
        ("genre_diversity", "Genre Diversity", "count of genres"),
        ("genre_coverage", "Genre Coverage", "% of 19 genres"),
        ("shannon_entropy", "Shannon Entropy", "bits"),
    ]

    start_data = (
        metrics[metrics["round"] == first_round]
        .groupby("algorithm")[[c for c, _, _ in columns]]
        .mean()
    )
    end_data = (
        metrics[metrics["round"] == final_round]
        .groupby("algorithm")[[c for c, _, _ in columns]]
        .mean()
    )

    algorithms = list(end_data.index)
    x = range(len(algorithms))
    width = 0.35

    figure, axes = plt.subplots(1, 3, figsize=(14, 5))

    for axis, (column, title, unit) in zip(axes, columns):
        axis.bar([i - width / 2 for i in x], start_data[column], width=width,
                 label=f"Round {first_round}", color="#8fb8de")
        axis.bar([i + width / 2 for i in x], end_data[column], width=width,
                 label=f"Round {final_round}", color="#e08a5d")

        for i, algorithm in enumerate(algorithms):
            change = end_data[column][algorithm] - start_data[column][algorithm]
            axis.text(i, max(start_data[column][algorithm],
                             end_data[column][algorithm]),
                      f"{change:+.2f}", ha="center", va="bottom", fontsize=9)

        axis.set_title(title)
        axis.set_ylabel(unit)
        axis.set_xticks(list(x))
        axis.set_xticklabels(algorithms, rotation=15)
        axis.margins(y=0.15)

    axes[0].legend()
    figure.suptitle(
        f"Diversity at round {first_round} vs round {final_round} "
        "(negative change = narrowing)"
    )
    figure.tight_layout()

    figure.savefig(os.path.join(RESULTS_FIGURES_DIR, "final_comparison.png"),
                   dpi=150)
    plt.close(figure)
