import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="IPL Analytics Dashboard (2008-2025)",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_path = "styles.css"
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Import project modules
from src.data_loader import load_or_process_data, TEAM_COLORS
from src.analytics import (
    get_batting_summary, get_bowling_summary, get_team_summary,
    get_team_season_summary, get_venue_summary, get_phase_summary, get_season_trends
)
from src.stats import (
    compute_descriptive_stats, compute_correlation_matrix,
    run_era_scoring_ttest, run_toss_impact_chisquare
)
from src.utils import apply_plotly_theme, render_kpi_card, COLOR_PALETTE

# Load data with Streamlit caching
@st.cache_data
def get_cached_data():
    return load_or_process_data()

matches_df, deliveries_df = get_cached_data()

# ==========================================
# SIDEBAR FILTERS
# ==========================================
st.sidebar.markdown("## 🏏 IPL Analytics Controls")
st.sidebar.markdown("---")

all_seasons = sorted(matches_df['season_year'].unique())
selected_years = st.sidebar.slider(
    "Select Season Range",
    min_value=int(min(all_seasons)),
    max_value=int(max(all_seasons)),
    value=(int(min(all_seasons)), int(max(all_seasons)))
)

all_teams = sorted(matches_df['team1'].dropna().unique())
selected_teams = st.sidebar.multiselect(
    "Filter Teams",
    options=all_teams,
    default=all_teams
)

min_balls_batted = st.sidebar.number_input("Min Balls Batted (Batting)", min_value=0, value=100, step=50)
min_balls_bowled = st.sidebar.number_input("Min Balls Bowled (Bowling)", min_value=0, value=100, step=50)

# Filter Dataframes based on selection
m_filtered = matches_df[
    (matches_df['season_year'] >= selected_years[0]) & 
    (matches_df['season_year'] <= selected_years[1]) &
    (matches_df['team1'].isin(selected_teams) | matches_df['team2'].isin(selected_teams))
].copy()

d_filtered = deliveries_df[
    (deliveries_df['season_year'] >= selected_years[0]) & 
    (deliveries_df['season_year'] <= selected_years[1]) &
    (deliveries_df['batting_team'].isin(selected_teams) | deliveries_df['bowling_team'].isin(selected_teams))
].copy()

st.sidebar.markdown("---")
st.sidebar.info(f"Filtered Dataset: **{len(m_filtered)}** matches & **{len(d_filtered):,}** deliveries")

# ==========================================
# HEADER
# ==========================================
st.title("🏏 IPL Player & Team Performance Analysis Dashboard")
st.caption(f"Exploratory, Statistical & Phase-wise Analytics Platform (Seasons {selected_years[0]} – {selected_years[1]})")

# Create Main Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📌 Overview",
    "🏏 Batting Analysis",
    "🎯 Bowling Analysis",
    "🛡️ Team Performance",
    "⚡ Match Phases & Venues",
    "🔬 Statistical Insights",
    "⚔️ Head-to-Head Comparator"
])

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW
# ==========================================
with tab1:
    st.markdown("### 📊 Executive Summary KPIs")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_matches_val = len(m_filtered)
    total_teams_val = len(selected_teams)
    total_runs_val = int(d_filtered['total_runs'].sum())
    total_wickets_val = int(d_filtered['is_bowler_wicket'].sum())
    total_sixes_val = int((d_filtered['batsman_runs'] == 6).sum())
    
    with col1:
        render_kpi_card("Matches Analyzed", f"{total_matches_val:,}", f"Seasons {selected_years[0]}-{selected_years[1]}", "🏟️")
    with col2:
        render_kpi_card("Active Teams", f"{total_teams_val}", "Franchises", "🛡️")
    with col3:
        render_kpi_card("Total Runs Scored", f"{total_runs_val:,}", f"Avg {(total_runs_val/total_matches_val if total_matches_val else 0):.0f}/match", "🏏")
    with col4:
        render_kpi_card("Wickets Taken", f"{total_wickets_val:,}", f"Avg {(total_wickets_val/total_matches_val if total_matches_val else 0):.1f}/match", "🎯")
    with col5:
        render_kpi_card("Sixes Hit", f"{total_sixes_val:,}", f"{(total_sixes_val/total_matches_val if total_matches_val else 0):.1f} sixes/match", "💥")
        
    st.markdown("---")
    
    col_left, col_right = st.columns([7, 5])
    
    with col_left:
        st.markdown("#### 📈 IPL Scoring Rate & 1st Innings Score Trend (2008 – 2025)")
        trends = get_season_trends(m_filtered, d_filtered)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trends['season_year'], y=trends['overall_run_rate'],
            name="Run Rate (runs/over)", mode='lines+markers',
            line=dict(color='#38BDF8', width=3), marker=dict(size=8)
        ))
        fig_trend.add_trace(go.Scatter(
            x=trends['season_year'], y=trends['avg_1st_inn_score'],
            name="Avg 1st Innings Score", mode='lines+markers', yaxis="y2",
            line=dict(color='#F43F5E', width=3, dash='dash'), marker=dict(size=8)
        ))
        fig_trend.update_layout(
            yaxis=dict(title=dict(text="Overall Run Rate (Runs/Over)", font=dict(color='#38BDF8'))),
            yaxis2=dict(title=dict(text="Avg 1st Innings Total", font=dict(color='#F43F5E')), overlaying="y", side="right"),
            hovermode="x unified", legend=dict(x=0.01, y=0.99)
        )
        apply_plotly_theme(fig_trend)
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_right:
        st.markdown("#### 🥧 Match Result Distribution")
        win_types = m_filtered['win_type'].value_counts().reset_index()
        win_types.columns = ['Result Type', 'Matches']
        fig_pie = px.pie(
            win_types, names='Result Type', values='Matches',
            hole=0.5, color_discrete_sequence=['#38BDF8', '#10B981', '#F59E0B', '#64748B']
        )
        apply_plotly_theme(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("#### 🏆 Top Teams by Win Percentage")
    t_summary = get_team_summary(m_filtered, d_filtered)
    fig_teams = px.bar(
        t_summary.head(10), x='win_pct', y='team', orientation='h',
        text='win_pct', color='win_pct',
        color_continuous_scale='Viridis', labels={'win_pct': 'Win %', 'team': 'Team'}
    )
    fig_teams.update_layout(yaxis=dict(autorange="reversed"))
    apply_plotly_theme(fig_teams)
    st.plotly_chart(fig_teams, use_container_width=True)

# ==========================================
# TAB 2: BATTING ANALYSIS
# ==========================================
with tab2:
    st.markdown("### 🏏 Batting Volume & Efficiency Metrics")
    bat_df = get_batting_summary(d_filtered, min_balls=min_balls_batted)
    
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        st.markdown("#### 🔝 Top 10 Run Scorers")
        fig_bat_runs = px.bar(
            bat_df.head(10), x='batsman', y='total_runs',
            color='strike_rate', text='total_runs',
            color_continuous_scale='Tealgrn',
            labels={'total_runs': 'Total Runs', 'batsman': 'Batsman', 'strike_rate': 'Strike Rate'}
        )
        apply_plotly_theme(fig_bat_runs)
        st.plotly_chart(fig_bat_runs, use_container_width=True)
        
    with col_b2:
        st.markdown("#### ⚡ Strike Rate vs Total Runs (Min Balls: {})".format(min_balls_batted))
        fig_sr = px.scatter(
            bat_df, x='total_runs', y='strike_rate',
            size='boundary_pct', color='batting_average',
            hover_name='batsman', hover_data=['fours', 'sixes', 'consistency_cv'],
            color_continuous_scale='Plasma',
            labels={'total_runs': 'Total Runs', 'strike_rate': 'Strike Rate (SR)', 'batting_average': 'Average'}
        )
        apply_plotly_theme(fig_sr)
        st.plotly_chart(fig_sr, use_container_width=True)
        
    st.markdown("#### 🔍 Player Deep Dive & Seasonal Breakdown")
    all_batsmen = bat_df['batsman'].tolist()
    if all_batsmen:
        selected_batter = st.selectbox("Select Batter for Detailed Inspection", options=all_batsmen)
        
        b_sub = d_filtered[d_filtered['batsman'] == selected_batter]
        b_year = b_sub.groupby('season_year').agg(
            runs=('batsman_runs', 'sum'),
            balls=('isWide', lambda s: s.isna().sum()),
            fours=('batsman_runs', lambda s: (s == 4).sum()),
            sixes=('batsman_runs', lambda s: (s == 6).sum())
        ).reset_index()
        b_year['strike_rate'] = (b_year['runs'] / b_year['balls'] * 100).round(2)
        
        c_yr1, c_yr2 = st.columns(2)
        with c_yr1:
            fig_b_yr_runs = px.bar(b_year, x='season_year', y='runs', text='runs', title=f"{selected_batter}: Runs by Season", color_discrete_sequence=['#38BDF8'])
            apply_plotly_theme(fig_b_yr_runs)
            st.plotly_chart(fig_b_yr_runs, use_container_width=True)
        with c_yr2:
            fig_b_yr_sr = px.line(b_year, x='season_year', y='strike_rate', markers=True, title=f"{selected_batter}: Strike Rate by Season", color_discrete_sequence=['#F43F5E'])
            apply_plotly_theme(fig_b_yr_sr)
            st.plotly_chart(fig_b_yr_sr, use_container_width=True)
            
    st.markdown("#### 📋 Batting Performance Leaderboard")
    st.dataframe(bat_df[['batsman', 'matches', 'innings', 'total_runs', 'balls', 'strike_rate', 'batting_average', 'fours', 'sixes', 'boundary_pct', 'consistency_cv']], use_container_width=True)

# ==========================================
# TAB 3: BOWLING ANALYSIS
# ==========================================
with tab3:
    st.markdown("### 🎯 Bowling Volume & Economy Metrics")
    bowl_df = get_bowling_summary(d_filtered, min_balls=min_balls_bowled)
    
    col_w1, col_w2 = st.columns(2)
    
    with col_w1:
        st.markdown("#### 🔝 Top 10 Wicket Takers")
        fig_bowl_w = px.bar(
            bowl_df.head(10), x='bowler', y='wickets',
            color='economy', text='wickets',
            color_continuous_scale='Purples_r',
            labels={'wickets': 'Wickets', 'bowler': 'Bowler', 'economy': 'Economy'}
        )
        apply_plotly_theme(fig_bowl_w)
        st.plotly_chart(fig_bowl_w, use_container_width=True)
        
    with col_w2:
        st.markdown("#### 🎯 Economy Rate vs Wickets (Min Balls: {})".format(min_balls_bowled))
        fig_econ = px.scatter(
            bowl_df, x='wickets', y='economy',
            size='overs', color='dot_ball_pct',
            hover_name='bowler', hover_data=['runs_conceded', 'bowling_average'],
            color_continuous_scale='Viridis',
            labels={'wickets': 'Wickets', 'economy': 'Economy Rate', 'dot_ball_pct': 'Dot Ball %'}
        )
        apply_plotly_theme(fig_econ)
        st.plotly_chart(fig_econ, use_container_width=True)
        
    st.markdown("#### 🔍 Bowler Deep Dive & Seasonal Breakdown")
    all_bowlers = bowl_df['bowler'].tolist()
    if all_bowlers:
        selected_bowler = st.selectbox("Select Bowler for Detailed Inspection", options=all_bowlers)
        
        bw_sub = d_filtered[d_filtered['bowler'] == selected_bowler]
        bw_year = bw_sub.groupby('season_year').agg(
            wickets=('is_bowler_wicket', 'sum'),
            legal_balls=('is_legal', 'sum'),
            runs_conceded=('bowler_runs', 'sum')
        ).reset_index()
        bw_year['economy'] = (bw_year['runs_conceded'] / (bw_year['legal_balls'] / 6)).round(2)
        
        c_bw1, c_bw2 = st.columns(2)
        with c_bw1:
            fig_bw_yr_w = px.bar(bw_year, x='season_year', y='wickets', text='wickets', title=f"{selected_bowler}: Wickets by Season", color_discrete_sequence=['#10B981'])
            apply_plotly_theme(fig_bw_yr_w)
            st.plotly_chart(fig_bw_yr_w, use_container_width=True)
        with c_bw2:
            fig_bw_yr_ec = px.line(bw_year, x='season_year', y='economy', markers=True, title=f"{selected_bowler}: Economy Rate by Season", color_discrete_sequence=['#F59E0B'])
            apply_plotly_theme(fig_bw_yr_ec)
            st.plotly_chart(fig_bw_yr_ec, use_container_width=True)
            
    st.markdown("#### 📋 Bowling Performance Leaderboard")
    st.dataframe(bowl_df[['bowler', 'matches', 'overs', 'wickets', 'runs_conceded', 'economy', 'bowling_average', 'bowling_strike_rate', 'dot_balls', 'dot_ball_pct']], use_container_width=True)

# ==========================================
# TAB 4: TEAM PERFORMANCE
# ==========================================
with tab4:
    st.markdown("### 🛡️ Team Performance & Season Trends")
    team_df = get_team_summary(m_filtered, d_filtered)
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("#### 📊 Team Win % & Total Victories")
        fig_t_win = px.bar(
            team_df, x='team', y='win_pct',
            color='wins', text='wins',
            labels={'win_pct': 'Win %', 'team': 'Team', 'wins': 'Total Wins'},
            color_continuous_scale='Blues'
        )
        apply_plotly_theme(fig_t_win)
        st.plotly_chart(fig_t_win, use_container_width=True)
        
    with col_t2:
        st.markdown("#### 🏏 Batting 1st vs Chasing Wins per Team")
        team_split = pd.melt(team_df, id_vars=['team'], value_vars=['wins_batting_1st', 'wins_chasing'], var_name='Strategy', value_name='Wins')
        team_split['Strategy'] = team_split['Strategy'].map({'wins_batting_1st': 'Batting 1st', 'wins_chasing': 'Chasing'})
        fig_split = px.bar(team_split, x='team', y='Wins', color='Strategy', barmode='group', color_discrete_sequence=['#38BDF8', '#10B981'])
        apply_plotly_theme(fig_split)
        st.plotly_chart(fig_split, use_container_width=True)
        
    st.markdown("#### 🗓️ Season-by-Season Team Win % Matrix")
    ts_df = get_team_season_summary(m_filtered)
    pivot_ts = ts_df.pivot(index='team', columns='season', values='win_pct')
    fig_heat = px.imshow(
        pivot_ts, labels=dict(x="Season", y="Team", color="Win %"),
        x=pivot_ts.columns, y=pivot_ts.index, color_continuous_scale='YlGnBu'
    )
    apply_plotly_theme(fig_heat)
    st.plotly_chart(fig_heat, use_container_width=True)

# ==========================================
# TAB 5: MATCH PHASES & VENUES
# ==========================================
with tab5:
    st.markdown("### ⚡ Strategic Analysis: Phase of Play & Venues")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("#### ⏱️ Phase of Play Run Rate & Boundary %")
        p_df = get_phase_summary(d_filtered)
        fig_phase = px.bar(
            p_df, x='phase', y='run_rate',
            color='boundary_pct', text='run_rate',
            color_continuous_scale='Magma',
            labels={'run_rate': 'Run Rate (runs/over)', 'phase': 'Phase', 'boundary_pct': 'Boundary %'}
        )
        apply_plotly_theme(fig_phase)
        st.plotly_chart(fig_phase, use_container_width=True)
        
    with col_p2:
        st.markdown("#### 🎯 Wickets & Dot Ball % by Phase")
        fig_phase_w = px.bar(
            p_df, x='phase', y='wickets',
            color='dot_ball_pct', text='wickets',
            color_continuous_scale='Cividis',
            labels={'wickets': 'Wickets Lost', 'phase': 'Phase', 'dot_ball_pct': 'Dot Ball %'}
        )
        apply_plotly_theme(fig_phase_w)
        st.plotly_chart(fig_phase_w, use_container_width=True)
        
    st.markdown("---")
    st.markdown("#### 🏟️ Venue Scoring Patterns & Chasing Advantage")
    v_df = get_venue_summary(m_filtered, d_filtered)
    
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        st.markdown("##### Top Venues by Average 1st Innings Score")
        fig_v_score = px.bar(
            v_df.head(12), x='venue_clean', y='avg_1st_inn_score',
            color='avg_1st_inn_score', text='avg_1st_inn_score',
            color_continuous_scale='Reds',
            labels={'avg_1st_inn_score': 'Avg 1st Inn Score', 'venue_clean': 'Venue'}
        )
        apply_plotly_theme(fig_v_score)
        st.plotly_chart(fig_v_score, use_container_width=True)
        
    with col_v2:
        st.markdown("##### Top Venues by Chasing Win %")
        fig_v_chase = px.bar(
            v_df.head(12), x='venue_clean', y='chasing_win_pct',
            color='chasing_win_pct', text='chasing_win_pct',
            color_continuous_scale='Greens',
            labels={'chasing_win_pct': 'Chasing Win %', 'venue_clean': 'Venue'}
        )
        apply_plotly_theme(fig_v_chase)
        st.plotly_chart(fig_v_chase, use_container_width=True)

# ==========================================
# TAB 6: STATISTICAL INSIGHTS & HYPOTHESIS TESTS
# ==========================================
with tab6:
    st.markdown("### 🔬 Statistical Analysis & Academic Hypothesis Testing")
    
    st.markdown("#### 📋 1. Descriptive Summary Statistics")
    bat_all = get_batting_summary(d_filtered, min_balls=50)
    bowl_all = get_bowling_summary(d_filtered, min_balls=50)
    
    desc_bat = compute_descriptive_stats(bat_all, ['total_runs', 'strike_rate', 'batting_average', 'consistency_cv'])
    st.write("**Batting Metrics Summary (Min 50 Balls):**")
    st.dataframe(desc_bat, use_container_width=True)
    
    desc_bowl = compute_descriptive_stats(bowl_all, ['wickets', 'economy', 'bowling_average', 'dot_ball_pct'])
    st.write("**Bowling Metrics Summary (Min 50 Balls):**")
    st.dataframe(desc_bowl, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 🧪 2. Inferential Hypothesis Tests")
    
    c_ht1, c_ht2 = st.columns(2)
    
    with c_ht1:
        st.markdown("##### Test 1: Welch's Two-Sample t-test")
        st.caption("Comparing 1st Innings Scores: Early Era (2008–2016) vs Modern Era (2017–2025)")
        ttest_res = run_era_scoring_ttest(d_filtered)
        
        st.write(f"• **Early Era Mean Score:** {ttest_res['early_era_mean']} runs (N={ttest_res['early_era_n']})")
        st.write(f"• **Modern Era Mean Score:** {ttest_res['modern_era_mean']} runs (N={ttest_res['modern_era_n']})")
        st.write(f"• **Mean Difference:** +{ttest_res['mean_diff']} runs")
        st.write(f"• **t-statistic:** {ttest_res['t_statistic']}")
        st.write(f"• **p-value:** `{ttest_res['p_value']:.4e}`")
        st.write(f"• **Cohen's d Effect Size:** {ttest_res['cohen_d']}")
        st.success(f"**Conclusion:** {ttest_res['conclusion']}")
        
    with c_ht2:
        st.markdown("##### Test 2: Chi-Square Test of Independence")
        st.caption("Testing Relationship Between Toss Winner & Match Winner")
        chi_res = run_toss_impact_chisquare(m_filtered)
        
        st.write(f"• **Total Matches Analyzed:** {chi_res['total_matches']}")
        st.write(f"• **Toss & Match Wins:** {chi_res['toss_and_match_wins']} matches")
        st.write(f"• **Toss Win Conversion Rate:** {chi_res['toss_win_conversion_pct']}%")
        st.write(f"• **Chi-Square Stat:** {chi_res['chi2_statistic']}")
        st.write(f"• **p-value:** `{chi_res['p_value']:.4f}`")
        st.write(f"• **Cramer's V:** {chi_res['cramers_v']}")
        st.info(f"**Conclusion:** {chi_res['conclusion']}")

# ==========================================
# TAB 7: PLAYER COMPARATOR
# ==========================================
with tab7:
    st.markdown("### ⚔️ Player Head-to-Head Comparator")
    
    comp_mode = st.radio("Select Comparison Category", ["Batting Comparison", "Bowling Comparison"], horizontal=True)
    
    if comp_mode == "Batting Comparison":
        bat_comp_df = get_batting_summary(d_filtered, min_balls=50)
        p_list = bat_comp_df['batsman'].tolist()
        
        if len(p_list) >= 2:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                player1 = st.selectbox("Select Player 1", options=p_list, index=0)
            with col_p2:
                player2 = st.selectbox("Select Player 2", options=p_list, index=1 if len(p_list) > 1 else 0)
                
            p1_stats = bat_comp_df[bat_comp_df['batsman'] == player1].iloc[0]
            p2_stats = bat_comp_df[bat_comp_df['batsman'] == player2].iloc[0]
            
            c_card1, c_card2 = st.columns(2)
            with c_card1:
                st.markdown(f"#### 🏏 {player1}")
                st.write(f"• **Total Runs:** {p1_stats['total_runs']}")
                st.write(f"• **Strike Rate:** {p1_stats['strike_rate']}")
                st.write(f"• **Average:** {p1_stats['batting_average']}")
                st.write(f"• **Boundaries (4s / 6s):** {p1_stats['fours']} / {p1_stats['sixes']}")
                st.write(f"• **Boundary %:** {p1_stats['boundary_pct']}%")
                
            with c_card2:
                st.markdown(f"#### 🏏 {player2}")
                st.write(f"• **Total Runs:** {p2_stats['total_runs']}")
                st.write(f"• **Strike Rate:** {p2_stats['strike_rate']}")
                st.write(f"• **Average:** {p2_stats['batting_average']}")
                st.write(f"• **Boundaries (4s / 6s):** {p2_stats['fours']} / {p2_stats['sixes']}")
                st.write(f"• **Boundary %:** {p2_stats['boundary_pct']}%")
                
            # Radar chart
            categories = ['Total Runs (rel)', 'Strike Rate', 'Average', 'Boundary %', 'Consistency (100-CV)']
            
            # Normalize for radar comparison
            max_runs = max(p1_stats['total_runs'], p2_stats['total_runs'], 1)
            v1 = [p1_stats['total_runs']/max_runs*100, min(p1_stats['strike_rate'], 200)/2, min(p1_stats['batting_average'], 60)/60*100, p1_stats['boundary_pct'], max(0, 100-(p1_stats['consistency_cv'] if pd.notna(p1_stats['consistency_cv']) else 50))]
            v2 = [p2_stats['total_runs']/max_runs*100, min(p2_stats['strike_rate'], 200)/2, min(p2_stats['batting_average'], 60)/60*100, p2_stats['boundary_pct'], max(0, 100-(p2_stats['consistency_cv'] if pd.notna(p2_stats['consistency_cv']) else 50))]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=v1, theta=categories, fill='toself', name=player1, line_color='#38BDF8'))
            fig_radar.add_trace(go.Scatterpolar(r=v2, theta=categories, fill='toself', name=player2, line_color='#F43F5E'))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
            apply_plotly_theme(fig_radar)
            st.plotly_chart(fig_radar, use_container_width=True)
            
    else:
        bowl_comp_df = get_bowling_summary(d_filtered, min_balls=50)
        bw_list = bowl_comp_df['bowler'].tolist()
        
        if len(bw_list) >= 2:
            col_bw1, col_bw2 = st.columns(2)
            with col_bw1:
                bowler1 = st.selectbox("Select Bowler 1", options=bw_list, index=0)
            with col_bw2:
                bowler2 = st.selectbox("Select Bowler 2", options=bw_list, index=1 if len(bw_list) > 1 else 0)
                
            bw1_stats = bowl_comp_df[bowl_comp_df['bowler'] == bowler1].iloc[0]
            bw2_stats = bowl_comp_df[bowl_comp_df['bowler'] == bowler2].iloc[0]
            
            c_bw_card1, c_bw_card2 = st.columns(2)
            with c_bw_card1:
                st.markdown(f"#### 🎯 {bowler1}")
                st.write(f"• **Wickets:** {bw1_stats['wickets']}")
                st.write(f"• **Economy:** {bw1_stats['economy']}")
                st.write(f"• **Average:** {bw1_stats['bowling_average']}")
                st.write(f"• **Dot Ball %:** {bw1_stats['dot_ball_pct']}%")
                
            with c_bw_card2:
                st.markdown(f"#### 🎯 {bowler2}")
                st.write(f"• **Wickets:** {bw2_stats['wickets']}")
                st.write(f"• **Economy:** {bw2_stats['economy']}")
                st.write(f"• **Average:** {bw2_stats['bowling_average']}")
                st.write(f"• **Dot Ball %:** {bw2_stats['dot_ball_pct']}%")
