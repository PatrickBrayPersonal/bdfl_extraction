import streamlit as st
import pandas as pd

def find_top_n_spikes(df, value_col='value', group_col='slug', n_steps=7, top_n=5):
    # Sort and calculate deltas
    df = df.sort_values(by=[group_col, 'date'])
    delta_col = f'delta_{n_steps}'
    df[delta_col] = df.groupby(group_col)[value_col].diff(n_steps)
    
    # Get top n spikes
    top_spikes = df.nlargest(top_n, delta_col)
    
    # Add the starting values and dates for each spike
    results = []
    for _, row in top_spikes.iterrows():
        start_idx = row.name - n_steps if row.name - n_steps >= 0 else 0
        results.append({
            'slug': row[group_col],
            'spike': row[delta_col],
            'start_date': df.loc[start_idx, 'date'],
            'end_date': row['date'],
            'start_value': df.loc[start_idx, value_col],
            'end_value': row[value_col],
            'percent_change': ((row[value_col] - df.loc[start_idx, value_col]) / 
                             df.loc[start_idx, value_col] * 100)
        })
    
    return pd.DataFrame(results)

# App title
st.title("Value Spike Analysis")

# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
if uploaded_file is None:
    uploaded_file = "data/processed/ktc_value_histories_20241229-122823.csv"
if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)
    
    # Display data info
    st.write(f"Number of unique slugs: {df.slug.nunique()}")
    
    # Parameters selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        n_steps = st.slider("Number of steps", min_value=1, max_value=30, value=7)
    
    with col2:
        top_n = st.slider("Number of top spikes", min_value=1, max_value=20, value=5)
    
    with col3:
        value_col = st.selectbox("Value column", df.columns, index=df.columns.get_loc('value') if 'value' in df.columns else 0)
    
    # Calculate and display results
    if st.button("Analyze Spikes"):
        results = find_top_n_spikes(df, value_col, 'slug', n_steps, top_n)
        
        # Format the results
        results['percent_change'] = results['percent_change'].round(2)
        results['spike'] = results['spike'].round(2)
        results['start_value'] = results['start_value'].round(2)
        results['end_value'] = results['end_value'].round(2)
        
        st.write("Top Value Spikes:")
        st.dataframe(results)