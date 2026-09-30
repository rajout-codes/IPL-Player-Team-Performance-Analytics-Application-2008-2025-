import numpy as np
import pandas as pd
from scipy import stats

def compute_descriptive_stats(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Computes descriptive summary statistics (mean, median, std, quartiles, IQR, skewness)."""
    results = []
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            s = df[col].dropna()
            q25 = s.quantile(0.25)
            q75 = s.quantile(0.75)
            results.append({
                'Metric': col,
                'Count': len(s),
                'Mean': round(s.mean(), 2),
                'Std Dev': round(s.std(), 2),
                'Median': round(s.median(), 2),
                'IQR': round(q75 - q25, 2),
                'Min': round(s.min(), 2),
                '25%': round(q25, 2),
                '75%': round(q75, 2),
                'Max': round(s.max(), 2),
                'Skewness': round(s.skew(), 2)
            })
    return pd.DataFrame(results)

def compute_correlation_matrix(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Computes Pearson & Spearman correlation coefficients among key metrics."""
    sub_df = df[columns].dropna()
    return sub_df.corr().round(3)

def run_era_scoring_ttest(deliveries_df: pd.DataFrame) -> dict:
    """
    Hypothesis Test 1: Welch's t-test comparing 1st Innings Scores 
    between Early IPL Era (2008-2016) vs Modern IPL Era (2017-2025).
    """
    inn1_df = deliveries_df[deliveries_df['inning'] == 1].groupby(['matchId', 'season_year'])['total_runs'].sum().reset_index()
    
    early_scores = inn1_df[inn1_df['season_year'] <= 2016]['total_runs'].dropna()
    modern_scores = inn1_df[inn1_df['season_year'] >= 2017]['total_runs'].dropna()
    
    t_stat, p_val = stats.ttest_ind(modern_scores, early_scores, equal_var=False)
    
    # Cohen's d effect size
    n1, n2 = len(modern_scores), len(early_scores)
    s1, s2 = modern_scores.std(), early_scores.std()
    s_pooled = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    cohen_d = (modern_scores.mean() - early_scores.mean()) / s_pooled
    
    alpha = 0.05
    reject_null = p_val < alpha
    
    return {
        'test_name': "Welch's Two-Sample t-test (1st Innings Scores: Modern vs Early Era)",
        'early_era_mean': round(early_scores.mean(), 2),
        'early_era_std': round(early_scores.std(), 2),
        'early_era_n': len(early_scores),
        'modern_era_mean': round(modern_scores.mean(), 2),
        'modern_era_std': round(modern_scores.std(), 2),
        'modern_era_n': len(modern_scores),
        'mean_diff': round(modern_scores.mean() - early_scores.mean(), 2),
        't_statistic': round(t_stat, 4),
        'p_value': p_val,
        'cohen_d': round(cohen_d, 3),
        'alpha': alpha,
        'reject_null': reject_null,
        'conclusion': (
            f"Reject Null Hypothesis (p={p_val:.4e} < 0.05). "
            f"1st Innings scores in Modern Era ({modern_scores.mean():.1f}) are statistically significantly higher "
            f"than Early Era ({early_scores.mean():.1f}) with Cohen's d effect size of {cohen_d:.2f}."
            if reject_null else
            "Fail to reject Null Hypothesis. No statistically significant difference in scoring rates between eras."
        )
    }

def run_toss_impact_chisquare(matches_df: pd.DataFrame) -> dict:
    """
    Hypothesis Test 2: Chi-Square Test of Independence 
    between Winning the Toss and Winning the Match.
    """
    valid_m = matches_df[matches_df['winner'].notna()].copy()
    contingency_table = pd.crosstab(valid_m['toss_winner'] == valid_m['winner'], columns='Count')
    
    # 2x2 contingency: [Toss Winner Lost Match, Toss Winner Won Match]
    toss_won = (valid_m['toss_winner'] == valid_m['winner']).sum()
    toss_lost = len(valid_m) - toss_won
    
    chi2, p_val, dof, ex = stats.chi2_contingency([[toss_won, toss_lost]])
    
    cramers_v = np.sqrt(chi2 / len(valid_m))
    alpha = 0.05
    reject_null = p_val < alpha
    
    return {
        'test_name': "Chi-Square Test of Independence (Toss Win vs Match Win)",
        'total_matches': len(valid_m),
        'toss_and_match_wins': toss_won,
        'toss_win_match_loss': toss_lost,
        'toss_win_conversion_pct': round((toss_won / len(valid_m)) * 100, 2),
        'chi2_statistic': round(chi2, 4),
        'p_value': p_val,
        'degrees_of_freedom': dof,
        'cramers_v': round(cramers_v, 4),
        'alpha': alpha,
        'reject_null': reject_null,
        'conclusion': (
            f"Winning the toss gives a win rate of {toss_won/len(valid_m)*100:.1f}%. "
            f"Chi-square p-value is {p_val:.4f}. " + 
            ("Winning toss provides statistically significant advantage." if reject_null else "Winning toss does not provide a statistically significant overall advantage.")
        )
    }
