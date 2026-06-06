import random

class TournamentSimulator:
    def __init__(self, groups, model, pipeline): 
        self.groups = groups
        self.model = model
        self.pipeline = pipeline
        self.match_cache = {}

    def _get_cached_probabilities(self, team_1, team_2):
        match_key = tuple(sorted([team_1, team_2]))
        
        if match_key not in self.match_cache:
            self.match_cache[match_key] = self.model.predict_match_probabilities(team_1, team_2, self.pipeline)
        probs = self.match_cache[match_key]
        if probs is None:
            return {
                'expected_score': [1, 1],
                'prob_A_win': 33.3,
                'prob_B_win': 33.3,
                'prob_draw': 33.4
            }
            
        return probs

    def simulate_group_stage(self):
        """Simulates all 12 groups, tracks Goal Difference, and advances 32 teams."""
        all_teams_stats = {}
        first_places, second_places, third_places = [], [], []
        
        for group_name, teams in self.groups.items():
            stats = {team: {'pts': 0, 'gf': 0, 'gc': 0, 'gd': 0} for team in teams}
            
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    t1, t2 = teams[i], teams[j]
                    probs = self._get_cached_probabilities(t1, t2)
                    
                    score_t1, score_t2 = probs['expected_score'][0], probs['expected_score'][1]
                    
                    roll = random.uniform(0, 100)
                    if t1 == sorted([t1, t2])[0]:
                        win_p = probs['prob_A_win']
                    else:
                        win_p = probs['prob_B_win']
                        score_t1, score_t2 = score_t2, score_t1
                        
                    if roll < win_p:
                        stats[t1]['pts'] += 3
                        stats[t1]['gf'] += max(score_t1, 1)
                        stats[t2]['gc'] += max(score_t1, 1)
                    elif roll < (win_p + probs['prob_draw']):
                        stats[t1]['pts'] += 1
                        stats[t2]['pts'] += 1
                        stats[t1]['gf'] += score_t1
                        stats[t2]['gf'] += score_t1
                        stats[t1]['gc'] += score_t1
                        stats[t2]['gc'] += score_t1
                    else:
                        stats[t2]['pts'] += 3
                        stats[t2]['gf'] += max(score_t2, 1)
                        stats[t1]['gc'] += max(score_t2, 1)
                        
            for t in teams:
                stats[t]['gd'] = stats[t]['gf'] - stats[t]['gc']
                all_teams_stats[t] = stats[t]
                
            ranked_group = sorted(stats.items(), key=lambda x: (x[1]['pts'], x[1]['gd'], x[1]['gf']), reverse=True)
            
            first_places.append(ranked_group[0][0])
            second_places.append(ranked_group[1][0])
            third_places.append(ranked_group[2][0])

        ranked_thirds = sorted(third_places, key=lambda t: (all_teams_stats[t]['pts'], all_teams_stats[t]['gd']), reverse=True)
        best_8_thirds = ranked_thirds[:8]
        
        worst_team = sorted(all_teams_stats.items(), key=lambda x: (x[1]['pts'], x[1]['gd'], x[1]['gf']))[0][0]
        
        qualified_32 = first_places + second_places + best_8_thirds
        return qualified_32, worst_team

    def simulate_knockout_match(self, team_A, team_B):
        probs = self._get_cached_probabilities(team_A, team_B)
        win_p = probs['prob_A_win'] if team_A == sorted([team_A, team_B])[0] else probs['prob_B_win']
        effective_probability_A = win_p + (probs['prob_draw'] / 2)
        
        if random.uniform(0, 100) < effective_probability_A:
            return team_A, team_B
        else:
            return team_B, team_A

    def simulate_bracket(self, qualified_32):
        """Simulates from Round of 32 down to the Final and 3rd Place Match."""
        random.shuffle(qualified_32)
        
        round_16 = [self.simulate_knockout_match(qualified_32[i], qualified_32[i+1])[0] for i in range(0, 32, 2)]
        
        quarter_finalists = [self.simulate_knockout_match(round_16[i], round_16[i+1])[0] for i in range(0, 16, 2)]
        
        semifinalists = [self.simulate_knockout_match(quarter_finalists[i], quarter_finalists[i+1])[0] for i in range(0, 8, 2)]
        
        finalist_1, loser_semi_1 = self.simulate_knockout_match(semifinalists[0], semifinalists[1])
        finalist_2, loser_semi_2 = self.simulate_knockout_match(semifinalists[2], semifinalists[3])
        
        third_place, fourth_place = self.simulate_knockout_match(loser_semi_1, loser_semi_2)
        
        champion, runner_up = self.simulate_knockout_match(finalist_1, finalist_2)
        
        return {
            'champion': champion,
            'runner_up': runner_up,
            'third_place': third_place,
            'fourth_place': fourth_place,
            'top_4': semifinalists
        }