import sys
import os
from collections import Counter
import numpy as np
np.random.seed(42)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_pipeline import DataPipeline
from src.model import PoissonModel
from src.simulator import TournamentSimulator

TOURNAMENT_GROUPS = {
    'Group A': ['Mexico', 'South Africa', 'South Korea', 'Czech Republic'],
    'Group B': ['Canada', 'Bosnia and Herzegovina', 'Qatar', 'Switzerland'],
    'Group C': ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    'Group D': ['USA', 'Paraguay', 'Australia', 'Turkey'],
    'Group E': ['Germany', 'Curacao', 'Ivory Coast', 'Ecuador'],
    'Group F': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'Group G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'Group H': ['Spain', 'Cape Verde', 'Saudi Arabia', 'Uruguay'],
    'Group I': ['France', 'Senegal', 'Iraq', 'Norway'],
    'Group J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'Group K': ['Portugal', 'DR Congo', 'Uzbekistan', 'Colombia'],
    'Group L': ['England', 'Croatia', 'Ghana', 'Panama']
}

def run_monte_carlo():
    print("Booting E2E 48-Team Production Pipeline...")
    pipeline = DataPipeline(data_dir="data")
    
    pipeline = DataPipeline(data_dir="data")

    baseline_home = 1.48 
    baseline_away = 1.15

    model = PoissonModel(baseline_home, baseline_away, pipeline)

    all_teams = [team for group in TOURNAMENT_GROUPS.values() for team in group]
    all_teams = list(set(all_teams)) 
    
    pipeline.precompute_tournament_metrics(all_teams)
    home_base, away_base = pipeline.get_baseline_goals()
    
    print("Calibrating Poisson Mathematical Engine...")
    model = PoissonModel(baseline_home=home_base, baseline_away=away_base, pipeline=pipeline)
    simulator = TournamentSimulator(TOURNAMENT_GROUPS, model, pipeline)
    
    champions, runners_up, thirds, fourths = [], [], [], []
    golden_boots, golden_balls, golden_gloves, worst_teams = [], [], [], []
    
    SIMULATIONS = 1000
    print(f"Processing {SIMULATIONS:,} complete World Cups concurrently...")
    
    for _ in range(SIMULATIONS):
        qualified_32, worst_team = simulator.simulate_group_stage()
        worst_teams.append(worst_team)
        
        results = simulator.simulate_bracket(qualified_32)
        
        champions.append(results['champion'])
        runners_up.append(results['runner_up'])
        thirds.append(results['third_place'])
        fourths.append(results['fourth_place'])
        
        champ_scorers = pipeline.get_active_scorers(results['champion'], top_n=1)
        for player in champ_scorers.keys(): 
            if player != "No Active Scorer Found": golden_balls.append(player)
            
        for team in [results['champion'], results['runner_up']]:
            for player in pipeline.get_active_scorers(team, top_n=1).keys():
                if player != "No Active Scorer Found": golden_boots.append(player)
                
        best_def_team, lowest_gc = None, float('inf')
        for team in results['top_4']:
            _, avg_conceded = pipeline.get_recent_form(team)
            if avg_conceded < lowest_gc:
                lowest_gc = avg_conceded
                best_def_team = team
        if best_def_team: golden_gloves.append(best_def_team)

    print("\n========================================================")
    print("ULTIMATE 2026 WORLD CUP PREDICTOR (48 TEAMS)")
    print("========================================================")
    
    print("\nTOURNAMENT CHAMPION:")
    for t, c in Counter(champions).most_common(3): print(f"  - {t}: {(c/SIMULATIONS)*100:.1f}%")
        
    print("\nTOURNAMENT RUNNER-UP:")
    for t, c in Counter(runners_up).most_common(3): print(f"  - {t}: {(c/SIMULATIONS)*100:.1f}%")
        
    print("\nTHIRD PLACE MEDALIST:")
    for t, c in Counter(thirds).most_common(3): print(f"  - {t}: {(c/SIMULATIONS)*100:.1f}%")
        
    print("\nGOLDEN BALL (Tournament MVP):")
    bad_names = ["Legendary Player", "No Active Scorer Found", "Star Striker", "Unknown Star", "Top Scorer"]
    
    valid_balls = [p for p in golden_balls if p not in bad_names]
    for p, c in Counter(valid_balls).most_common(3): 
        prob = (c / SIMULATIONS) * 100
        print(f"  - {p}: {prob:.1f}%")
        
    print("\nGOLDEN BOOT (Top Goalscorer):")
    valid_boots = [p for p in golden_boots if p not in bad_names]
    for p, c in Counter(valid_boots).most_common(3): 
        prob = (c / SIMULATIONS) * 100
        print(f"  - {p}: {prob:.1f}%")
        
    print("\nGOLDEN GLOVE (Best Goalkeeper):")
    for t, c in Counter(golden_gloves).most_common(3): print(f"  - Goalkeeper from {t}")
        
    print("\nTHE WOODEN SPOON (Worst Overall Performance):")
    for t, c in Counter(worst_teams).most_common(3): print(f"  - {t}: {(c/SIMULATIONS)*100:.1f}% probability of last place finish")
    print("========================================================")

if __name__ == "__main__":
    run_monte_carlo()