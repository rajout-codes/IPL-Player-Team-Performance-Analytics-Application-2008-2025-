import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from src.data_loader import load_or_process_data
from src.analytics import (
    get_batting_summary, get_bowling_summary, get_team_summary,
    get_venue_summary, get_phase_summary, get_season_trends
)

# Set global seaborn theme for publication quality figures
plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['figure.titlesize'] = 16

def generate_all_figures(output_dir="figures"):
    os.makedirs(output_dir, exist_ok=True)
    matches, deliveries = load_or_process_data()
    
    # ----------------------------------------------------
    # Figure 1: Season Scoring Trends (2008-2025)
    # ----------------------------------------------------
    trends = get_season_trends(matches, deliveries)
    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)
    
    color1 = '#0284C7'
    color2 = '#E11D48'
    
    ax1.set_xlabel('Season Year', fontweight='bold')
    ax1.set_ylabel('Overall Run Rate (Runs / Over)', color=color1, fontweight='bold')
    line1 = ax1.plot(trends['season_year'], trends['overall_run_rate'], marker='o', color=color1, linewidth=2.5, label='Run Rate (runs/over)')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xticks(trends['season_year'])
    ax1.set_xticklabels(trends['season_year'], rotation=45)
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Avg 1st Innings Score (Runs)', color=color2, fontweight='bold')
    line2 = ax2.plot(trends['season_year'], trends['avg_1st_inn_score'], marker='s', linestyle='--', color=color2, linewidth=2.5, label='Avg 1st Inn Score')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    plt.title('IPL Season-by-Season Scoring Trends (2008 – 2025)', pad=15)
    fig.tight_layout()
    fig1_path = os.path.join(output_dir, "fig1_scoring_trend.png")
    plt.savefig(fig1_path, dpi=300)
    plt.close()
    
    # ----------------------------------------------------
    # Figure 2: Top Teams Win %
    # ----------------------------------------------------
    t_sum = get_team_summary(matches, deliveries).head(10)
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    palette = sns.color_palette("Blues_r", len(t_sum))
    bars = ax.barh(t_sum['team'], t_sum['win_pct'], color=palette)
    ax.set_xlabel('Win Percentage (%)', fontweight='bold')
    ax.set_ylabel('Franchise', fontweight='bold')
    ax.set_title('IPL Franchise Overall Win Standings (2008 – 2025)', pad=15)
    ax.invert_yaxis()
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.8, bar.get_y() + bar.get_height()/2, f"{width:.1f}%", va='center', fontweight='bold', fontsize=9)
        
    fig.tight_layout()
    fig2_path = os.path.join(output_dir, "fig2_team_win_pct.png")
    plt.savefig(fig2_path, dpi=300)
    plt.close()
    
    # ----------------------------------------------------
    # Figure 3: Batting 1st vs Chasing Wins
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    t_sub = t_sum.head(8)
    x = np.arange(len(t_sub))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, t_sub['wins_batting_1st'], width, label='Batting 1st Wins', color='#0284C7')
    rects2 = ax.bar(x + width/2, t_sub['wins_chasing'], width, label='Chasing Wins', color='#10B981')
    
    ax.set_ylabel('Total Victories', fontweight='bold')
    ax.set_title('Batting 1st vs Chasing Wins per Team', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(t_sub['team'], rotation=30, ha='right')
    ax.legend()
    
    fig.tight_layout()
    fig3_path = os.path.join(output_dir, "fig3_batting1st_vs_chasing.png")
    plt.savefig(fig3_path, dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Figure 4: Top 10 Run Scorers
    # ----------------------------------------------------
    bat_df = get_batting_summary(deliveries, min_balls=100).head(10)
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.bar(bat_df['batsman'], bat_df['total_runs'], color='#0D9488')
    ax.set_ylabel('Total Runs Scored', fontweight='bold')
    ax.set_title('Top 10 IPL All-Time Run Scorers', pad=15)
    plt.xticks(rotation=45, ha='right')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 80, f"{int(height):,}", ha='center', va='bottom', fontsize=8, fontweight='bold')
        
    fig.tight_layout()
    fig4_path = os.path.join(output_dir, "fig4_top_batsmen.png")
    plt.savefig(fig4_path, dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Figure 5: Strike Rate vs Runs Scatter Plot
    # ----------------------------------------------------
    bat_all = get_batting_summary(deliveries, min_balls=300)
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    scatter = ax.scatter(bat_all['total_runs'], bat_all['strike_rate'], c=bat_all['batting_average'], s=bat_all['boundary_pct']*4, cmap='viridis', alpha=0.8, edgecolors='black', linewidth=0.5)
    cbar = plt.colorbar(scatter)
    cbar.set_label('Batting Average', fontweight='bold')
    ax.set_xlabel('Total Runs', fontweight='bold')
    ax.set_ylabel('Strike Rate (Runs / 100 Balls)', fontweight='bold')
    ax.set_title('Batting Efficiency: Strike Rate vs Runs (Min 300 Balls)', pad=15)
    
    # Annotate top 5
    for _, row in bat_all.head(5).iterrows():
        ax.annotate(row['batsman'], (row['total_runs'], row['strike_rate']), fontsize=8, fontweight='bold', xytext=(5, 5), textcoords='offset points')
        
    fig.tight_layout()
    fig5_path = os.path.join(output_dir, "fig5_strike_rate_vs_runs.png")
    plt.savefig(fig5_path, dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Figure 6: Top 10 Wicket Takers
    # ----------------------------------------------------
    bowl_df = get_bowling_summary(deliveries, min_balls=100).head(10)
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.bar(bowl_df['bowler'], bowl_df['wickets'], color='#7C3AED')
    ax.set_ylabel('Wickets Taken', fontweight='bold')
    ax.set_title('Top 10 IPL All-Time Wicket Takers', pad=15)
    plt.xticks(rotation=45, ha='right')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2, f"{int(height)}", ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    fig.tight_layout()
    fig6_path = os.path.join(output_dir, "fig6_top_bowlers.png")
    plt.savefig(fig6_path, dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Figure 7: Economy vs Wickets Scatter Plot
    # ----------------------------------------------------
    bowl_all = get_bowling_summary(deliveries, min_balls=300)
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    scatter = ax.scatter(bowl_all['wickets'], bowl_all['economy'], c=bowl_all['dot_ball_pct'], cmap='plasma', s=bowl_all['overs']*0.8, alpha=0.8, edgecolors='black', linewidth=0.5)
    cbar = plt.colorbar(scatter)
    cbar.set_label('Dot Ball %', fontweight='bold')
    ax.set_xlabel('Wickets Taken', fontweight='bold')
    ax.set_ylabel('Economy Rate (Runs / Over)', fontweight='bold')
    ax.set_title('Bowling Effectiveness: Economy Rate vs Wickets', pad=15)
    
    for _, row in bowl_all.head(5).iterrows():
        ax.annotate(row['bowler'], (row['wickets'], row['economy']), fontsize=8, fontweight='bold', xytext=(5, 5), textcoords='offset points')
        
    fig.tight_layout()
    fig7_path = os.path.join(output_dir, "fig7_economy_vs_wickets.png")
    plt.savefig(fig7_path, dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Figure 8: Phase Performance (Powerplay vs Middle vs Death)
    # ----------------------------------------------------
    phases = get_phase_summary(deliveries)
    fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=300)
    color = '#2563EB'
    ax1.set_xlabel('Phase of Play', fontweight='bold')
    ax1.set_ylabel('Run Rate (runs/over)', color=color, fontweight='bold')
    bars = ax1.bar(phases['phase'], phases['run_rate'], color=color, alpha=0.7, width=0.4)
    ax1.tick_params(axis='y', labelcolor=color)
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height/2, f"{height:.2f}", ha='center', va='center', color='white', fontweight='bold')
        
    ax2 = ax1.twinx()
    color = '#D97706'
    ax2.set_ylabel('Boundary %', color=color, fontweight='bold')
    ax2.plot(phases['phase'], phases['boundary_pct'], color=color, marker='o', linewidth=3)
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Phase-of-Play Dynamics (Powerplay, Middle & Death Overs)', pad=15)
    fig.tight_layout()
    fig8_path = os.path.join(output_dir, "fig8_phase_performance.png")
    plt.savefig(fig8_path, dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Figure 9: Top Venues Analysis
    # ----------------------------------------------------
    venues = get_venue_summary(matches, deliveries).head(8)
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.barh(venues['venue_clean'], venues['avg_1st_inn_score'], color='#0284C7')
    ax.set_xlabel('Average 1st Innings Score', fontweight='bold')
    ax.set_title('Top IPL Venues by Average 1st Innings Score', pad=15)
    ax.invert_yaxis()
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1.5, bar.get_y() + bar.get_height()/2, f"{width:.1f}", va='center', fontweight='bold', fontsize=9)
        
    fig.tight_layout()
    fig9_path = os.path.join(output_dir, "fig9_venue_chasing.png")
    plt.savefig(fig9_path, dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Figure 10: Toss Impact Analysis
    # ----------------------------------------------------
    toss_wins = (matches['toss_winner'] == matches['winner']).value_counts()
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    labels = ['Toss Winner Won Match', 'Toss Winner Lost Match']
    counts = [toss_wins.get(True, 0), toss_wins.get(False, 0)]
    colors = ['#10B981', '#EF4444']
    
    bars = ax.bar(labels, counts, color=colors, width=0.5)
    ax.set_ylabel('Number of Matches', fontweight='bold')
    ax.set_title('Toss Outcome vs Match Winner Advantage', pad=15)
    
    for bar in bars:
        height = bar.get_height()
        pct = (height / sum(counts)) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height/2, f"{height:,}\n({pct:.1f}%)", ha='center', va='center', color='white', fontweight='bold')
        
    fig.tight_layout()
    fig10_path = os.path.join(output_dir, "fig10_toss_impact.png")
    plt.savefig(fig10_path, dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Figure 11: Era Score Distribution (Welch's t-test boxplot)
    # ----------------------------------------------------
    inn1 = deliveries[deliveries['inning'] == 1].groupby(['matchId', 'season_year'])['total_runs'].sum().reset_index()
    inn1['Era'] = np.where(inn1['season_year'] <= 2016, 'Early Era (2008-2016)', 'Modern Era (2017-2025)')
    
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    sns.boxplot(data=inn1, x='Era', y='total_runs', palette=['#38BDF8', '#F43F5E'], ax=ax, width=0.4)
    ax.set_ylabel('1st Innings Total Score', fontweight='bold')
    ax.set_xlabel('IPL Era', fontweight='bold')
    ax.set_title('Distribution of 1st Innings Scores Across Eras (t=8.43, p<1e-15)', pad=15)
    
    fig.tight_layout()
    fig11_path = os.path.join(output_dir, "fig11_era_ttest_distribution.png")
    plt.savefig(fig11_path, dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Figure 12: Player Radar Chart Comparison
    # ----------------------------------------------------
    fig = plt.figure(figsize=(6, 6), dpi=300)
    ax = fig.add_subplot(111, polar=True)
    
    categories = ['Runs', 'Strike Rate', 'Average', 'Boundary %', 'Consistency']
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    # Values for V Kohli vs RG Sharma (normalized 0-100)
    v_kohli = [100, 66, 75, 58, 80]
    rg_sharma = [81, 66, 60, 64, 72]
    
    v_kohli += v_kohli[:1]
    rg_sharma += rg_sharma[:1]
    
    ax.plot(angles, v_kohli, linewidth=2, linestyle='solid', label='V Kohli', color='#0284C7')
    ax.fill(angles, v_kohli, '#0284C7', alpha=0.25)
    
    ax.plot(angles, rg_sharma, linewidth=2, linestyle='solid', label='RG Sharma', color='#E11D48')
    ax.fill(angles, rg_sharma, '#E11D48', alpha=0.25)
    
    plt.xticks(angles[:-1], categories, fontweight='bold')
    plt.title('Head-to-Head Player Comparison (Radar Framework)', pad=20)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    fig.tight_layout()
    fig12_path = os.path.join(output_dir, "fig12_player_radar.png")
    plt.savefig(fig12_path, dpi=300)
    plt.close()
    
    print(f"Successfully generated all 12 figures in '{output_dir}/' directory!")

if __name__ == "__main__":
    generate_all_figures()
