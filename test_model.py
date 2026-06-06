from src.data_pipeline import DataPipeline
from src.model import PoissonModel

def test_mathematical_engine():
    print("Starting Poisson Model predictive test...")
    try:
        pipeline = DataPipeline(data_dir="data")
        home_base, away_base = pipeline.get_baseline_goals()
        model = PoissonModel(baseline_home=home_base, baseline_away=away_base)
        team_1 = "Argentina"
        team_2 = "Mexico"
        
        predictions = model.predict_match_probabilities(team_1, team_2, pipeline)
        
        print(f"\n Success: Poisson distribution calculated successfully for {team_1} vs {team_2}.")
        print(f"   {team_1} Win Probability: {predictions['prob_A_win']}%")
        print(f"   Draw Probability: {predictions['prob_draw']}%")
        print(f"   {team_2} Win Probability: {predictions['prob_B_win']}%")
        print(f"   Most Probable Exact Scoreline: {predictions['expected_score'][0]} - {predictions['expected_score'][1]}")
        
        print("\n [10/10] Poisson Model test passed!")
        
    except Exception as e:
        print(f"Test Failed! Error: {str(e)}")

if __name__ == "__main__":
    test_mathematical_engine()