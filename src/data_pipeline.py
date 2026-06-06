import pandas as pd
import numpy as np
from src.scraper import WebScraper 

class DataPipeline:
    def __init__(self, data_dir="data"):
        print(" Loading local datasets...")
        
        self.matches = pd.read_csv(f"{data_dir}/results.csv")
        self.goalscorers = pd.read_csv(f"{data_dir}/goalscorers.csv")
        self.matches['date'] = pd.to_datetime(self.matches['date'])
        self.goalscorers['date'] = pd.to_datetime(self.goalscorers['date'])
        self.cutoff_date = '2023-01-01'
        self.scorer_cutoff = '2018-01-01'
        self.matches_cycle = self.matches[self.matches['date'] >= self.cutoff_date].copy()
        self.goalscorers_cycle = self.goalscorers[self.goalscorers['date'] >= self.scorer_cutoff].copy()
        
        self.scraper = WebScraper()
        self.form_cache = {}
        self.scorers_cache = {}
        self.backup_ratings_2026 = {}
        
        #  DATA EXTRACTION: Live June 2026 ratings mapped from user verification screens ( June - 6 )
        self.backup_ratings_2026 = {
            'Argentina': 1874.81, 'Spain': 1873.01, 'France': 1869.43, 
            'England': 1825.97, 'Portugal': 1763.83, 'Brazil': 1762.66, 
            'Morocco': 1756.94, 'Netherlands': 1751.10, 'Belgium': 1739.55, 
            'Germany': 1731.30, 'Croatia': 1712.24, 'Italy': 1701.77, 
            'Colombia': 1695.99, 'Mexico': 1687.48, 'USA': 1675.70, 
            'Uruguay': 1673.07, 'Japan': 1661.58, 'South Korea': 1591.63, 
            'Canada': 1564.48
        }
        self.form_cache = {}
        self.scorers_cache = {}

    def normalize_name(self, team_name):
        """
        Data Engineering Core: Standardizes all incoming team names to English
        to guarantee perfect Join Keys across CSVs, Scrapers, and Dashboards.
        """
        synonyms = {
            'Francia': 'France', 
            'Alemania': 'Germany', 
            'España': 'Spain',
            'Inglaterra': 'England', 
            'Brasil': 'Brazil', 
            'Países Bajos': 'Netherlands',
            'Holanda': 'Netherlands', 
            'Bélgica': 'Belgium', 
            'Italia': 'Italy',
            'Corea del Sur': 'South Korea', 
            'Korea Republic': 'South Korea',
            'Estados Unidos': 'USA', 
            'United States': 'USA',
            'México': 'Mexico',
            'Japón': 'Japan',
            'Marruecos': 'Morocco',
            'Turquía': 'Turkey'
        }
        clean_name = str(team_name).strip()
        return synonyms.get(clean_name, clean_name)

    def get_talent_score(self, team_name):
        norm_name = self.normalize_name(team_name)
        
        elite_talent = {
            'England': 1470.0, 'France': 1230.0, 'Portugal': 1050.0,
            'Brazil': 1040.0, 'Spain': 960.0, 'Germany': 870.0,
            'Argentina': 850.0, 'Italy': 750.0, 'Netherlands': 600.0,
            'Belgium': 580.0, 'Uruguay': 480.0, 'Colombia': 280.0,
            'Senegal': 270.0, 'Ivory Coast': 250.0, 'Mexico': 220.0,
            'USA': 340.0
        }
        
        if norm_name in elite_talent:
            return elite_talent[norm_name]
            
        return self.scraper.fetch_transfermarkt_value(norm_name)
    
    def get_live_rating(self, team_name):
        norm_name = self.normalize_name(team_name)
        safety_ratings = {
            'Germany': 1900.0, 'France': 2100.0, 'Argentina': 2150.0, 
            'Brazil': 2050.0, 'England': 2000.0, 'Spain': 1950.0
        }
        
        if norm_name in safety_ratings:
            return safety_ratings[norm_name]
            
        return float(self.backup_ratings_2026.get(norm_name, 1450.0))

    def get_baseline_goals(self):
        """Calculates the global average of goals scored by home and away teams."""
        baseline_home = self.matches_cycle['home_score'].mean()
        baseline_away = self.matches_cycle['away_score'].mean()
        return baseline_home, baseline_away
        
        normalized_name = team_synonyms.get(team_name, team_name)
        
        try:
            backup_url = "https://raw.githubusercontent.com/datasets/fifa-world-ranking/master/data/fifa_ranking.csv"
            df_live = pd.read_csv(backup_url, nrows=10) 
            
            return float(self.backup_ratings_2026.get(normalized_name, 1450.0))
            
        except Exception:
            return float(self.backup_ratings_2026.get(normalized_name, 1450.0))

    def precompute_tournament_metrics(self, teams_list):
        """
        Data Engineering Optimization: Pre-calculates performance metrics and 
        top goalscorers for all teams to achieve near-instant memory retrieval.
        """
        self.form_cache = {}
        self.scorers_cache = {}
        for team in teams_list:
            h_data = self.matches_cycle[self.matches_cycle['home_team'] == team][['date', 'home_score', 'away_score']].rename(columns={'home_score': 'scored', 'away_score': 'conceded'})
            a_data = self.matches_cycle[self.matches_cycle['away_team'] == team][['date', 'away_score', 'home_score']].rename(columns={'away_score': 'scored', 'home_score': 'conceded'})
            combined = pd.concat([h_data, a_data]).sort_values('date', ascending=False).head(15)
        
        for team in teams_list:
            home_m = self.matches_cycle[self.matches_cycle['home_team'] == team]
            away_m = self.matches_cycle[self.matches_cycle['away_team'] == team]
            
            h_data = home_m[['date', 'home_score', 'away_score']].rename(columns={'home_score': 'scored', 'away_score': 'conceded'})
            a_data = away_m[['date', 'away_score', 'home_score']].rename(columns={'away_score': 'scored', 'home_score': 'conceded'})
            
            combined = pd.concat([h_data, a_data]).sort_values('date', ascending=False).head(15)
            
            if combined.empty:
                self.form_cache[team] = (1.2, 1.1)
            else:
                weights = np.linspace(1.5, 0.5, len(combined))
                avg_scored = np.average(combined['scored'], weights=weights)
                avg_conceded = np.average(combined['conceded'], weights=weights)
                self.form_cache[team] = (max(0.1, avg_scored), max(0.1, avg_conceded))
            
            team_goals = self.goalscorers_cycle[self.goalscorers_cycle['team'] == team]
            if not team_goals.empty:
                self.scorers_cache[team] = {team_goals['scorer'].value_counts().idxmax(): 1}
            else:
                self.scorers_cache[team] = {"Unknown Star": 1}

    def get_recent_form(self, team_name, n_matches=15):
        norm_name = self.normalize_name(team_name)
        attack, defense = self.form_cache.get(norm_name, (1.2, 1.1))
        smoothed_attack = (attack * 0.3) + (1.2 * 0.85)
        smoothed_defense = (defense * 0.15) + (1.1 * 0.85)
        
        return smoothed_attack, smoothed_defense

    def get_active_scorers(self, team_name, top_n=1):
        fallback_stars = {
            'France': 'Kylian Mbappé', 'Argentina': 'Lionel Messi',
            'England': 'Harry Kane', 'Brazil': 'Vinícius Júnior',
            'Portugal': 'Cristiano Ronaldo', 'Spain': 'Lamine Yamal',
            'Belgium': 'Romelu Lukaku', 'Germany': 'Jamal Musiala',
            'Netherlands': 'Cody Gakpo', 'Uruguay': 'Darwin Núñez',
            'Colombia': 'Luis Díaz', 'Mexico': 'Santiago Giménez',
            'USA': 'Christian Pulisic'
        }
        
        if team_name in self.scorers_cache:
            cached_scorer = list(self.scorers_cache[team_name].keys())[0]
            
            bad_names = ["Star Striker", "Unknown Star", "Legendary Player", "No Active Scorer Found"]
            
            if cached_scorer not in bad_names:
                return self.scorers_cache[team_name]
        
        final_name = fallback_stars.get(team_name, f"Star of {team_name}")
        return {final_name: 1}