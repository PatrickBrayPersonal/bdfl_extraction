"""Fantasy Football Top Risers Dashboard.

Compact 3-column interface showing top 5 rising players for 1 day, 1 month, and 1 year periods.
"""

from typing import Optional

import pandas as pd
import streamlit as st
from loguru import logger


def find_top_n_spikes(
    df: pd.DataFrame,
    value_col: str = "value",
    group_col: str = "slug",
    n_steps: int = 7,
    top_n: int = 5,
) -> pd.DataFrame:
    """Find players with the top N value increases over a specified period.

    Args:
        df: DataFrame containing player value data with date, player info, and values.
        value_col: Name of the column containing player values.
        group_col: Name of the column to group by (typically player identifier).
        n_steps: Number of time steps to look back for calculating value changes.
        top_n: Number of top rising players to return.

    Returns:
        DataFrame with top rising players including rise amount, dates, and values.
    """
    logger.info(f"Finding top {top_n} spikes over {n_steps} steps")

    if n_steps <= 0 or top_n <= 0:
        return pd.DataFrame()

    required_cols = [group_col, "date", value_col, "player_name"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.warning(f"Missing required columns: {missing_cols}")
        return pd.DataFrame()

    # Sort and calculate deltas
    df_sorted = df.sort_values(by=[group_col, "date"]).copy()
    delta_col = f"delta_{n_steps}"
    df_sorted[delta_col] = df_sorted.groupby(group_col)[value_col].diff(n_steps)

    # Get top spikes
    top_spikes = df_sorted.nlargest(top_n * 50, delta_col)

    # Build results
    results = []
    for _, row in top_spikes.iterrows():
        start_idx = max(0, row.name - n_steps)
        try:
            result_data = {
                "player": row["player_name"],
                "rise": row[delta_col],
                "start_date": df_sorted.loc[start_idx, "date"],
                "end_date": row["date"],
                "start_value": df_sorted.loc[start_idx, value_col],
                "end_value": row[value_col],
            }
            results.append(result_data)
        except (KeyError, IndexError):
            continue

    if not results:
        return pd.DataFrame()

    # Remove duplicates and return top N
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("rise", ascending=False)
    results_df = results_df.drop_duplicates(
        subset=["player"], keep="first"
    ).reset_index(drop=True)

    return results_df.head(top_n)


def load_default_data() -> Optional[pd.DataFrame]:
    """Load the default CSV data file.

    Returns:
        DataFrame containing the loaded data, or None if loading fails.
    """
    default_file = "data/published/ktc_value_histories_20240929-221650.csv"
    try:
        df = pd.read_csv(default_file)
        logger.info(f"Loaded {len(df)} rows of data")
        return df
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return None


def calculate_percentage_change(start_value: float, end_value: float) -> float:
    """Calculate percentage change between two values.

    Args:
        start_value: Initial value.
        end_value: Final value.

    Returns:
        Percentage change as a float.
    """
    if start_value == 0:
        return 0.0
    return ((end_value - start_value) / start_value) * 100


def create_compact_player_card(player_data: pd.Series, rank: int) -> None:
    """Create a compact player card using basic Streamlit components.

    Args:
        player_data: Series containing player information and metrics.
        rank: Player's rank in the top risers list.
    """
    rise = player_data["rise"]
    start_value = player_data["start_value"]
    end_value = player_data["end_value"]
    percentage_change = calculate_percentage_change(start_value, end_value)

    # Format dates
    start_date = pd.to_datetime(player_data["start_date"]).strftime("%b-%d-%Y")
    end_date = pd.to_datetime(player_data["end_date"]).strftime("%b-%d-%Y")

    # Create card using basic Streamlit components
    with st.container():
        # Player name and rank
        st.subheader(f"#{rank} {player_data['player']}")

        # Date range
        st.caption(f"{start_date} → {end_date}")

        # Metrics in columns
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="Value Rise", value=f"{end_value:.0f}", delta=f"+{rise:.0f}"
            )

        with col2:
            st.metric(
                label="Growth",
                value=f"+{percentage_change:.1f}%",
            )


def display_column_section(df: pd.DataFrame, title: str, days: int, col) -> None:
    """Display a column section with top 5 player cards.

    Args:
        df: DataFrame containing player value data.
        title: Column title.
        days: Number of days for the analysis.
        col: Streamlit column object.
    """
    with col:
        st.markdown(f"### {title}")

        try:
            results = find_top_n_spikes(df, n_steps=days, top_n=5)

            if results.empty:
                st.warning("No data available")
                return

            # Create compact cards
            for i, (_, player) in enumerate(results.iterrows(), 1):
                create_compact_player_card(player, i)

        except Exception as e:
            logger.error(f"Error analyzing {title} data: {e}")
            st.error(f"Error loading {title.lower()} data")


def app() -> None:
    """Main Streamlit application for the Fantasy Football Top Risers Dashboard.

    Displays a compact 3-column layout with top 5 rising players for each time period.
    """
    logger.info("Starting Fantasy Football Top Risers Dashboard")

    # App configuration
    st.set_page_config(
        page_title="Fantasy Football Top Risers",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Header
    st.title("🚀 Fantasy Football Top Risers")
    st.markdown("**Top 5 rising players across different time periods**")

    # Load data
    df = load_default_data()
    if df is None:
        st.error("Unable to load data. Please check if the data file exists.")
        st.stop()

    # Create 3-column layout
    col1, col2, col3 = st.columns(3)

    # Display each time period
    display_column_section(df, "1 Day", 1, col1)
    display_column_section(df, "1 Month", 30, col2)
    display_column_section(df, "1 Year", 365, col3)

    # Footer
    st.divider()
    st.caption("Data from KeepTradeCut • Updated regularly")


if __name__ == "__main__":
    app()
