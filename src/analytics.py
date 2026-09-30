import pandas as pd
import numpy as np

def get_batting_summary(deliveries_df: pd.DataFrame, min_balls: int = 0) -> pd.DataFrame:
    """Computes comprehensive batting stats for all batters."""
    # Filter legal balls for ball counts
    legal_df = deliveries_df[deliveries_df['isWide'].isna()].copy()
    
    # Inning-level runs per batter for highest score, 50s, 100s, CV
    inning_runs = deliveries_df.groupby(['matchId', 'inning', 'batsman'])['batsman_runs'].sum().reset_index()
    
    # Aggregations
    bat_stats = deliveries_df.groupby('batsman').agg(
        total_runs=('batsman_runs', 'sum'),
        fours=('batsman_runs', lambda s: (s == 4).sum()),
        sixes=('batsman_runs', lambda s: (s == 6).sum()),
        matches=('matchId', 'nunique')
    ).reset_index()
    
    # Add legal balls
    balls_cnt = legal_df.groupby('batsman').size().reset_index(name='balls')
    bat_stats = bat_stats.merge(balls_cnt, on='batsman', how='left').fillna({'balls': 0})
    
    # Add dismissals
    dismissals = deliveries_df[deliveries_df['player_dismissed'].notna()].groupby('player_dismissed').size().reset_index(name='dismissals')
    bat_stats = bat_stats.merge(dismissals, left_on='batsman', right_on='player_dismissed', how='left').fillna({'dismissals': 0})
    bat_stats.drop(columns=['player_dismissed'], inplace=True, errors='ignore')
    
    # Inning metrics
    inn_agg = inning_runs.groupby('batsman').agg(
        innings=('batsman_runs', 'count'),
        highest_score=('batsman_runs', 'max'),
        fifties=('batsman_runs', lambda s: ((s >= 50) & (s < 100)).sum()),
        hundreds=('batsman_runs', lambda s: (s >= 100).sum()),
        std_runs=('batsman_runs', 'std'),
        mean_runs=('batsman_runs', 'mean')
    ).reset_index()
    
    bat_stats = bat_stats.merge(inn_agg, on='batsman', how='left')
    
    # Derived metrics
    bat_stats['strike_rate'] = np.where(bat_stats['balls'] > 0, (bat_stats['total_runs'] / bat_stats['balls'] * 100).round(2), 0.0)
    bat_stats['batting_average'] = np.where(bat_stats['dismissals'] > 0, (bat_stats['total_runs'] / bat_stats['dismissals']).round(2), bat_stats['total_runs'].astype(float))
    bat_stats['boundary_runs'] = (bat_stats['fours'] * 4) + (bat_stats['sixes'] * 6)
    bat_stats['boundary_pct'] = np.where(bat_stats['total_runs'] > 0, (bat_stats['boundary_runs'] / bat_stats['total_runs'] * 100).round(2), 0.0)
    
    # Consistency Coefficient of Variation (CV = std / mean * 100)
    bat_stats['consistency_cv'] = np.where(bat_stats['mean_runs'] > 0, (bat_stats['std_runs'] / bat_stats['mean_runs'] * 100).round(2), np.nan)
    
    if min_balls > 0:
        bat_stats = bat_stats[bat_stats['balls'] >= min_balls]
        
    return bat_stats.sort_values(by='total_runs', ascending=False).reset_index(drop=True)

def get_bowling_summary(deliveries_df: pd.DataFrame, min_balls: int = 0) -> pd.DataFrame:
    """Computes comprehensive bowling stats for all bowlers."""
    # Aggregations
    bowl_stats = deliveries_df.groupby('bowler').agg(
        matches=('matchId', 'nunique'),
        legal_balls=('is_legal', 'sum'),
        runs_conceded=('bowler_runs', 'sum'),
        wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    
    # Dot balls (legal balls with 0 total runs)
    dot_df = deliveries_df[deliveries_df['is_legal'] & (deliveries_df['total_runs'] == 0)]
    dot_cnt = dot_df.groupby('bowler').size().reset_index(name='dot_balls')
    bowl_stats = bowl_stats.merge(dot_cnt, on='bowler', how='left').fillna({'dot_balls': 0})
    
    # Derived metrics
    bowl_stats['overs'] = (bowl_stats['legal_balls'] / 6).round(1)
    bowl_stats['economy'] = np.where(bowl_stats['legal_balls'] > 0, (bowl_stats['runs_conceded'] / (bowl_stats['legal_balls'] / 6)).round(2), 0.0)
    bowl_stats['bowling_average'] = np.where(bowl_stats['wickets'] > 0, (bowl_stats['runs_conceded'] / bowl_stats['wickets']).round(2), np.nan)
    bowl_stats['bowling_strike_rate'] = np.where(bowl_stats['wickets'] > 0, (bowl_stats['legal_balls'] / bowl_stats['wickets']).round(2), np.nan)
    bowl_stats['dot_ball_pct'] = np.where(bowl_stats['legal_balls'] > 0, (bowl_stats['dot_balls'] / bowl_stats['legal_balls'] * 100).round(2), 0.0)
    
    if min_balls > 0:
        bowl_stats = bowl_stats[bowl_stats['legal_balls'] >= min_balls]
        
    return bowl_stats.sort_values(by='wickets', ascending=False).reset_index(drop=True)

def get_team_summary(matches_df: pd.DataFrame, deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """Computes overall team performance stats."""
    # Matches played
    teams_t1 = matches_df[['team1', 'matchId']].rename(columns={'team1': 'team'})
    teams_t2 = matches_df[['team2', 'matchId']].rename(columns={'team2': 'team'})
    all_teams_matches = pd.concat([teams_t1, teams_t2])
    
    team_played = all_teams_matches.groupby('team')['matchId'].nunique().reset_index(name='matches')
    
    # Wins
    team_wins = matches_df[matches_df['winner'].notna()].groupby('winner')['matchId'].nunique().reset_index(name='wins').rename(columns={'winner': 'team'})
    
    team_stats = team_played.merge(team_wins, on='team', how='left').fillna({'wins': 0})
    team_stats['wins'] = team_stats['wins'].astype(int)
    team_stats['losses'] = team_stats['matches'] - team_stats['wins']
    team_stats['win_pct'] = (team_stats['wins'] / team_stats['matches'] * 100).round(2)
    
    # Batting 1st vs Chasing wins
    bat_1st_wins = matches_df[matches_df['win_type'] == 'Batting 1st'].groupby('winner')['matchId'].nunique().reset_index(name='wins_batting_1st').rename(columns={'winner': 'team'})
    chase_wins = matches_df[matches_df['win_type'] == 'Chasing'].groupby('winner')['matchId'].nunique().reset_index(name='wins_chasing').rename(columns={'winner': 'team'})
    
    team_stats = team_stats.merge(bat_1st_wins, on='team', how='left').merge(chase_wins, on='team', how='left').fillna(0)
    
    # Team runs & wickets from deliveries
    bat_runs = deliveries_df.groupby('batting_team')['total_runs'].sum().reset_index(name='total_runs_scored').rename(columns={'batting_team': 'team'})
    bowl_wickets = deliveries_df.groupby('bowling_team')['is_bowler_wicket'].sum().reset_index(name='total_wickets_taken').rename(columns={'bowling_team': 'team'})
    
    team_stats = team_stats.merge(bat_runs, on='team', how='left').merge(bowl_wickets, on='team', how='left').fillna(0)
    
    return team_stats.sort_values(by='wins', ascending=False).reset_index(drop=True)

def get_team_season_summary(matches_df: pd.DataFrame) -> pd.DataFrame:
    """Computes season-by-season performance for each team."""
    records = []
    seasons = sorted(matches_df['season_year'].unique())
    
    for yr in seasons:
        sub_m = matches_df[matches_df['season_year'] == yr]
        teams_t1 = sub_m[['team1', 'matchId']].rename(columns={'team1': 'team'})
        teams_t2 = sub_m[['team2', 'matchId']].rename(columns={'team2': 'team'})
        comb = pd.concat([teams_t1, teams_t2])
        
        matches_cnt = comb.groupby('team')['matchId'].nunique()
        wins_cnt = sub_m[sub_m['winner'].notna()].groupby('winner')['matchId'].nunique()
        
        for team, m_cnt in matches_cnt.items():
            w_cnt = wins_cnt.get(team, 0)
            l_cnt = m_cnt - w_cnt
            w_pct = round((w_cnt / m_cnt * 100), 2) if m_cnt > 0 else 0.0
            records.append({
                'season': yr,
                'team': team,
                'matches': m_cnt,
                'wins': w_cnt,
                'losses': l_cnt,
                'win_pct': w_pct
            })
            
    return pd.DataFrame(records)

def get_venue_summary(matches_df: pd.DataFrame, deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """Computes venue-level metrics (average scores, chasing win %, match counts)."""
    # Match count per venue
    v_stats = matches_df.groupby('venue_clean').agg(
        matches=('matchId', 'nunique'),
        chasing_wins=('win_type', lambda s: (s == 'Chasing').sum()),
        batting_1st_wins=('win_type', lambda s: (s == 'Batting 1st').sum())
    ).reset_index()
    
    v_stats['chasing_win_pct'] = np.where(v_stats['matches'] > 0, (v_stats['chasing_wins'] / v_stats['matches'] * 100).round(2), 0.0)
    
    # Calculate 1st and 2nd innings average totals per venue
    inn_totals = deliveries_df[deliveries_df['inning'].isin([1, 2])].groupby(['matchId', 'venue_clean', 'inning'])['total_runs'].sum().reset_index()
    avg_scores = inn_totals.groupby(['venue_clean', 'inning'])['total_runs'].mean().unstack().reset_index()
    avg_scores.columns = ['venue_clean', 'avg_1st_inn_score', 'avg_2nd_inn_score']
    
    v_stats = v_stats.merge(avg_scores, on='venue_clean', how='left')
    v_stats['avg_1st_inn_score'] = v_stats['avg_1st_inn_score'].round(1)
    v_stats['avg_2nd_inn_score'] = v_stats['avg_2nd_inn_score'].round(1)
    
    return v_stats.sort_values(by='matches', ascending=False).reset_index(drop=True)

def get_phase_summary(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """Computes overall statistics by phase of play (Powerplay, Middle Overs, Death Overs)."""
    phase_stats = deliveries_df.groupby('phase').agg(
        total_runs=('total_runs', 'sum'),
        batsman_runs=('batsman_runs', 'sum'),
        extras=('extras', 'sum'),
        legal_balls=('is_legal', 'sum'),
        wickets=('is_bowler_wicket', 'sum'),
        fours=('batsman_runs', lambda s: (s == 4).sum()),
        sixes=('batsman_runs', lambda s: (s == 6).sum())
    ).reset_index()
    
    # Dot balls in phase
    dot_df = deliveries_df[deliveries_df['is_legal'] & (deliveries_df['total_runs'] == 0)]
    dots = dot_df.groupby('phase').size().reset_index(name='dot_balls')
    phase_stats = phase_stats.merge(dots, on='phase', how='left').fillna({'dot_balls': 0})
    
    # Phase derived stats
    phase_stats['overs'] = (phase_stats['legal_balls'] / 6).round(1)
    phase_stats['run_rate'] = (phase_stats['total_runs'] / (phase_stats['legal_balls'] / 6)).round(2)
    phase_stats['dot_ball_pct'] = (phase_stats['dot_balls'] / phase_stats['legal_balls'] * 100).round(2)
    phase_stats['boundary_runs'] = (phase_stats['fours'] * 4) + (phase_stats['sixes'] * 6)
    phase_stats['boundary_pct'] = (phase_stats['boundary_runs'] / phase_stats['total_runs'] * 100).round(2)
    
    return phase_stats

def get_season_trends(matches_df: pd.DataFrame, deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """Computes yearly trends from 2008 to 2025."""
    yr_deliv = deliveries_df.groupby('season_year').agg(
        matches=('matchId', 'nunique'),
        total_runs=('total_runs', 'sum'),
        legal_balls=('is_legal', 'sum'),
        wickets=('is_bowler_wicket', 'sum'),
        fours=('batsman_runs', lambda s: (s == 4).sum()),
        sixes=('batsman_runs', lambda s: (s == 6).sum())
    ).reset_index()
    
    yr_deliv['overs'] = (yr_deliv['legal_balls'] / 6).round(1)
    yr_deliv['overall_run_rate'] = (yr_deliv['total_runs'] / (yr_deliv['legal_balls'] / 6)).round(2)
    yr_deliv['sixes_per_match'] = (yr_deliv['sixes'] / yr_deliv['matches']).round(1)
    yr_deliv['fours_per_match'] = (yr_deliv['fours'] / yr_deliv['matches']).round(1)
    
    # Average 1st innings score per season
    inn1 = deliveries_df[deliveries_df['inning'] == 1].groupby(['season_year', 'matchId'])['total_runs'].sum().reset_index()
    avg_inn1 = inn1.groupby('season_year')['total_runs'].mean().reset_index(name='avg_1st_inn_score')
    
    yr_deliv = yr_deliv.merge(avg_inn1, on='season_year', how='left')
    yr_deliv['avg_1st_inn_score'] = yr_deliv['avg_1st_inn_score'].round(1)
    
    return yr_deliv.sort_values(by='season_year').reset_index(drop=True)
