"""Streamlit application for analyzing fantasy football player value trends.

This module provides a web interface for identifying players with the biggest
value increases over specified time periods using KeepTradeCut data.
"""

from typing import Optional, Union

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

    Raises:
        KeyError: If required columns are missing from the DataFrame.
        ValueError: If n_steps or top_n are not positive integers.
    """
    logger.info(
        f"Finding top {top_n} spikes over {n_steps} steps using {value_col} column"
    )

    if n_steps <= 0 or top_n <= 0:
        raise ValueError("n_steps and top_n must be positive integers")

    required_cols = [group_col, "date", value_col, "player_name"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")

    # Sort and calculate deltas
    df_sorted = df.sort_values(by=[group_col, "date"]).copy()
    delta_col = f"delta_{n_steps}"
    df_sorted[delta_col] = df_sorted.groupby(group_col)[value_col].diff(n_steps)

    # Get top spikes (multiply by 100 to ensure we have enough data after filtering)
    top_spikes = df_sorted.nlargest(top_n * 100, delta_col)
    logger.debug(f"Found {len(top_spikes)} potential spikes before filtering")

    # Build results with starting values and dates for each spike
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
        except (KeyError, IndexError) as e:
            logger.warning(f"Skipping row due to missing data: {e}")
            continue

    if not results:
        logger.warning("No valid results found")
        return pd.DataFrame()

    # Remove duplicates by player and return top N
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("rise", ascending=False)
    results_df = results_df.drop_duplicates(
        subset=["player"], keep="first"
    ).reset_index(drop=True)

    final_results = results_df.head(top_n)
    logger.info(f"Returning {len(final_results)} top rising players")
    return final_results


def load_data(
    file_source: Union[str, st.runtime.uploaded_file_manager.UploadedFile],
) -> Optional[pd.DataFrame]:
    """Load CSV data from file upload or default file path.

    Args:
        file_source: Either an uploaded file object or string path to CSV file.

    Returns:
        DataFrame containing the loaded data, or None if loading fails.
    """
    try:
        df = pd.read_csv(file_source)
        logger.info(
            f"Successfully loaded data with {len(df)} rows and {len(df.columns)} columns"
        )
        return df
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        st.error(f"Error loading data: {e}")
        return None


def format_results(results: pd.DataFrame) -> pd.DataFrame:
    """Format numerical columns in results DataFrame for display.

    Args:
        results: DataFrame containing analysis results.

    Returns:
        DataFrame with formatted numerical values.
    """
    if results.empty:
        return results

    formatted_results = results.copy()
    numeric_cols = ["rise", "start_value", "end_value"]

    for col in numeric_cols:
        if col in formatted_results.columns:
            formatted_results[col] = formatted_results[col].round(2)

    logger.debug("Formatted numerical columns for display")
    return formatted_results


def app() -> None:
    """Main Streamlit application for fantasy football value analysis.

    Provides an interactive interface for uploading CSV files and analyzing
    player value trends over customizable time periods.
    """
    logger.info("Starting Streamlit app")

    # App configuration
    st.set_page_config(
        page_title="Fantasy Football Top Risers", page_icon="📈", layout="wide"
    )

    # App title and description
    st.title("📈 Fantasy Football Top Risers")
    st.markdown(
        "Upload a CSV file with player value data to identify the biggest risers "
        "over your specified time period."
    )

    # File upload section
    st.subheader("Data Upload")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Upload a CSV file containing player value history data",
    )

    # Use default file if none uploaded
    file_source = uploaded_file
    if uploaded_file is None:
        default_file = "data/published/ktc_value_histories_20240929-221650.csv"
        st.info(f"Using default file: {default_file}")
        file_source = default_file

    # Load and validate data
    df = load_data(file_source)
    if df is None:
        st.stop()

    # Display data info
    st.subheader("Data Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        if "player_name" in df.columns:
            st.metric("Unique Players", df["player_name"].nunique())

    # Analysis parameters
    st.subheader("Analysis Parameters")
    col1, col2 = st.columns(2)

    with col1:
        n_steps = st.slider(
            "Time period (days)",
            min_value=1,
            max_value=365,
            value=30,
            help="Number of days to look back for calculating value changes",
        )

    with col2:
        top_n = st.slider(
            "Number of top risers",
            min_value=1,
            max_value=50,
            value=10,
            help="Number of top rising players to display",
        )

    # Analysis and results
    st.subheader("Results")

    try:
        with st.spinner("Analyzing player value trends..."):
            results = find_top_n_spikes(
                df=df, value_col="value", group_col="slug", n_steps=n_steps, top_n=top_n
            )

        if results.empty:
            st.warning("No results found. Please check your data format.")
        else:
            # Format and display results
            formatted_results = format_results(results)
            st.dataframe(formatted_results, use_container_width=True, hide_index=True)

            # Download button for results
            csv_data = formatted_results.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv_data,
                file_name=f"top_risers_{n_steps}days.csv",
                mime="text/csv",
            )

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        st.error(f"Analysis failed: {e}")
        st.info(
            "Please ensure your CSV file has the required columns: date, player_name, value, slug"
        )


if __name__ == "__main__":
    app()
