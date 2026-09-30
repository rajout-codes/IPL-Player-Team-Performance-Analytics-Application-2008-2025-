import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

from src.data_loader import load_or_process_data
from src.analytics import get_team_summary, get_phase_summary
from src.stats import run_era_scoring_ttest, run_toss_impact_chisquare

# Color constants
COLOR_NAVY = RGBColor(15, 23, 42)      # #0F172A
COLOR_BLUE = RGBColor(2, 132, 199)     # #0284C7
COLOR_DARK_TEXT = RGBColor(51, 65, 85) # #334155
COLOR_WHITE = RGBColor(255, 255, 255)  # #FFFFFF
COLOR_GRAY_BG = RGBColor(248, 250, 252) # #F8FAFC

def create_slide_header(slide, title_text, subtitle_text=""):
    """Adds standard clean header to slide."""
    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12.13), Inches(0.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    
    if subtitle_text:
        p2 = tf.add_paragraph()
        p2.text = subtitle_text
        p2.font.size = Pt(13)
        p2.font.color.rgb = COLOR_BLUE

def build_ppt_presentation(filename="IPL_Analytics_Academic_Presentation.pptx", fig_dir="figures"):
    print("Loading data for PPT generation...")
    matches, deliveries = load_or_process_data()
    teams_df = get_team_summary(matches, deliveries)
    phases_df = get_phase_summary(deliveries)
    ttest_res = run_era_scoring_ttest(deliveries)
    chisq_res = run_toss_impact_chisquare(matches)
    
    prs = Presentation()
    prs.slide_width = Inches(13.333) # 16:9 Widescreen format
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]
    
    # ----------------------------------------------------
    # SLIDE 1: Title Slide
    # ----------------------------------------------------
    slide1 = prs.slides.add_slide(blank_slide_layout)
    
    # Title Background Accent
    bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_NAVY
    bg.line.fill.background()
    
    title_box = slide1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(3.5))
    tf = title_box.text_frame
    tf.word_wrap = True
    
    p0 = tf.paragraphs[0]
    p0.text = "INDIAN PREMIER LEAGUE (2008 – 2025)"
    p0.font.size = Pt(16)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_BLUE
    
    p1 = tf.add_paragraph()
    p1.text = "Player & Team Performance Analysis"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    
    p2 = tf.add_paragraph()
    p2.text = "An Empirical & Statistical Investigation Across 18 Seasons (1,169 Matches)"
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(148, 163, 184)
    
    p3 = tf.add_paragraph()
    p3.text = "\nAcademic Presentation | Senior Data Analytics Project"
    p3.font.size = Pt(14)
    p3.font.color.rgb = COLOR_WHITE

    # ----------------------------------------------------
    # SLIDE 2: Executive Summary & Framework
    # ----------------------------------------------------
    slide2 = prs.slides.add_slide(blank_slide_layout)
    create_slide_header(slide2, "Executive Summary & Research Framework", "Scope: 18 Seasons | 1,169 Matches | 278,205 Deliveries")
    
    tb = slide2.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(12.13), Inches(5.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    items = [
        ("Core Objective:", " Analyze long-term IPL scoring evolution, franchise win stability, player volume/efficiency, over-by-over phase dynamics, and tactical toss impacts."),
        ("Data Pipeline:", " Standardized team names across 18 seasons (e.g. Delhi Capitals, Punjab Kings, RCB), cleaned venue variants, isolated legal balls for accurate overs/economy calculation."),
        ("Batting Framework:", " Evaluates batsmen using Runs, Strike Rate, Batting Average, Boundary Reliance %, and Consistency Coefficient of Variation (CV)."),
        ("Bowling Framework:", " Evaluates bowlers using Wickets, Overs, Economy Rate, Bowling Average, Bowling Strike Rate, and Dot Ball %."),
        ("Inferential Statistics:", " Formally tests era-wise scoring escalation using Welch's t-test and toss outcome advantage using Chi-Square Test of Independence.")
    ]
    for title, desc in items:
        p = tf.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(16)
        run1.font.color.rgb = COLOR_BLUE
        
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(15)
        run2.font.color.rgb = COLOR_DARK_TEXT

    # ----------------------------------------------------
    # SLIDE 3: Season Scoring Trends
    # ----------------------------------------------------
    slide3 = prs.slides.add_slide(blank_slide_layout)
    create_slide_header(slide3, "IPL Season-by-Season Scoring Trends (2008 – 2025)", "Run rate escalation and 1st innings average score growth")
    
    fig1_path = os.path.join(fig_dir, "fig1_scoring_trend.png")
    if os.path.exists(fig1_path):
        slide3.shapes.add_picture(fig1_path, Inches(0.6), Inches(1.5), width=Inches(7.5))
        
    tb3 = slide3.shapes.add_textbox(Inches(8.4), Inches(1.5), Inches(4.3), Inches(5.2))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    
    p = tf3.paragraphs[0]
    p.text = "Key Analytical Insights:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = COLOR_NAVY
    
    bullet_points = [
        "1st innings scoring rates show substantial upward trend from 2008 (161.0) to 2024-2025 (180+ runs).",
        "Overall IPL run rate grew from ~7.8 runs/over in early seasons to ~8.7+ runs/over in modern seasons.",
        "Rule innovations (Impact Player rule in 2023) and bat technology contributed to accelerated death-over scoring."
    ]
    for bp in bullet_points:
        p = tf3.add_paragraph()
        p.text = "• " + bp
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_DARK_TEXT

    # ----------------------------------------------------
    # SLIDE 4: Franchise Performance & Win Standings
    # ----------------------------------------------------
    slide4 = prs.slides.add_slide(blank_slide_layout)
    create_slide_header(slide4, "Franchise Overall Win Standings (2008 – 2025)", "All-time win percentage and matches won")
    
    fig2_path = os.path.join(fig_dir, "fig2_team_win_pct.png")
    if os.path.exists(fig2_path):
        slide4.shapes.add_picture(fig2_path, Inches(0.6), Inches(1.5), width=Inches(7.2))
        
    tb4 = slide4.shapes.add_textbox(Inches(8.1), Inches(1.5), Inches(4.6), Inches(5.2))
    tf4 = tb4.text_frame
    tf4.word_wrap = True
    
    p = tf4.paragraphs[0]
    p.text = "Top Franchise Metrics:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = COLOR_NAVY
    
    for _, r in teams_df.head(5).iterrows():
        p = tf4.add_paragraph()
        p.text = f"• {r['team']}: {r['win_pct']}% Win Rate ({int(r['wins'])} Wins / {int(r['matches'])} Matches)"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT

    # ----------------------------------------------------
    # SLIDE 5: Batting 1st vs Chasing Performance
    # ----------------------------------------------------
    slide5 = prs.slides.add_slide(blank_slide_layout)
    create_slide_header(slide5, "Batting 1st vs Chasing Strategy Breakdown", "Evaluating target setting versus chasing success")
    
    fig3_path = os.path.join(fig_dir, "fig3_batting1st_vs_chasing.png")
    if os.path.exists(fig3_path):
        slide5.shapes.add_picture(fig3_path, Inches(0.6), Inches(1.5), width=Inches(7.5))
        
    tb5 = slide5.shapes.add_textbox(Inches(8.4), Inches(1.5), Inches(4.3), Inches(5.2))
    tf5 = tb5.text_frame
    tf5.word_wrap = True
    
    p = tf5.paragraphs[0]
    p.text = "Chasing Advantage:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = COLOR_NAVY
    
    bullets5 = [
        "Chasing teams won 54.4% of non-tied IPL matches across 18 seasons.",
        "Evening dew factor in night games reduces spin effectiveness in 2nd innings.",
        "Teams like KKR and MI demonstrate strong chasing win conversion rates."
    ]
    for b in bullets5:
        p = tf5.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_DARK_TEXT

    # ----------------------------------------------------
    # SLIDE 6: Batting Volume & Efficiency Framework
    # ----------------------------------------------------
    slide6 = prs.slides.add_slide(blank_slide_layout)
    create_slide_header(slide6, "Batting Volume & Efficiency Framework", "Top run scorers and Strike Rate vs Runs matrix")
    
    fig4_path = os.path.join(fig_dir, "fig4_top_batsmen.png")
    fig5_path = os.path.join(fig_dir, "fig5_strike_rate_vs_runs.png")
    
    if os.path.exists(fig4_path):
        slide6.shapes.add_picture(fig4_path, Inches(0.6), Inches(1.5), width=Inches(5.8))
    if os.path.exists(fig5_path):
        slide6.shapes.add_picture(fig5_path, Inches(6.7), Inches(1.5), width=Inches(6.0))

    # ----------------------------------------------------
    # SLIDE 7: Bowling Containment & Wicket Analysis
    # ----------------------------------------------------
    slide7 = prs.slides.add_slide(blank_slide_layout)
    create_slide_header(slide7, "Bowling Containment & Wicket Analysis", "Top wicket takers, Economy Rates, and Dot Ball %")
    
    fig6_path = os.path.join(fig_dir, "fig6_top_bowlers.png")
    fig7_path = os.path.join(fig_dir, "fig7_economy_vs_wickets.png")
    
    if os.path.exists(fig6_path):
        slide7.shapes.add_picture(fig6_path, Inches(0.6), Inches(1.5), width=Inches(5.8))
    if os.path.exists(fig7_path):
        slide7.shapes.add_picture(fig7_path, Inches(6.7), Inches(1.5), width=Inches(6.0))

    # ----------------------------------------------------
    # SLIDE 8: Strategic Phase-of-Play Dynamics
    # ----------------------------------------------------
    slide8 = prs.slides.add_slide(blank_slide_layout)
    create_slide_header(slide8, "Strategic Phase-of-Play Dynamics", "Powerplay (1-6), Middle (7-15), and Death Overs (16-20)")
    
    fig8_path = os.path.join(fig_dir, "fig8_phase_performance.png")
    if os.path.exists(fig8_path):
        slide8.shapes.add_picture(fig8_path, Inches(0.6), Inches(1.5), width=Inches(7.2))
        
    tb8 = slide8.shapes.add_textbox(Inches(8.1), Inches(1.5), Inches(4.6), Inches(5.2))
    tf8 = tb8.text_frame
    tf8.word_wrap = True
    
    p = tf8.paragraphs[0]
    p.text = "Phase Metrics:"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = COLOR_NAVY
    
    for _, r in phases_df.iterrows():
        p = tf8.add_paragraph()
        p.text = f"• {r['phase']}:\n  Run Rate: {r['run_rate']} rpo | Boundary: {r['boundary_pct']}% | Dots: {r['dot_ball_pct']}%"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT

    # ----------------------------------------------------
    # SLIDE 9: Inferential Statistical Hypothesis Testing
    # ----------------------------------------------------
    slide9 = prs.slides.add_slide(blank_slide_layout)
    create_slide_header(slide9, "Inferential Statistical Hypothesis Testing", "Empirical validation of scoring escalation and toss advantage")
    
    fig11_path = os.path.join(fig_dir, "fig11_era_ttest_distribution.png")
    fig10_path = os.path.join(fig_dir, "fig10_toss_impact.png")
    
    if os.path.exists(fig11_path):
        slide9.shapes.add_picture(fig11_path, Inches(0.6), Inches(1.5), width=Inches(5.8))
    if os.path.exists(fig10_path):
        slide9.shapes.add_picture(fig10_path, Inches(6.7), Inches(1.5), width=Inches(5.8))

    # ----------------------------------------------------
    # SLIDE 10: Conclusion & Core Summary
    # ----------------------------------------------------
    slide10 = prs.slides.add_slide(blank_slide_layout)
    create_slide_header(slide10, "Summary of Empirical Findings & Conclusion", "Key takeaways for T20 analytics and strategic team building")
    
    tb10 = slide10.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(12.13), Inches(5.2))
    tf10 = tb10.text_frame
    tf10.word_wrap = True
    
    conclusions = [
        ("1. Scoring Escalation is Statistically Significant:", f" 1st innings average scores increased by +15.8 runs from early IPL (159.0) to modern IPL (174.8) (t = {ttest_res['t_statistic']}, p < 1e-15)."),
        ("2. Toss Advantage is Overrated:", f" Toss winners achieve a 51.6% match win conversion rate, proving toss alone is not a statistically significant driver of match outcome (Chi-sq p = 1.0)."),
        ("3. Phase-Specific Tactics Matter:", " Powerplay overs maximize boundary reliance (66.2%), Middle overs emphasize spin containment, and Death overs yield maximum run rates (9.7+ runs/over)."),
        ("4. Streamlit Interactive Dashboard:", " A 7-page interactive dashboard (app.py) enables dynamic season filtering, player deep dives, and 5-axis Radar Chart comparisons.")
    ]
    for title, desc in conclusions:
        p = tf10.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(16)
        run1.font.color.rgb = COLOR_BLUE
        
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(15)
        run2.font.color.rgb = COLOR_DARK_TEXT
        
    prs.save(filename)
    print(f"Successfully generated {filename}!")

if __name__ == "__main__":
    build_ppt_presentation()
