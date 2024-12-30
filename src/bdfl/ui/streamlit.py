import streamlit as st
import pandas as pd

def find_top_n_spikes(df, value_col='value', group_col='slug', n_steps=7, top_n=5):
    # Sort and calculate deltas
    df = df.sort_values(by=[group_col, 'date'])
    delta_col = f'delta_{n_steps}'
    df[delta_col] = df.groupby(group_col)[value_col].diff(n_steps)
    

    # Get top n spikes
    top_spikes = df.nlargest(top_n * 100, delta_col)
    
    # Add the starting values and dates for each spike
    results = []
    for _, row in top_spikes.iterrows():
        start_idx = row.name - n_steps if row.name - n_steps >= 0 else 0
        results.append({
            'player': row[
                'player_name'
            ],
            'rise': row[delta_col],
            'start_date': df.loc[start_idx, 'date'],
            'end_date': row['date'],
            'start_value': df.loc[start_idx, value_col],
            'end_value': row[value_col],
        })
    # remove duplicates by slug
    results = pd.DataFrame(results)
    results = results.sort_values('rise', ascending=False)
    results = results.drop_duplicates(subset=['player'], keep="first").reset_index(drop=True)
    return results.head(top_n)

def app():
    # App title
    st.title("Top Risers")

    # File uploader
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    if uploaded_file is None:
        uploaded_file = "data/published/ktc_value_histories_20240929-221650.csv"
    # Load data
    df = pd.read_csv(uploaded_file)

    # Parameters selection
    col1, col2, col3 = st.columns(3)

    with col1:
        n_steps = st.slider("Time period (days)", min_value=1, max_value=30, value=7)
    value_col = "value"
    top_n = 10
    # Calculate and display results
    results = find_top_n_spikes(df, value_col, 'slug', n_steps, top_n)

    # Format the results
    results['rise'] = results['rise'].round(2)
    results['start_value'] = results['start_value'].round(2)
    results['end_value'] = results['end_value'].round(2)

    st.dataframe(results)


if __name__ == "__main__":
    app()
