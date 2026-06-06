import numpy as np
from scipy.stats import poisson

class PoissonModel:
    def __init__(self, baseline_home, baseline_away, pipeline, alpha=3.5):
        self.baseline_home = baseline_home
        self.baseline_away = baseline_away
        self.pipeline = pipeline
        self.alpha = alpha

    def predict_match_probabilities(self, team_A, team_B, pipeline):
        """
        Calculates win, draw, and loss probabilities.
        Now includes Web Scraped Market Values to weight individual talent (e.g., Lamine Yamal effect (my favorite player)).
        """
        rating_A = pipeline.get_live_rating(team_A)
        rating_B = pipeline.get_live_rating(team_B)
        
        attack_A, defense_A = pipeline.get_recent_form(team_A)
        attack_B, defense_B = pipeline.get_recent_form(team_B)
        
        talent_A = pipeline.get_talent_score(team_A)
        talent_B = pipeline.get_talent_score(team_B)
        
        talent_ratio_A = (talent_A / talent_B) ** 0.4
        talent_ratio_B = (talent_B / talent_A) ** 0.4
        
        lambda_A = (attack_A / self.baseline_home) * (defense_B / self.baseline_away) * ((rating_A / rating_B) ** self.alpha) * talent_ratio_A
        lambda_B = (attack_B / self.baseline_away) * (defense_A / self.baseline_home) * ((rating_B / rating_A) ** self.alpha) * talent_ratio_B
        
        max_goals = 6
        joint_matrix = np.outer(poisson.pmf(range(max_goals), lambda_A), poisson.pmf(range(max_goals), lambda_B))
        
        prob_draw = np.sum(np.diag(joint_matrix))       
        prob_A = np.sum(np.tril(joint_matrix, -1))     
        prob_B = np.sum(np.triu(joint_matrix, 1))      
        
        most_probable_score = np.unravel_index(joint_matrix.argmax(), joint_matrix.shape)

    def generate_exact_score(self, lambda_A, lambda_B):
        """
        Converts the statistical Poisson rate into a concrete match score.
        """
        score_A = np.random.poisson(lambda_A)
        score_B = np.random.poisson(lambda_B)
        return score_A, score_B
        
        return {
            'prob_A_win': round(prob_A * 100, 2),
            'prob_draw': round(prob_draw * 100, 2),
            'prob_B_win': round(prob_B * 100, 2),
            'expected_score': most_probable_score
        }
    
    def generate_exact_score(self, lambda_A, lambda_B):
        score_A = min(np.random.poisson(lambda_A), 5)
        score_B = min(np.random.poisson(lambda_B), 5)
        return score_A, score_B
    
    def generate_exact_score(self, lambda_A, lambda_B):
        """
        Generates a concrete match score using Poisson distribution.
        Truncates at 5 goals to avoid unrealistic tennis scores.
        """
        # np.random.poisson genera el número de eventos (goles)
        score_A = np.random.poisson(lambda_A)
        score_B = np.random.poisson(lambda_B)
        
        # Límite de realismo (máximo 5 goles por equipo)
        return min(score_A, 5), min(score_B, 5)

    def get_lambdas(self, team_A, team_B):
        """
        Helper to return the pre-calculated scoring strengths (lambdas).
        """
        rating_A = self.pipeline.get_live_rating(team_A)
        rating_B = self.pipeline.get_live_rating(team_B)
        attack_A, defense_A = self.pipeline.get_recent_form(team_A)
        attack_B, defense_B = self.pipeline.get_recent_form(team_B)
        talent_A = self.pipeline.get_talent_score(team_A)
        talent_B = self.pipeline.get_talent_score(team_B)
        
        talent_ratio_A = (talent_A / talent_B) ** 0.4
        talent_ratio_B = (talent_B / talent_A) ** 0.4
        
        lambda_A = (attack_A / self.baseline_home) * (defense_B / self.baseline_away) * ((rating_A / rating_B) ** self.alpha) * talent_ratio_A
        lambda_B = (attack_B / self.baseline_away) * (defense_A / self.baseline_home) * ((rating_B / rating_A) ** self.alpha) * talent_ratio_B
        
        return lambda_A, lambda_B