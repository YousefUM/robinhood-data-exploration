import streamlit as st
import pandas as pd
import plotly.express as px # Great for interactive plots
import numpy as np

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Robinhood Trading Analysis")

# --- Load Data ---
@st.cache_data # Cache the data loading to improve performance
def load_data():
    try:
        df = pd.read_csv('closed_positions.csv')
        df['sell_date'] = pd.to_datetime(df['sell_date'])
        # You might need to reload other dataframes as well:
        # monthly_pl_df = pd.read_csv('monthly_pl.csv')
        # monthly_pl_df['sell_date'] = pd.to_datetime(monthly_pl_df['sell_date'])
        # instrument_perf_df = pd.read_csv('instrument_performance.csv')
        return df#, monthly_pl_df, instrument_perf_df # Return all necessary DFs
    except FileNotFoundError:
        st.error("Error: Data files not found. Make sure 'closed_positions.csv' (and others) are in the same directory.")
        st.stop() # Stop the app if data is not found

closed_positions_df = load_data()

# --- Pre-calculate some necessary data for charts ---
# For Cumulative P/L
closed_positions_df_sorted = closed_positions_df.sort_values(by='sell_date')
closed_positions_df_sorted['cumulative_pl'] = closed_positions_df_sorted['realized_profit_loss'].cumsum()

# For Monthly Cumulative P/L
monthly_pl = closed_positions_df_sorted.set_index('sell_date').resample('ME')['realized_profit_loss'].sum().reset_index()
monthly_pl['cumulative_pl'] = monthly_pl['realized_profit_loss'].cumsum()

# For Instrument Performance
instrument_performance = closed_positions_df.groupby('instrument').agg(
    total_pl=('realized_profit_loss', 'sum'),
    num_trades=('instrument', 'count'),
    avg_holding_period=('holding_period_days', 'mean')
).reset_index()
top_10_profitable = instrument_performance.sort_values(by='total_pl', ascending=False).head(10)
bottom_10_losing = instrument_performance.sort_values(by='total_pl', ascending=True).head(10)


# --- App Layout ---
st.title("My Robinhood Trading Performance Analysis")

st.markdown("""
This interactive dashboard analyzes my personal trading history from Robinhood,
providing insights into overall profitability, instrument performance, and trading patterns.
""")

# --- Section 1: Overall Performance Metrics ---
st.header("Overall Performance Summary")
col1, col2, col3, col4 = st.columns(4)

total_realized_pl = closed_positions_df['realized_profit_loss'].sum()
col1.metric("Total Realized P/L", f"${total_realized_pl:,.2f}")

total_trades = len(closed_positions_df)
col2.metric("Total Closed Trades", total_trades)

profitable_trades_count = len(closed_positions_df[closed_positions_df['realized_profit_loss'] > 0])
win_rate = (profitable_trades_count / total_trades) * 100 if total_trades > 0 else 0
col3.metric("Win Rate", f"{win_rate:.2f}%")

avg_holding_period = closed_positions_df['holding_period_days'].mean()
col4.metric("Avg Holding Period", f"{avg_holding_period:.0f} days")


# --- Section 2: Cumulative P/L Over Time ---
st.header("Cumulative Profit/Loss Trend")

# Create an interactive Plotly chart for cumulative P/L
fig_cum_pl = px.line(closed_positions_df_sorted, x='sell_date', y='cumulative_pl',
                     title='Cumulative Realized Profit/Loss Over Time',
                     labels={'sell_date': 'Date', 'cumulative_pl': 'Cumulative P/L ($)'})
fig_cum_pl.add_trace(px.line(monthly_pl, x='sell_date', y='cumulative_pl').data[0].update(name='Monthly Cumulative P/L', mode='markers+lines', line=dict(dash='dash', color='orange')))
fig_cum_pl.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-Even", annotation_position="top left")
st.plotly_chart(fig_cum_pl, use_container_width=True)


# --- Section 3: Instrument Performance ---
st.header("Instrument Performance Breakdown")
col_inst1, col_inst2 = st.columns(2)

with col_inst1:
    st.subheader("Top 10 Most Profitable")
    fig_top_profitable = px.bar(top_10_profitable, x='total_pl', y='instrument', orientation='h',
                                title='Top 10 Most Profitable Instruments',
                                labels={'total_pl': 'Total Realized P/L ($)'})
    fig_top_profitable.update_layout(yaxis={'categoryorder':'total ascending'}) # Sort bars
    st.plotly_chart(fig_top_profitable, use_container_width=True)

with col_inst2:
    st.subheader("Top 10 Least Profitable")
    fig_bottom_losing = px.bar(bottom_10_losing, x='total_pl', y='instrument', orientation='h',
                               title='Top 10 Least Profitable Instruments',
                               labels={'total_pl': 'Total Realized P/L ($)'})
    fig_bottom_losing.update_layout(yaxis={'categoryorder':'total descending'}) # Sort bars
    st.plotly_chart(fig_bottom_losing, use_container_width=True)


# --- Section 4: Holding Period Analysis ---
st.header("Holding Period Analysis")

st.subheader("Distribution of All Holding Periods")
fig_holding_dist = px.histogram(closed_positions_df, x='holding_period_days', nbins=50,
                                 title='Distribution of Holding Periods (Days)',
                                 labels={'holding_period_days': 'Holding Period (Days)', 'count': 'Number of Trades'})
st.plotly_chart(fig_holding_dist, use_container_width=True)

st.subheader("Holding Period: Profitable vs. Losing Trades")
profitable_trades = closed_positions_df[closed_positions_df['realized_profit_loss'] > 0]
losing_trades = closed_positions_df[closed_positions_df['realized_profit_loss'] <= 0]

# Combine for Plotly Express
combined_holding = pd.concat([
    profitable_trades.assign(Trade_Outcome='Profitable'),
    losing_trades.assign(Trade_Outcome='Losing')
])

fig_holding_compare = px.histogram(combined_holding, x='holding_period_days', color='Trade_Outcome',
                                   histnorm='density', nbins=50,
                                   title='Holding Period Distribution: Profitable vs. Losing Trades',
                                   labels={'holding_period_days': 'Holding Period (Days)', 'density': 'Density'},
                                   barmode='overlay', opacity=0.7,
                                   color_discrete_map={'Profitable': 'green', 'Losing': 'red'})
st.plotly_chart(fig_holding_compare, use_container_width=True)

st.subheader("Distribution of Realized Profit/Loss per Trade")
fig_pl_dist = px.histogram(closed_positions_df, x='realized_profit_loss', nbins=50,
                           title='Distribution of Realized Profit/Loss per Trade',
                           labels={'realized_profit_loss': 'Realized Profit/Loss ($)', 'count': 'Number of Trades'})
st.plotly_chart(fig_pl_dist, use_container_width=True)
