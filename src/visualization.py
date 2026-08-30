import pandas as pd
import matplotlib.pyplot as plt
import os


os.makedirs("results/figures", exist_ok=True)


def plot_diversity(metrics): # metrics is expected to be a dataframe
    plt.figure(figsize=(10, 6))

    for algorithm in metrics["algorithm"].unique():
        data = metrics[metrics["algorithm"] == algorithm]

        plt.plot(
            data["round"],
            data["genre_diversity"],
            label=algorithm
        )

    plt.xlabel("Round")
    plt.ylabel("Genre Diversity")
    plt.title("Genre Diversity Over Time")
    plt.legend()
    plt.tight_layout()

    plt.savefig("results/figures/diversity_over_time.png")
    plt.close()


def plot_coverage(metrics):
    plt.figure(figsize=(10, 6))

    for algorithm in metrics["algorithm"].unique():
        data = metrics[metrics["algorithm"] == algorithm]

        plt.plot(
            data["round"],
            data["genre_coverage"],
            label=algorithm
        )

    plt.xlabel("Round")
    plt.ylabel("Genre Coverage (%)")
    plt.title("Genre Coverage Over Time")
    plt.legend()
    plt.tight_layout()

    plt.savefig("results/figures/coverage_over_time.png")
    plt.close()


def plot_entropy(metrics):
    plt.figure(figsize=(10, 6))

    for algorithm in metrics["algorithm"].unique():
        data = metrics[metrics["algorithm"] == algorithm]

        plt.plot(
            data["round"],
            data["shannon_entropy"],
            label=algorithm
        )

    plt.xlabel("Round")
    plt.ylabel("Shannon Entropy")
    plt.title("Shannon Entropy Over Time")
    plt.legend()
    plt.tight_layout()

    plt.savefig("results/figures/shannon_entropy_over_time.png")
    plt.close()


def plot_final_comparison(metrics):
    final_round = metrics["round"].max()
    final_data = metrics[metrics["round"] == final_round]

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