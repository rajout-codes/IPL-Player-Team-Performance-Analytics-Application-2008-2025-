# 🏏 IPL Player and Team Performance Analysis Using Python
## Academic & Technical Project Report (2008 – 2025)

---

## Executive Summary
This report presents an in-depth exploratory, statistical, and phase-wise analytical evaluation of the Indian Premier League (IPL) from its inaugural season in **2008 through the 2025 season**. Utilizing high-granularity ball-by-ball data comprising **1,169 matches** and **278,205 legal & extra deliveries**, this study examines franchise performance evolution, player batting efficiency, bowling economy, phase-specific tactical dynamics, and historical scoring trends.

Key metrics evaluated include:
- **Total IPL Matches Analyzed:** 1,169
- **Total Deliveries Processed:** 278,205
- **Total Runs Scored:** 374,283 runs (Average: 320.2 runs/match)
- **Total Wickets Taken:** 12,645 wickets (Average: 10.8 wickets/match)
- **Total Boundaries:** 32,113 Fours and 14,353 Sixes

---

## Chapter 1 — Introduction

### 1.1 Background
The Indian Premier League (IPL), established by the Board of Control for Cricket in India (BCCI) in 2008, has evolved into the world's premiere Twenty20 (T20) cricket tournament. Combining high-intensity athletic competition with modern sports data analytics, the IPL provides a vast, multi-dimensional dataset ideal for empirical performance research.

### 1.2 Motivation
Traditional sports analytics often relied solely on high-level match summaries (e.g., total runs, match winner). However, modern T20 analytics requires micro-level ball-by-ball analysis to examine phase of play efficiency, player consistency, tactical toss dynamics, and venue-specific scoring biases.

### 1.3 Problem Statement
Simple descriptive queries such as "most runs" or "most wins" fail to capture nuance. For instance:
- A batsman with high cumulative runs might exhibit a low strike rate or high consistency variation.
- A bowler with many wickets may concede runs at an unsustainable economy rate.
- Historical rule changes (e.g., Impact Player rule introduced in 2023) may have fundamentally altered scoring dynamics over time.

### 1.4 Research Objectives
1. **Team Performance:** Quantify franchise win percentages, batting 1st vs chasing success rates, and cross-season stability.
2. **Batting Framework:** Evaluate batsmen across scoring volume, efficiency (Strike Rate), boundary dependence, and consistency (Coefficient of Variation).
3. **Bowling Framework:** Analyze bowler efficiency through economy rate, dot-ball percentage, and phase-wise containment.
4. **Strategic & Phase Analysis:** Dissect over-by-over dynamics across Powerplay (Overs 1-6), Middle Overs (7-15), and Death Overs (16-20).
5. **Statistical Hypothesis Testing:** Formally test era-wise scoring escalation and toss outcome independence.

---

## Chapter 2 — Dataset Description

The analysis is built upon an updated, complete IPL ball-by-ball dataset (2008–2025):
- **`matches_updated_ipl_upto_2025.csv`**: Contains 1169 match metadata records including date, teams, winner, toss winner, toss decision, venue, winner runs, winner wickets, and player of the match.
- **`deliveries_updated_ipl_upto_2025.csv`**: Contains 278205 ball-by-ball records detailing over, ball, batter, bowler, batsman runs, extras, wide/no-ball indicators, dismissal types, and dismissed player names.

### Data Cleaning & Standardizations Applied:
1. **Franchise Name Normalization:** Standardized historical team name changes across 18 seasons:
   - `Delhi Daredevils` $ightarrow$ `Delhi Capitals`
   - `Kings XI Punjab` $ightarrow$ `Punjab Kings`
   - `Royal Challengers Bangalore` $ightarrow$ `Royal Challengers Bengaluru`
   - `Rising Pune Supergiants` $ightarrow$ `Rising Pune Supergiant`
2. **Venue Name Aggregation:** Grouped alternate stadium naming strings (e.g., merging `Wankhede Stadium, Mumbai` into `Wankhede Stadium`, `Eden Gardens, Kolkata` into `Eden Gardens`).
3. **Legal Delivery & Extras Calculation:** Strictly isolated legal balls (`isWide == NaN` and `isNoBall == NaN`) to compute accurate overs bowled, bowler economy rates, and strike rates.

---

## Chapter 3 — Methodology

```
               IPL Raw Data (Matches & Deliveries 2008-2025)
                                  │
                                  ▼
                   Data Cleaning & Normalization
            (Team remapping, Venue cleanup, Extras isolation)
                                  │
                                  ▼
                    Feature Engineering & Tagging
            (Legal balls, Bowler runs, Phase of Play classification)
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
Match & Team Analysis                             Player Performance Framework
(Win %, Batting 1st vs Chase)                    (Batting & Bowling Metrics)
         │                                                 │
         └────────────────────────┬────────────────────────┘
                                  ▼
                     Statistical Hypothesis Testing
                (Welch's t-test, Chi-Square, Descriptive Stats)
                                  │
                                  ▼
                     Streamlit Interactive Dashboard
```

---

## Chapter 4 — Team Performance Analysis

### 4.1 Overall Franchise Win Standings
The table below highlights top IPL teams by win percentage across all seasons (2008–2025):

| Team | Matches Played | Wins | Losses | Win % | Batting 1st Wins | Chasing Wins | Total Runs |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Mumbai Indians | 277 | 151 | 126 | 54.51% | 76 | 75 | 45,088 |
| Chennai Super Kings | 252 | 142 | 110 | 56.35% | 72 | 70 | 41,070 |
| Kolkata Knight Riders | 264 | 135 | 129 | 51.14% | 57 | 78 | 41,333 |
| Royal Challengers Bengaluru | 270 | 132 | 138 | 48.89% | 62 | 70 | 43,275 |
| Punjab Kings | 264 | 119 | 145 | 45.08% | 56 | 63 | 42,862 |
| Delhi Capitals | 267 | 118 | 149 | 44.19% | 47 | 71 | 41,696 |
| Rajasthan Royals | 235 | 114 | 121 | 48.51% | 45 | 69 | 37,361 |
| Sunrisers Hyderabad | 196 | 93 | 103 | 47.45% | 47 | 46 | 31,590 |
| Gujarat Titans | 60 | 37 | 23 | 61.67% | 15 | 22 | 10,649 |
| Lucknow Super Giants | 58 | 30 | 28 | 51.72% | 20 | 10 | 10,242 |

### 4.2 Batting First vs Chasing Analysis
Across 1169 matches:
- **Chasing Teams Won:** 615 matches (52.6%)
- **Batting 1st Teams Won:** 531 matches (45.4%)
- **Tied / Super Over Matches:** 15 matches

---

## Chapter 5 — Player Performance Analysis

### 5.1 Top Batting Performers (Min 100 Legal Balls)
The top run-scorers in IPL history combine high volume with strong strike rates:

| Player | Matches | Innings | Total Runs | Balls | Strike Rate | Batting Avg | 4s | 6s | Boundary % | CV (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| V Kohli | 259 | 261 | 8,671 | 6523 | 132.93 | 39.59 | 774 | 292 | 55.91% | 82.39% |
| RG Sharma | 266 | 267 | 7,048 | 5337 | 132.06 | 29.74 | 640 | 303 | 62.12% | 91.31% |
| S Dhawan | 221 | 222 | 6,769 | 5326 | 127.09 | 35.07 | 768 | 153 | 58.95% | 83.31% |
| DA Warner | 184 | 187 | 6,567 | 4702 | 139.66 | 40.04 | 663 | 236 | 61.95% | 82.83% |
| SK Raina | 200 | 201 | 5,536 | 4046 | 136.83 | 32.37 | 506 | 204 | 58.67% | 84.28% |
| MS Dhoni | 241 | 241 | 5,439 | 3957 | 137.45 | 38.3 | 375 | 264 | 56.7% | 79.88% |
| KL Rahul | 135 | 138 | 5,235 | 3848 | 136.04 | 45.52 | 453 | 208 | 58.45% | 78.7% |
| AB de Villiers | 170 | 172 | 5,181 | 3411 | 151.89 | 39.85 | 414 | 253 | 61.26% | 91.24% |
| AM Rahane | 183 | 183 | 5,032 | 4025 | 125.02 | 30.5 | 515 | 123 | 55.6% | 87.31% |
| CH Gayle | 141 | 145 | 4,997 | 3346 | 149.34 | 39.66 | 408 | 359 | 75.77% | 95.86% |

### 5.2 Top Bowling Performers (Min 100 Legal Balls)
Leading wicket-takers evaluated by economy rate and dot-ball percentage:

| Bowler | Matches | Overs | Wickets | Runs Conceded | Economy | Bowling Avg | Bowling SR | Dot Balls | Dot Ball % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| YS Chahal | 172 | 631.8 | 221 | 5,032 | 7.96 | 22.77 | 17.15 | 1266 | 33.39% |
| B Kumar | 190 | 703.7 | 198 | 5,412 | 7.69 | 27.33 | 21.32 | 1748 | 41.4% |
| SP Narine | 187 | 725.2 | 192 | 4,933 | 6.8 | 25.69 | 22.66 | 1653 | 37.99% |
| PP Chawla | 191 | 641.7 | 192 | 5,108 | 7.96 | 26.6 | 20.05 | 1325 | 34.42% |
| R Ashwin | 217 | 785.0 | 187 | 5,652 | 7.2 | 30.22 | 25.19 | 1606 | 34.1% |
| JJ Bumrah | 145 | 559.8 | 186 | 4,059 | 7.25 | 21.82 | 18.06 | 1353 | 40.28% |
| DJ Bravo | 158 | 520.0 | 183 | 4,360 | 8.38 | 23.83 | 17.05 | 998 | 31.99% |
| A Mishra | 162 | 561.8 | 174 | 4,145 | 7.38 | 23.82 | 19.37 | 1185 | 35.15% |
| RA Jadeja | 225 | 676.0 | 170 | 5,188 | 7.67 | 30.52 | 23.86 | 1292 | 31.85% |
| SL Malinga | 122 | 471.2 | 170 | 3,366 | 7.14 | 19.8 | 16.63 | 1144 | 40.47% |

---

## Chapter 6 — Strategic & Phase of Play Analysis

### 6.1 Phase Breakdown (Powerplay vs Middle vs Death Overs)
Splitting innings into three tactical phases reveals contrasting scoring dynamics:

| Phase | Overs | Total Runs | Wickets | Legal Balls | Run Rate | Boundary % | Dot Ball % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Death Overs (16-20) | 10025.8 | 100,423 | 4467 | 60155 | 10.02 | 59.45% | 28.41% |
| Middle Overs (7-15) | 20628.5 | 162,249 | 5003 | 123771 | 7.87 | 49.92% | 31.97% |
| Powerplay (1-6) | 14006.0 | 111,611 | 3175 | 84036 | 7.97 | 66.19% | 46.55% |

**Key Phase Findings:**
- **Powerplay (1-6):** High boundary percentage (66.19%) driven by fielding restrictions, but elevated dot-ball rate due to new ball movement.
- **Middle Overs (7-15):** Characterized by lower risk taking, steady accumulation, and spin dominance.
- **Death Overs (16-20):** High-intensity boundary hitting resulting in the highest run rate (10.02 runs/over).

---

## Chapter 7 — Inferential Statistical Hypothesis Testing

### 7.1 Hypothesis Test 1: Scoring Escalation (Welch's Two-Sample t-Test)
- **Research Question:** Has IPL 1st innings scoring significantly escalated in the Modern Era (2017–2025) compared to the Early Era (2008–2016)?
- **Null Hypothesis ($H_0$):** $\mu_{	ext{modern}} = \mu_{	ext{early}}$
- **Alternative Hypothesis ($H_1$):** $\mu_{	ext{modern}} > \mu_{	ext{early}}$

**Empirical Results:**
- **Early Era (2008–2016) Mean 1st Innings Score:** 159.04 runs ($SD = 30.11$, $N = 577$)
- **Modern Era (2017–2025) Mean 1st Innings Score:** 174.8 runs ($SD = 33.75$, $N = 592$)
- **Mean Difference:** +15.76 runs per innings
- **t-statistic:** 8.4301
- **p-value:** $1.0141e-16$ (Significantly $< 0.05$)
- **Cohen's d Effect Size:** 0.492 (Moderate-to-large effect size)
- **Statistical Decision:** **Reject Null Hypothesis.** There is overwhelming statistical evidence that modern IPL scoring rates are significantly higher than early IPL seasons.

### 7.2 Hypothesis Test 2: Toss Outcome Advantage (Chi-Square Test)
- **Research Question:** Does winning the toss provide a statistically significant advantage toward winning the match?
- **Null Hypothesis ($H_0$):** Toss outcome and match outcome are independent.
- **Alternative Hypothesis ($H_1$):** Winning the toss provides a non-random win advantage.

**Empirical Results:**
- **Matches Analyzed:** 1146
- **Toss Winners Winning Match:** 591 (51.57%)
- **Chi-Square Statistic ($\chi^2$):** 0.0
- **p-value:** 1.0000
- **Cramer's V:** 0.0
- **Statistical Decision:** **Fail to Reject Null Hypothesis.** Across all 18 seasons, winning the toss yields a win rate of 51.6%, which is not statistically different from random chance (50%).

---

## Chapter 8 — Streamlit Interactive Dashboard Architecture

The accompanying Streamlit application (`app.py`) provides an interactive 7-page analytical environment:
1. **Overview & Summary:** High-level KPIs, scoring trends, and win distribution charts.
2. **Batting Analytics:** Leaderboards, strike rate vs run scatter plots, and seasonal player deep dives.
3. **Bowling Analytics:** Wicket leaders, economy vs wickets scatter plots, and dot ball analysis.
4. **Team Performance:** Win percentage rankings, chasing vs defending split, and team-season heatmaps.
5. **Phase & Venue Analytics:** Over-by-over phase comparison and venue-level score distributions.
6. **Statistical Insights:** Descriptive statistics tables, Welch's t-test, and Chi-square hypothesis tests.
7. **Player Head-to-Head Comparator:** Side-by-side metric comparison and 5-axis Radar Charts.

---

## Chapter 9 — Analytical Limitations

1. **Rule Changes:** Introduction of the Impact Player rule (2023 onwards) altered batting depth and team tactics.
2. **Venue Home Advantage:** Certain teams played more home matches in specific venues due to stadium availability or neutral venue tournaments (e.g., UAE 2020).
3. **Player Role Context:** Lower-order finishers face fewer balls at higher required strike rates compared to top-order anchors.

---

## Chapter 10 — Conclusion

This comprehensive study demonstrates that:
1. **IPL scoring environment has evolved dramatically**, increasing by ~15.8 runs per 1st innings from early eras to modern seasons ($p < 10^-15$).
2. **Toss outcomes do not guarantee match victory** ($51.6\%$ win conversion rate, $p > 0.05$).
3. **Franchises prioritizing death-over execution and boundary percentage** achieve higher overall win stability across 18 IPL seasons.

---
*Report generated automatically by IPL Analytics Engine v1.0.0*
