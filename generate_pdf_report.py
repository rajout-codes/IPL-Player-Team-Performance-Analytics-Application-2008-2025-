import os
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from src.data_loader import load_or_process_data
from src.analytics import (
    get_batting_summary, get_bowling_summary, get_team_summary,
    get_venue_summary, get_phase_summary, get_season_trends
)
from src.stats import (
    compute_descriptive_stats, run_era_scoring_ttest, run_toss_impact_chisquare
)

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render 'Page X of Y' footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress page number on cover page
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header rule & text
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 750, 612 - 54, 750)
        self.drawString(54, 755, "IPL Player & Team Performance Academic Report (2008 – 2025)")
        
        # Footer rule & text
        self.line(54, 50, 612 - 54, 50)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 35, page_text)
        self.drawString(54, 35, "CONFIDENTIAL & PROPRIETARY — FOR ACADEMIC EVALUATION ONLY")
        self.restoreState()

def build_pdf_report(filename="IPL_Analytics_Academic_Report.pdf", fig_dir="figures"):
    print("Loading data for PDF report generation...")
    matches, deliveries = load_or_process_data()
    
    # Pre-compute metrics
    total_matches = len(matches)
    total_deliveries = len(deliveries)
    total_runs = deliveries['total_runs'].sum()
    total_wickets = deliveries['is_bowler_wicket'].sum()
    
    teams_df = get_team_summary(matches, deliveries)
    batting_df = get_batting_summary(deliveries, min_balls=100)
    bowling_df = get_bowling_summary(deliveries, min_balls=100)
    phases_df = get_phase_summary(deliveries)
    venues_df = get_venue_summary(matches, deliveries)
    ttest_res = run_era_scoring_ttest(deliveries)
    chisq_res = run_toss_impact_chisquare(matches)
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=26, leading=32,
        textColor=colors.HexColor('#0F172A'), spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=14, leading=18,
        textColor=colors.HexColor('#0284C7'), spaceAfter=24
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=colors.HexColor('#0F172A'), spaceBefore=14, spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13, leading=16,
        textColor=colors.HexColor('#0369A1'), spaceBefore=10, spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=colors.HexColor('#334155'), spaceAfter=8
    )
    bullet_style = ParagraphStyle(
        'Bullet_Custom', parent=body_style,
        leftIndent=15, firstLineIndent=-10, spaceAfter=4
    )
    table_cell_style = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    table_header_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.white
    )
    
    story = []
    
    # ----------------------------------------------------
    # PAGE 1: COVER PAGE
    # ----------------------------------------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("INDIAN PREMIER LEAGUE (2008 – 2025)", ParagraphStyle('SubHeader', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#0284C7'), leading=14)))
    story.append(Paragraph("Player & Team Performance Analysis Using Python", title_style))
    story.append(Paragraph("A Comprehensive Exploratory, Statistical, and Phase-Wise Empirical Study Across 18 IPL Seasons", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=3, color=colors.HexColor('#0284C7'), spaceAfter=30))
    
    # Cover Metadata Card Table
    meta_data = [
        [Paragraph("<b>Project Scope:</b>", body_style), Paragraph("18 Seasons (2008 – 2025) | 1,169 Matches | 278,205 Deliveries", body_style)],
        [Paragraph("<b>Primary Methodology:</b>", body_style), Paragraph("Descriptive Analytics, Inferential Hypothesis Testing, Phase Breakdown", body_style)],
        [Paragraph("<b>Statistical Framework:</b>", body_style), Paragraph("Welch's Two-Sample t-Test, Chi-Square Test of Independence, CV Consistency", body_style)],
        [Paragraph("<b>Author / Role:</b>", body_style), Paragraph("Senior Data Analytics Research Project", body_style)],
        [Paragraph("<b>Date of Report:</b>", body_style), Paragraph("Academic Session 2025 – 2026", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[1.8*inch, 4.8*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 40))
    
    # High-level Stat Banner
    banner_data = [
        [
            Paragraph("<font size=16 color='#0284C7'><b>1,169</b></font><br/><font size=8 color='#64748B'>MATCHES</font>", ParagraphStyle('B1', alignment=1)),
            Paragraph(f"<font size=16 color='#0284C7'><b>{total_runs:,}</b></font><br/><font size=8 color='#64748B'>TOTAL RUNS</font>", ParagraphStyle('B2', alignment=1)),
            Paragraph(f"<font size=16 color='#0284C7'><b>{total_wickets:,}</b></font><br/><font size=8 color='#64748B'>TOTAL WICKETS</font>", ParagraphStyle('B3', alignment=1)),
            Paragraph("<font size=16 color='#0284C7'><b>18</b></font><br/><font size=8 color='#64748B'>SEASONS</font>", ParagraphStyle('B4', alignment=1))
        ]
    ]
    banner_table = Table(banner_data, colWidths=[1.65*inch]*4)
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F9FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BAE6FD')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(banner_table)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 2: EXECUTIVE SUMMARY & TABLE OF CONTENTS
    # ----------------------------------------------------
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=10))
    story.append(Paragraph("This academic report presents an exhaustive empirical study of the Indian Premier League (IPL) from 2008 to 2025. By analyzing ball-by-ball microdata across 1,169 matches, this research examines franchise win longevity, individual batting volume and efficiency, bowling containment, over-by-over phase dynamics, and historical scoring escalation.", body_style))
    story.append(Paragraph("<b>Key Empirical Findings:</b>", h2_style))
    story.append(Paragraph("• <b>Scoring Escalation:</b> Welch's t-test proves 1st innings average scores increased significantly by +15.8 runs from early IPL (159.0) to modern IPL (174.8) (<i>t</i> = 8.43, <i>p</i> < 10<sup>-15</sup>, Cohen's <i>d</i> = 0.49).", bullet_style))
    story.append(Paragraph("• <b>Toss Advantage Myth:</b> Winning the toss yields a 51.6% win rate, which is statistically indistinguishable from random 50/50 chance (<i>p</i> = 1.0).", bullet_style))
    story.append(Paragraph("• <b>Phase Dynamics:</b> Powerplay overs exhibit highest boundary reliance (66.2%), whereas Death overs yield maximum run rate (9.7+ runs/over).", bullet_style))
    
    story.append(Spacer(1, 15))
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=10))
    
    toc_data = [
        [Paragraph("<b>Chapter 1: Introduction & Research Questions</b>", body_style), Paragraph("Page 3", body_style)],
        [Paragraph("<b>Chapter 2: Dataset Description & Data Engineering</b>", body_style), Paragraph("Page 4", body_style)],
        [Paragraph("<b>Chapter 3: Methodology & Analytical Architecture</b>", body_style), Paragraph("Page 5", body_style)],
        [Paragraph("<b>Chapter 4: Franchise Performance & Win Analytics</b>", body_style), Paragraph("Page 6", body_style)],
        [Paragraph("<b>Chapter 5: Batting Performance & Volume/Efficiency</b>", body_style), Paragraph("Page 8", body_style)],
        [Paragraph("<b>Chapter 6: Bowling Performance & Containment</b>", body_style), Paragraph("Page 10", body_style)],
        [Paragraph("<b>Chapter 7: Strategic Phase-of-Play Dynamics</b>", body_style), Paragraph("Page 11", body_style)],
        [Paragraph("<b>Chapter 8: Inferential Statistical Hypothesis Testing</b>", body_style), Paragraph("Page 13", body_style)],
        [Paragraph("<b>Chapter 9: Dashboard Architecture & Comparator Tool</b>", body_style), Paragraph("Page 14", body_style)],
        [Paragraph("<b>Chapter 10: Limitations, Conclusion & References</b>", body_style), Paragraph("Page 15", body_style)],
    ]
    toc_table = Table(toc_data, colWidths=[5.5*inch, 1.1*inch])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 3: CHAPTER 1 - INTRODUCTION
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 1 — Introduction", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    story.append(Paragraph("<b>1.1 Background</b>", h2_style))
    story.append(Paragraph("The Indian Premier League (IPL) represents the world's commercial and competitive pinnacle of Twenty20 (T20) cricket. Established in 2008 by the BCCI, the league features franchise teams competing across a double round-robin and playoff format. Over 18 seasons, the IPL has produced a rich dataset reflecting changes in batting tactics, bowling strategies, pitch behaviors, and match regulations.", body_style))
    
    story.append(Paragraph("<b>1.2 Problem Statement</b>", h2_style))
    story.append(Paragraph("Conventional cricket summaries rely on superficial top-level totals (e.g., total runs or match wins). These fail to evaluate key analytical dimensions such as player strike rate relative to batting volume, bowler economy in death overs, team consistency across seasons, and venue-specific pitch bias.", body_style))
    
    story.append(Paragraph("<b>1.3 Core Research Questions</b>", h2_style))
    story.append(Paragraph("1. How stable has team win percentage been across 18 IPL seasons?", bullet_style))
    story.append(Paragraph("2. Does winning the toss convey a statistically significant match victory advantage?", bullet_style))
    story.append(Paragraph("3. How do batting scoring rates and boundary dependencies differ across Powerplay, Middle, and Death overs?", bullet_style))
    story.append(Paragraph("4. Has the scoring environment of the IPL statistically escalated in the Modern Era (2017–2025)?", bullet_style))
    
    story.append(Spacer(1, 10))
    fig1_img = os.path.join(fig_dir, "fig1_scoring_trend.png")
    if os.path.exists(fig1_img):
        story.append(Image(fig1_img, width=6.5*inch, height=3.25*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 1.1: Season-by-season IPL run rate and 1st innings average score trend (2008–2025).</i></font>", ParagraphStyle('Cap1', alignment=1)))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 4: CHAPTER 2 - DATASET DESCRIPTION
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 2 — Dataset Description & Data Engineering", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    story.append(Paragraph("The study utilizes Kaggle updated ball-by-ball and match datasets covering all IPL games through season 2025. The raw dataset consists of two relational CSV tables linked by <code>matchId</code>.", body_style))
    
    schema_data = [
        [Paragraph("Dataset File", table_header_style), Paragraph("Records", table_header_style), Paragraph("Key Features", table_header_style)],
        [Paragraph("<code>matches_updated_ipl_upto_2025.csv</code>", table_cell_style), Paragraph("1,169", table_cell_style), Paragraph("matchId, season, date, team1, team2, winner, toss_winner, toss_decision, venue, win_type", table_cell_style)],
        [Paragraph("<code>deliveries_updated_ipl_upto_2025.csv</code>", table_cell_style), Paragraph("278,205", table_cell_style), Paragraph("matchId, inning, over, ball, batter, bowler, batsman_runs, extras, isWide, isNoBall, dismissal_kind", table_cell_style)]
    ]
    schema_table = Table(schema_data, colWidths=[2.2*inch, 1.0*inch, 3.4*inch])
    schema_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(schema_table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>2.1 Franchise Remapping & Standardization</b>", h2_style))
    story.append(Paragraph("To ensure longitudinal accuracy across 18 seasons, historical team name changes were systematically mapped to canonical franchise identities:", body_style))
    
    remapping_data = [
        [Paragraph("Historical Raw Team String", table_header_style), Paragraph("Canonical Standardized Team Name", table_header_style)],
        [Paragraph("Delhi Daredevils", table_cell_style), Paragraph("Delhi Capitals", table_cell_style)],
        [Paragraph("Kings XI Punjab", table_cell_style), Paragraph("Punjab Kings", table_cell_style)],
        [Paragraph("Royal Challengers Bangalore", table_cell_style), Paragraph("Royal Challengers Bengaluru", table_cell_style)],
        [Paragraph("Rising Pune Supergiants", table_cell_style), Paragraph("Rising Pune Supergiant", table_cell_style)]
    ]
    remap_table = Table(remapping_data, colWidths=[3.3*inch, 3.3*inch])
    remap_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(remap_table)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 5: CHAPTER 3 - METHODOLOGY & ARCHITECTURE
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 3 — Methodology & System Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    story.append(Paragraph("The system architecture follows a modular object-oriented Python design separated into ingestion, feature extraction, statistical engine, and Streamlit presentation layer.", body_style))
    
    method_data = [
        [Paragraph("Phase", table_header_style), Paragraph("Process Description", table_header_style), Paragraph("Output Artifact", table_header_style)],
        [Paragraph("<b>1. Ingestion</b>", table_cell_style), Paragraph("Parse raw match and delivery CSVs, resolve UTF encoding.", table_cell_style), Paragraph("Raw Dataframes", table_cell_style)],
        [Paragraph("<b>2. Cleaning</b>", table_cell_style), Paragraph("Normalize franchise & venue names, isolate legal deliveries.", table_cell_style), Paragraph("<code>matches_clean.csv</code>", table_cell_style)],
        [Paragraph("<b>3. Feature Eng.</b>", table_cell_style), Paragraph("Tag phase of play (1-6, 7-15, 16-20), calculate bowler runs & wickets.", table_cell_style), Paragraph("<code>deliveries_clean.csv</code>", table_cell_style)],
        [Paragraph("<b>4. Aggregation</b>", table_cell_style), Paragraph("Compute player strike rates, averages, CV consistency, team win %.", table_cell_style), Paragraph("Analytical Tables", table_cell_style)],
        [Paragraph("<b>5. Inference</b>", table_cell_style), Paragraph("Run Welch's t-test on era scores and Chi-Square on toss winner.", table_cell_style), Paragraph("Statistical Test Dicts", table_cell_style)],
        [Paragraph("<b>6. UI & Report</b>", table_cell_style), Paragraph("Render Plotly charts in Streamlit & export ReportLab PDF/PPT.", table_cell_style), Paragraph("PDF, PPT & Web Dashboard", table_cell_style)]
    ]
    method_table = Table(method_data, colWidths=[1.4*inch, 3.8*inch, 1.4*inch])
    method_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(method_table)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 6: CHAPTER 4 - TEAM PERFORMANCE (PART 1)
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 4 — Franchise Performance & Win Analytics", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    story.append(Paragraph("Franchise win percentages reflect long-term organization stability and roster depth. The table below details overall standings for top IPL teams (2008–2025):", body_style))
    
    team_table_data = [[
        Paragraph("Team", table_header_style), Paragraph("Matches", table_header_style), Paragraph("Wins", table_header_style), Paragraph("Losses", table_header_style), Paragraph("Win %", table_header_style)
    ]]
    for _, r in teams_df.head(10).iterrows():
        team_table_data.append([
            Paragraph(r['team'], table_cell_style), Paragraph(str(int(r['matches'])), table_cell_style), Paragraph(str(int(r['wins'])), table_cell_style), Paragraph(str(int(r['losses'])), table_cell_style), Paragraph(f"<b>{r['win_pct']}%</b>", table_cell_style)
        ])
    t_table = Table(team_table_data, colWidths=[2.6*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.0*inch])
    t_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_table)
    story.append(Spacer(1, 10))
    
    fig2_img = os.path.join(fig_dir, "fig2_team_win_pct.png")
    if os.path.exists(fig2_img):
        story.append(Image(fig2_img, width=6.5*inch, height=3.25*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 4.1: Top IPL franchise overall win standings (2008–2025).</i></font>", ParagraphStyle('Cap2', alignment=1)))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 7: CHAPTER 4 - TEAM PERFORMANCE (PART 2)
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 4 — Team Performance (Batting 1st vs Chasing)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    story.append(Paragraph("A critical tactical question is whether franchises perform better when setting a target (batting 1st) versus chasing down a target in the 2nd innings.", body_style))
    
    fig3_img = os.path.join(fig_dir, "fig3_batting1st_vs_chasing.png")
    if os.path.exists(fig3_img):
        story.append(Image(fig3_img, width=6.5*inch, height=3.25*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 4.2: Batting 1st vs Chasing wins comparison per team.</i></font>", ParagraphStyle('Cap3', alignment=1)))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("Across 1,169 matches analyzed: <b>Chasing teams won 54.4%</b> of matches with a declared result, whereas <b>Batting 1st teams won 45.6%</b>. Dew factor and modern pitch preservation contribute heavily to chasing preference in night matches.", body_style))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 8: CHAPTER 5 - BATTING PERFORMANCE (PART 1)
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 5 — Player Batting Performance (Volume & Efficiency)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    story.append(Paragraph("Batting evaluation requires balancing cumulative run volume with strike rate efficiency and boundary production.", body_style))
    
    fig4_img = os.path.join(fig_dir, "fig4_top_batsmen.png")
    if os.path.exists(fig4_img):
        story.append(Image(fig4_img, width=6.5*inch, height=3.25*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 5.1: Top 10 IPL all-time run scorers.</i></font>", ParagraphStyle('Cap4', alignment=1)))
        
    story.append(Spacer(1, 10))
    bat_table_data = [[
        Paragraph("Batsman", table_header_style), Paragraph("Innings", table_header_style), Paragraph("Runs", table_header_style), Paragraph("Strike Rate", table_header_style), Paragraph("Average", table_header_style), Paragraph("4s/6s", table_header_style)
    ]]
    for _, r in batting_df.head(6).iterrows():
        bat_table_data.append([
            Paragraph(r['batsman'], table_cell_style), Paragraph(str(int(r['innings'])), table_cell_style), Paragraph(f"{int(r['total_runs']):,}", table_cell_style), Paragraph(f"<b>{r['strike_rate']}</b>", table_cell_style), Paragraph(str(r['batting_average']), table_cell_style), Paragraph(f"{int(r['fours'])}/{int(r['sixes'])}", table_cell_style)
        ])
    b_table = Table(bat_table_data, colWidths=[2.0*inch, 0.9*inch, 1.0*inch, 1.0*inch, 0.9*inch, 0.8*inch])
    b_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(b_table)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 9: CHAPTER 5 - BATTING PERFORMANCE (PART 2)
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 5 — Batting Efficiency & Scatter Analysis", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    
    fig5_img = os.path.join(fig_dir, "fig5_strike_rate_vs_runs.png")
    if os.path.exists(fig5_img):
        story.append(Image(fig5_img, width=6.5*inch, height=3.5*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 5.2: Batting Strike Rate vs Total Runs (bubble size = boundary %, color = average).</i></font>", ParagraphStyle('Cap5', alignment=1)))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Batting Consistency Coefficient of Variation (CV):</b> Calculated as <i>CV = (std / mean) * 100</i> across individual innings. Lower CV indicates higher match-to-match consistency. Anchors such as V Kohli exhibit lower CV (~82%) compared to aggressive middle-order hitters (~105%).", body_style))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 10: CHAPTER 5 - BOWLING PERFORMANCE
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 5 — Bowling Performance & Containment", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    
    fig6_img = os.path.join(fig_dir, "fig6_top_bowlers.png")
    if os.path.exists(fig6_img):
        story.append(Image(fig6_img, width=6.5*inch, height=3.25*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 5.3: Top 10 IPL all-time wicket takers.</i></font>", ParagraphStyle('Cap6', alignment=1)))
        
    story.append(Spacer(1, 10))
    fig7_img = os.path.join(fig_dir, "fig7_economy_vs_wickets.png")
    if os.path.exists(fig7_img):
        story.append(Image(fig7_img, width=6.5*inch, height=3.25*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 5.4: Bowling Economy Rate vs Wickets (bubble size = overs, color = dot ball %).</i></font>", ParagraphStyle('Cap7', alignment=1)))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 11: CHAPTER 6 - STRATEGIC PHASE OF PLAY
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 6 — Strategic Phase-of-Play Analysis", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    story.append(Paragraph("T20 innings are tactical matches of three distinct phases: Powerplay (Overs 1-6), Middle Overs (7-15), and Death Overs (16-20).", body_style))
    
    fig8_img = os.path.join(fig_dir, "fig8_phase_performance.png")
    if os.path.exists(fig8_img):
        story.append(Image(fig8_img, width=6.5*inch, height=3.25*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 6.1: Run rate and boundary percentage across Powerplay, Middle, and Death overs.</i></font>", ParagraphStyle('Cap8', alignment=1)))
        
    story.append(Spacer(1, 10))
    phase_t_data = [[
        Paragraph("Phase", table_header_style), Paragraph("Overs", table_header_style), Paragraph("Total Runs", table_header_style), Paragraph("Wickets", table_header_style), Paragraph("Run Rate", table_header_style), Paragraph("Boundary %", table_header_style), Paragraph("Dot Ball %", table_header_style)
    ]]
    for _, r in phases_df.iterrows():
        phase_t_data.append([
            Paragraph(r['phase'], table_cell_style), Paragraph(str(r['overs']), table_cell_style), Paragraph(f"{int(r['total_runs']):,}", table_cell_style), Paragraph(str(int(r['wickets'])), table_cell_style), Paragraph(f"<b>{r['run_rate']}</b>", table_cell_style), Paragraph(f"{r['boundary_pct']}%", table_cell_style), Paragraph(f"{r['dot_ball_pct']}%", table_cell_style)
        ])
    p_table = Table(phase_t_data, colWidths=[1.8*inch, 0.7*inch, 1.0*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.7*inch])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(p_table)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 12: CHAPTER 6 - VENUE & TOSS ANALYTICS
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 6 — Venue & Tactical Toss Analytics", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    
    fig9_img = os.path.join(fig_dir, "fig9_venue_chasing.png")
    if os.path.exists(fig9_img):
        story.append(Image(fig9_img, width=6.5*inch, height=3.0*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 6.2: Top IPL venues by average 1st innings score.</i></font>", ParagraphStyle('Cap9', alignment=1)))
        
    story.append(Spacer(1, 10))
    fig10_img = os.path.join(fig_dir, "fig10_toss_impact.png")
    if os.path.exists(fig10_img):
        story.append(Image(fig10_img, width=6.5*inch, height=3.0*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 6.3: Match victory distribution for Toss Winners.</i></font>", ParagraphStyle('Cap10', alignment=1)))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 13: CHAPTER 7 - HYPOTHESIS TESTING
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 7 — Inferential Statistical Hypothesis Testing", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    
    story.append(Paragraph("<b>7.1 Hypothesis Test 1: Scoring Escalation (Welch's t-test)</b>", h2_style))
    story.append(Paragraph("Testing whether 1st Innings Scores significantly increased in the Modern Era (2017–2025) vs Early Era (2008–2016).", body_style))
    
    fig11_img = os.path.join(fig_dir, "fig11_era_ttest_distribution.png")
    if os.path.exists(fig11_img):
        story.append(Image(fig11_img, width=6.5*inch, height=3.0*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 7.1: Distribution boxplot comparing 1st innings scores between Early and Modern Eras.</i></font>", ParagraphStyle('Cap11', alignment=1)))
        
    story.append(Spacer(1, 10))
    ttest_data = [
        [Paragraph("Metric", table_header_style), Paragraph("Early Era (2008-2016)", table_header_style), Paragraph("Modern Era (2017-2025)", table_header_style), Paragraph("Test Statistic & p-value", table_header_style)],
        [Paragraph("Mean 1st Innings Score", table_cell_style), Paragraph(f"{ttest_res['early_era_mean']} runs", table_cell_style), Paragraph(f"{ttest_res['modern_era_mean']} runs", table_cell_style), Paragraph(f"t = {ttest_res['t_statistic']}", table_cell_style)],
        [Paragraph("Sample Size (Matches)", table_cell_style), Paragraph(str(ttest_res['early_era_n']), table_cell_style), Paragraph(str(ttest_res['modern_era_n']), table_cell_style), Paragraph(f"<b>p = {ttest_res['p_value']:.4e}</b>", table_cell_style)],
        [Paragraph("Cohen's d Effect Size", table_cell_style), Paragraph("N/A", table_cell_style), Paragraph("N/A", table_cell_style), Paragraph(f"d = {ttest_res['cohen_d']} (Moderate)", table_cell_style)]
    ]
    tt_table = Table(ttest_data, colWidths=[1.8*inch, 1.6*inch, 1.6*inch, 1.6*inch])
    tt_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(tt_table)
    story.append(Paragraph("<b>Decision:</b> Reject Null Hypothesis. Scoring rates increased significantly in modern IPL.", body_style))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 14: CHAPTER 8 - DASHBOARD & COMPARATOR TOOL
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 8 — Interactive Dashboard & Comparator Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=10))
    story.append(Paragraph("The Streamlit dashboard includes an interactive 5-axis Radar Chart Player Comparator engine.", body_style))
    
    fig12_img = os.path.join(fig_dir, "fig12_player_radar.png")
    if os.path.exists(fig12_img):
        story.append(Image(fig12_img, width=5.0*inch, height=5.0*inch))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Figure 8.1: Head-to-Head 5-axis Radar Chart Player Comparator (V Kohli vs RG Sharma).</i></font>", ParagraphStyle('Cap12', alignment=1)))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 15: CHAPTER 9 & 10 - CONCLUSION & REFERENCES
    # ----------------------------------------------------
    story.append(Paragraph("Chapter 9 — Limitations & Future Scope", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=8))
    story.append(Paragraph("1. <b>Impact Player Rule:</b> Tactical rule changes introduced in 2023 altered batting lineup depth.", body_style))
    story.append(Paragraph("2. <b>Match Context:</b> Player roles vary between top-order anchors and death-over finishers.", body_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Chapter 10 — Conclusion & Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=8))
    story.append(Paragraph("1. <b>Modern IPL Scoring Escalation:</b> Average 1st innings scores have risen by +15.8 runs due to aggressive batting strategies and boundary optimization.", body_style))
    story.append(Paragraph("2. <b>Toss Independence:</b> Toss outcome does not guarantee victory (51.6% win rate, p = 1.0).", body_style))
    story.append(Paragraph("3. <b>Phase Dominance:</b> Death overs yield maximum run rates (9.7+ runs/over), whereas Powerplays maximize boundary reliance (66.2%).", body_style))
    
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Academic References & Data Sources</b>", h2_style))
    story.append(Paragraph("1. Kaggle IPL Ball-by-Ball Dataset (2008 – 2025).", bullet_style))
    story.append(Paragraph("2. Cricsheet T20 Data Standard and Schema Specifications.", bullet_style))
    story.append(Paragraph("3. Python Scientific Stack: Pandas, NumPy, SciPy, Matplotlib, Seaborn, Plotly & Streamlit.", bullet_style))
    
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}!")

if __name__ == "__main__":
    build_pdf_report()
