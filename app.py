import streamlit as st
import pandas as pd
import asyncio
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px
from scraper import get_headlines

# Configure the Streamlit page
st.set_page_config(page_title="FinSentiment Arb", page_icon="📈", layout="wide")

def apply_color(val):
    if val >= 0.05:
        return 'color: green'
    elif val <= -0.05:
        return 'color: red'
    else:
        return 'color: gray'

def main():
    st.title("📈 Financial News Sentiment Arbitrage")
    st.markdown("### Analyze real-time market sentiment to discover algorithmic arbitrage opportunities.")
    
    st.sidebar.header("Configuration")
    ticker = st.sidebar.text_input("Enter Stock Ticker:", value="NVDA").upper()
    analyze_button = st.sidebar.button("Run Sentiment Analysis")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**How it works:**")
    st.sidebar.markdown("- Scrapes latest headlines asynchronously.")
    st.sidebar.markdown("- Applies NLP (VADER) to score sentiment.")
    st.sidebar.markdown("- Visualizes data for quant modeling.")
    
    if analyze_button:
        with st.spinner(f"Fetching asynchronous news and analyzing sentiment for {ticker}..."):
            # Fetch headlines using async scraper
            headlines = asyncio.run(get_headlines(ticker))
            
        if not headlines:
            st.error("No news found or an error occurred. Please check the ticker symbol and try again.")
        else:
            st.success(f"Successfully retrieved and analyzed {len(headlines)} recent headlines for {ticker}.")
            
            # Analyze Sentiment
            analyzer = SentimentIntensityAnalyzer()
            results = []
            
            for headline in headlines:
                scores = analyzer.polarity_scores(headline)
                results.append({
                    "Headline": headline,
                    "Compound Score": scores['compound'],
                    "Positive": scores['pos'],
                    "Neutral": scores['neu'],
                    "Negative": scores['neg']
                })
                
            df = pd.DataFrame(results)
            avg_score = df['Compound Score'].mean()
            
            # Determine Market Mood
            sentiment_label = "Neutral ⚖️"
            if avg_score >= 0.05:
                sentiment_label = "Bullish 🚀"
            elif avg_score <= -0.05:
                sentiment_label = "Bearish 📉"
                
            # Dashboard Metrics
            st.markdown("## Overview Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Average Compound Score", value=f"{avg_score:.3f}")
            col2.metric(label="Market Mood Signal", value=sentiment_label)
            col3.metric(label="Total Headlines Analyzed", value=len(headlines))
            
            st.markdown("---")
            
            # Visualizations
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("Sentiment Polarity Distribution")
                fig_hist = px.histogram(
                    df, x="Compound Score", nbins=20, 
                    color_discrete_sequence=['#4c78a8'],
                    labels={'Compound Score': 'Sentiment Score (-1 to 1)'}
                )
                fig_hist.update_layout(bargap=0.1)
                st.plotly_chart(fig_hist, use_container_width=True)
                
            with col_chart2:
                st.subheader("Sentiment Breakdown")
                pos_count = len(df[df['Compound Score'] >= 0.05])
                neg_count = len(df[df['Compound Score'] <= -0.05])
                neu_count = len(df[(df['Compound Score'] > -0.05) & (df['Compound Score'] < 0.05)])
                
                pie_df = pd.DataFrame({
                    'Sentiment': ['Positive', 'Negative', 'Neutral'],
                    'Count': [pos_count, neg_count, neu_count]
                })
                fig_pie = px.pie(pie_df, values='Count', names='Sentiment', 
                                 color='Sentiment',
                                 color_discrete_map={'Positive':'#2ca02c', 'Negative':'#d62728', 'Neutral':'#7f7f7f'})
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Raw Headline Data")
            styled_df = df.style.map(apply_color, subset=['Compound Score'])
            st.dataframe(styled_df, use_container_width=True, height=400)

if __name__ == "__main__":
    main()
