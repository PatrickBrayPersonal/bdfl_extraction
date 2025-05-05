import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

REPORTS = Path("figures/reports")


def load_scores(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])
    return df


def preprocess_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["draft_year"] > 0].copy()
    df["draft_date"] = pd.to_datetime(df["draft_year"].astype(str) + "-04-15")
    df["time_since_draft"] = df["date"] - df["draft_date"]
    df["years_since_draft"] = df["time_since_draft"].dt.days // 365
    return df


def compute_average_value(df: pd.DataFrame, by: list[str]) -> pd.DataFrame | pd.Series:
    grouped = df.groupby(by)["value"].mean()
    if len(by) == 1:
        return grouped  # Series
    else:
        return grouped.unstack()  # DataFrame


def plot_aging_curve(data, output_path: str):
    plt.figure(figsize=(10, 6))

    if isinstance(data, pd.Series):
        plt.plot(data.index, data.values, marker="o")
        plt.title("Average Player Value Over Time Since Draft")
    else:
        for col in data.columns:
            plt.plot(data.index, data[col], marker="o", label=str(col))
        plt.legend(title=", ".join(data.columns.names or ["Group"]))
        plt.title("Average Player Value Over Time Since Draft by Group")

    plt.xlabel("Years Since Draft")
    plt.ylabel("Average Value")
    plt.grid(True)
    plt.xticks(range(data.index.min(), data.index.max() + 1))
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()


def filter_top_48_at_draft(df: pd.DataFrame) -> pd.DataFrame:
    # Snap to draft_date rows
    draft_snapshots = df[df["date"] == df["draft_date"]].copy()

    # Rank players within their draft year by value on draft day
    draft_snapshots["draft_rank"] = draft_snapshots.groupby("draft_year")["value"].rank(
        ascending=False, method="first"
    )

    # Get player_ids who were top 48 at draft
    top_players = draft_snapshots[draft_snapshots["draft_rank"] <= 48]["slug"].unique()

    # Filter original dataframe to only those player_ids
    return df[df["slug"].isin(top_players)]


def log_dataset_stats(df: pd.DataFrame):
    print("=== Dataset Stats ===")
    print(f"Date range       : {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Draft year range : {df['draft_year'].min()} to {df['draft_year'].max()}")
    print(f"Total rows       : {len(df):,}")
    print(f"Unique players   : {df['slug'].nunique():,}")
    print("\nCounts per draft year:")
    print(df.groupby("draft_year")["slug"].nunique())
    print("=====================\n")



def plot_aging_curve_dist(data: pd.DataFrame, output_path: str, plot_type: str = "boxplot", by: str = None):
    plt.figure(figsize=(10, 6))

    # Plot distribution using seaborn
    if plot_type == "histogram":
        # Use hue for differentiation (if 'by' is provided)
        sns.histplot(data=data, x='value', kde=True, bins=30, hue=by)
        plt.title('Distribution of Player Value Over Time Since Draft')
    elif plot_type == "boxplot":
        # Use hue for differentiation (if 'by' is provided)
        sns.boxplot(x='years_since_draft', y='value', data=data, hue=by)
        plt.title('Distribution of Player Value Over Time Since Draft by Group')

    plt.xlabel('Years Since Draft')
    plt.ylabel('Value Distribution')
    plt.grid(True)
    plt.xticks(range(data['years_since_draft'].min(), data['years_since_draft'].max() + 1))
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()


def plot_reports(scores: pd.DataFrame, output_dir: Path):
    log_dataset_stats(scores)
    avg_all = compute_average_value(scores, by=["years_since_draft"])
    plot_aging_curve(avg_all, output_dir / "value_over_time.png")
    # By position - line plot
    avg_by_pos = compute_average_value(scores, by=["years_since_draft", "position"])
    plot_aging_curve(avg_by_pos, output_dir / "value_over_time_by_position.png")

    plot_aging_curve_dist(
        scores, output_dir / "value_distribution.png", plot_type="boxplot"
    )
    plot_aging_curve_dist(
        scores,
        output_dir / "value_distribution_by_position.png",
        plot_type="boxplot",
        by="position",
    )


def main():
    filepath = "data/published/ktc_value_histories_20240929-221650.csv"

    scores = load_scores(filepath)
    scores = preprocess_scores(scores)

    log_dataset_stats(scores)
    plot_reports(scores, REPORTS / "all")

    top_48 = filter_top_48_at_draft(scores)
    plot_reports(top_48, REPORTS / "top_48")

    first_4_rounds = scores[scores["pick_round"] < 4]
    plot_reports(first_4_rounds, REPORTS / "first_4_rounds")


if __name__ == "__main__":
    main()
