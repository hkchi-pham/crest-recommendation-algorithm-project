import matplotlib.pyplot as plt
import os


os.makedirs("results/figures", exist_ok=True)


def plot_genre_diversity(metrics):
    data = (
        metrics
        .groupby("algorithm")["genre_diversity"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(8, 6))

    plt.bar(
        data["algorithm"],
        data["genre_diversity"]
    )

    plt.xlabel("Algorithm")
    plt.ylabel("Genre Diversity")
    plt.title("Genre Diversity by Recommendation Algorithm")

    plt.tight_layout()
    plt.savefig("results/figures/genre_diversity.png")
    plt.close()


def plot_genre_coverage(metrics):
    data = (
        metrics
        .groupby("algorithm")["genre_coverage"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(8, 6))

    plt.bar(
        data["algorithm"],
        data["genre_coverage"]
    )

    plt.xlabel("Algorithm")
    plt.ylabel("Genre Coverage (%)")
    plt.title("Genre Coverage by Recommendation Algorithm")

    plt.tight_layout()
    plt.savefig("results/figures/genre_coverage.png")
    plt.close()


def plot_shannon_entropy(metrics):
    data = (
        metrics
        .groupby("algorithm")["shannon_entropy"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(8, 6))

    plt.bar(
        data["algorithm"],
        data["shannon_entropy"]
    )

    plt.xlabel("Algorithm")
    plt.ylabel("Shannon Entropy")
    plt.title("Shannon Entropy by Recommendation Algorithm")

    plt.tight_layout()
    plt.savefig("results/figures/shannon_entropy.png")
    plt.close()