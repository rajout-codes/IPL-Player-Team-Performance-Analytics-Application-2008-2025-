import os
import pandas as pd
import numpy as np

# Canonical Team Name Standardizations
TEAM_MAPPING = {
    'Rising Pune Supergiants': 'Rising Pune Supergiant',
    'Delhi Daredevils': 'Delhi Capitals',
    'Kings XI Punjab': 'Punjab Kings',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru'
}

# Team Colors for Charts & UI Cards
TEAM_COLORS = {
    'Chennai Super Kings': '#FCCA06',
    'Mumbai Indians': '#004BA0',
    'Royal Challengers Bengaluru': '#EC1C24',
    'Kolkata Knight Riders': '#3A225D',
    'Delhi Capitals': '#00008B',
    'Punjab Kings': '#DD1F2D',
    'Rajasthan Royals': '#EA1A85',
    'Sunrisers Hyderabad': '#F26522',
    'Gujarat Titans': '#1B2133',
    'Lucknow Super Giants': '#0057B8',
    'Deccan Chargers': '#43525A',
    'Rising Pune Supergiant': '#D11D49',
    'Gujarat Lions': '#E04F16',
    'Pune Warriors': '#2F9BE3',
    'Kochi Tuskers Kerala': '#632B74'
}

# Venue Standardizations
VENUE_MAPPING = {
    'Eden Gardens, Kolkata': 'Eden Gardens',
    'Wankhede Stadium, Mumbai': 'Wankhede Stadium',
    'M Chinnaswamy Stadium, Bengaluru': 'M Chinnaswamy Stadium',
    'M. Chinnaswamy Stadium': 'M Chinnaswamy Stadium',
    'Feroz Shah Kotla': 'Arun Jaitley Stadium',
    'Feroz Shah Kotla, Delhi': 'Arun Jaitley Stadium',
    'Arun Jaitley Stadium, Delhi': 'Arun Jaitley Stadium',
    'MA Chidambaram Stadium, Chepauk': 'MA Chidambaram Stadium',
    'MA Chidambaram Stadium, Chepauk, Chennai': 'MA Chidambaram Stadium',
    'MA Chidambaram Stadium, Chennai': 'MA Chidambaram Stadium',
    'Rajiv Gandhi International Stadium, Uppal': 'Rajiv Gandhi International Stadium',
    'Rajiv Gandhi International Stadium, Uppal, Hyderabad': 'Rajiv Gandhi International Stadium',
    'Punjab Cricket Association Stadium, Mohali': 'PCA Stadium, Mohali',
    'Punjab Cricket Association IS Bindra Stadium, Mohali': 'PCA Stadium, Mohali',
    'Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh': 'PCA Stadium, Mohali',
    'Narendra Modi Stadium, Ahmedabad': 'Narendra Modi Stadium',
    'Sardar Patel Stadium, Motera': 'Narendra Modi Stadium',
    'Brabourne Stadium, Mumbai': 'Brabourne Stadium',
    'Dr DY Patil Sports Academy, Mumbai': 'Dr DY Patil Sports Academy',
    'Maharashtra Cricket Association Stadium, Pune': 'Maharashtra Cricket Association Stadium',
    'Subrata Roy Sahara Stadium': 'Maharashtra Cricket Association Stadium',
    'Sawai Mansingh Stadium, Jaipur': 'Sawai Mansingh Stadium',
    'Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow': 'Ekana Cricket Stadium, Lucknow'
}

BOWLER_WICKET_KINDS = [
    'caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket'
]

def clean_matches_data(matches_path: str) -> pd.DataFrame:
    """Loads and cleans matches dataset."""
    df = pd.read_csv(matches_path)
    
    # Parse canonical season year
    df['season_year'] = pd.to_datetime(df['date']).dt.year
    
    # Standardize Team Names
    for col in ['team1', 'team2', 'winner', 'toss_winner']:
        if col in df.columns:
            df[col] = df[col].replace(TEAM_MAPPING)
            
    # Standardize Venues
    df['venue_clean'] = df['venue'].replace(VENUE_MAPPING)
    
    # Win type classification
    def get_win_type(row):
        if pd.notna(row['winner_runs']) and row['winner_runs'] > 0:
            return 'Batting 1st'
        elif pd.notna(row['winner_wickets']) and row['winner_wickets'] > 0:
            return 'Chasing'
        elif pd.notna(row['eliminator']) and str(row['eliminator']).strip() not in ['', 'nan', 'NaN']:
            return 'Tie / Super Over'
        return 'No Result / Other'
        
    df['win_type'] = df.apply(get_win_type, axis=1)
    df['toss_match_winner_same'] = df['toss_winner'] == df['winner']
    
    return df

def clean_deliveries_data(deliveries_path: str, matches_df: pd.DataFrame) -> pd.DataFrame:
    """Loads and cleans ball-by-ball deliveries dataset, enriched with match metadata."""
    df = pd.read_csv(deliveries_path)
    
    # Standardize Team Names
    df['batting_team'] = df['batting_team'].replace(TEAM_MAPPING)
    df['bowling_team'] = df['bowling_team'].replace(TEAM_MAPPING)
    
    # Runs calculation
    df['byes'] = df['Byes'].fillna(0)
    df['legbyes'] = df['LegByes'].fillna(0)
    df['penalty'] = df['Penalty'].fillna(0)
    df['total_runs'] = df['batsman_runs'] + df['extras']
    
    # Runs conceded by bowler (excludes byes, legbyes, penalty)
    df['bowler_runs'] = df['total_runs'] - (df['byes'] + df['legbyes'] + df['penalty'])
    
    # Legal balls (excludes wides and noballs)
    df['is_legal'] = df['isWide'].isna() & df['isNoBall'].isna()
    
    # Wickets credited to bowler
    df['is_bowler_wicket'] = df['dismissal_kind'].isin(BOWLER_WICKET_KINDS)
    df['is_any_wicket'] = df['dismissal_kind'].notna()
    
    # Phase of play calculation (over is 0-indexed: 0..19)
    def assign_phase(over):
        if over < 6:
            return 'Powerplay (1-6)'
        elif over < 15:
            return 'Middle Overs (7-15)'
        else:
            return 'Death Overs (16-20)'
            
    df['phase'] = df['over'].apply(assign_phase)
    
    # Merge essential match metadata
    match_meta = matches_df[['matchId', 'season_year', 'venue_clean', 'toss_winner', 'toss_decision', 'winner', 'win_type']]
    df = df.merge(match_meta, on='matchId', how='left')
    
    return df

def load_or_process_data(data_dir: str = "data", processed_dir: str = "processed_data"):
    """Loads datasets and caches cleaned files to processed_data folder."""
    os.makedirs(processed_dir, exist_ok=True)
    
    matches_clean_path = os.path.join(processed_dir, "matches_clean.csv")
    deliveries_clean_path = os.path.join(processed_dir, "deliveries_clean.csv")
    
    matches_raw = os.path.join(data_dir, "matches_updated_ipl_upto_2025.csv")
    deliveries_raw = os.path.join(data_dir, "deliveries_updated_ipl_upto_2025.csv")
    
    print("Processing raw datasets...")
    matches_df = clean_matches_data(matches_raw)
    deliveries_df = clean_deliveries_data(deliveries_raw, matches_df)
    
    matches_df.to_csv(matches_clean_path, index=False)
    deliveries_df.to_csv(deliveries_clean_path, index=False)
    print("Successfully cached cleaned datasets!")
    
    return matches_df, deliveries_df
