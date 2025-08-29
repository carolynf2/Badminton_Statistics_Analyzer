"""
Badminton Statistics Analyzer
Advanced analytics for badminton match data with SQL queries and statistical analysis
"""

import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import json
from datetime import datetime, timedelta
import statistics

class BadmintonAnalyzer:
    """Advanced badminton statistics analyzer with comprehensive metrics"""
    
    def __init__(self, db_path: str = "badminton_test.db"):
        self.db_path = db_path
        self.conn = None
        self.connect_db()
    
    def connect_db(self):
        """Connect to the badminton database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Execute SQL query and return results as list of dictionaries"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            return []
    
    def get_player_profile(self, player_id: int) -> Dict:
        """Get comprehensive player profile"""
        query = """
        SELECT 
            p.*,
            COUNT(DISTINCT m.match_id) as total_matches,
            SUM(CASE WHEN mp.is_winner = 1 THEN 1 ELSE 0 END) as matches_won,
            ROUND(AVG(CASE WHEN mp.is_winner = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as win_percentage,
            AVG(m.duration_minutes) as avg_match_duration,
            MAX(m.match_date) as last_match_date,
            COUNT(DISTINCT m.tournament_id) as tournaments_played
        FROM players p
        LEFT JOIN match_participants mp ON p.player_id = mp.player_id
        LEFT JOIN matches m ON mp.match_id = m.match_id AND m.status = 'COMPLETED'
        WHERE p.player_id = ?
        GROUP BY p.player_id
        """
        result = self.execute_query(query, (player_id,))
        return result[0] if result else {}
    
    def get_player_statistics_summary(self, player_id: int) -> Dict:
        """Get aggregated statistics for a player across all matches"""
        query = """
        SELECT 
            COUNT(*) as total_matches,
            AVG(total_serves) as avg_serves,
            AVG(service_aces * 1.0 / NULLIF(total_serves, 0)) * 100 as ace_percentage,
            AVG(service_faults * 1.0 / NULLIF(total_serves, 0)) * 100 as fault_percentage,
            AVG(winners) as avg_winners,
            AVG(unforced_errors) as avg_unforced_errors,
            AVG(winners * 1.0 / NULLIF(unforced_errors, 0)) as winner_to_error_ratio,
            AVG(points_won * 1.0 / NULLIF(points_played, 0)) * 100 as points_won_percentage,
            SUM(smashes) as total_smashes,
            SUM(clears) as total_clears,
            SUM(drops) as total_drops,
            SUM(net_shots) as total_net_shots,
            AVG(short_rallies_won * 1.0 / NULLIF(short_rallies_played, 0)) * 100 as short_rally_success,
            AVG(medium_rallies_won * 1.0 / NULLIF(medium_rallies_played, 0)) * 100 as medium_rally_success,
            AVG(long_rallies_won * 1.0 / NULLIF(long_rallies_played, 0)) * 100 as long_rally_success
        FROM match_statistics 
        WHERE player_id = ?
        """
        result = self.execute_query(query, (player_id,))
        return result[0] if result else {}
    
    def get_head_to_head(self, player1_id: int, player2_id: int) -> Dict:
        """Get head-to-head record between two players"""
        query = """
        SELECT 
            h.*,
            p1.first_name || ' ' || p1.last_name as player1_name,
            p2.first_name || ' ' || p2.last_name as player2_name
        FROM head_to_head h
        JOIN players p1 ON h.player1_id = p1.player_id
        JOIN players p2 ON h.player2_id = p2.player_id
        WHERE (h.player1_id = ? AND h.player2_id = ?) OR (h.player1_id = ? AND h.player2_id = ?)
        """
        result = self.execute_query(query, (min(player1_id, player2_id), max(player1_id, player2_id),
                                          min(player1_id, player2_id), max(player1_id, player2_id)))
        return result[0] if result else {}
    
    def get_recent_matches(self, player_id: int, limit: int = 10) -> List[Dict]:
        """Get recent matches for a player"""
        query = """
        SELECT 
            m.*,
            t.tournament_name,
            p_opp.first_name || ' ' || p_opp.last_name as opponent_name,
            p_opp.nationality as opponent_nationality,
            mp.is_winner,
            ms.points_won,
            ms.points_played,
            ms.winners,
            ms.unforced_errors
        FROM matches m
        JOIN match_participants mp ON m.match_id = mp.match_id
        JOIN match_participants mp_opp ON m.match_id = mp_opp.match_id AND mp_opp.player_id != ?
        JOIN players p_opp ON mp_opp.player_id = p_opp.player_id
        JOIN tournaments t ON m.tournament_id = t.tournament_id
        LEFT JOIN match_statistics ms ON m.match_id = ms.match_id AND ms.player_id = ?
        WHERE mp.player_id = ? AND m.status = 'COMPLETED'
        ORDER BY m.match_date DESC, m.match_time DESC
        LIMIT ?
        """
        return self.execute_query(query, (player_id, player_id, player_id, limit))
    
    def get_performance_by_tournament_type(self, player_id: int) -> List[Dict]:
        """Analyze player performance by tournament type"""
        query = """
        SELECT 
            t.tournament_type,
            COUNT(DISTINCT m.match_id) as matches_played,
            SUM(CASE WHEN mp.is_winner = 1 THEN 1 ELSE 0 END) as matches_won,
            ROUND(AVG(CASE WHEN mp.is_winner = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as win_percentage,
            AVG(ms.points_won * 1.0 / NULLIF(ms.points_played, 0)) * 100 as avg_points_won_pct,
            AVG(m.duration_minutes) as avg_match_duration
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.tournament_id
        JOIN match_participants mp ON m.match_id = mp.match_id AND mp.player_id = ?
        LEFT JOIN match_statistics ms ON m.match_id = ms.match_id AND ms.player_id = ?
        WHERE m.status = 'COMPLETED'
        GROUP BY t.tournament_type
        ORDER BY matches_played DESC
        """
        return self.execute_query(query, (player_id, player_id))
    
    def get_shot_distribution_analysis(self, player_id: int) -> Dict:
        """Analyze shot distribution and effectiveness"""
        query = """
        SELECT 
            SUM(smashes) as total_smashes,
            SUM(clears) as total_clears,
            SUM(drops) as total_drops,
            SUM(drives) as total_drives,
            SUM(net_shots) as total_net_shots,
            SUM(lobs) as total_lobs,
            SUM(kills) as total_kills,
            SUM(winners) as total_winners,
            SUM(unforced_errors) as total_unforced_errors,
            COUNT(*) as total_matches
        FROM match_statistics 
        WHERE player_id = ?
        """
        result = self.execute_query(query, (player_id,))[0]
        
        if result and result['total_matches'] > 0:
            total_shots = sum([result[shot] for shot in ['total_smashes', 'total_clears', 'total_drops', 
                                                       'total_drives', 'total_net_shots', 'total_lobs', 'total_kills']])
            
            distribution = {
                'smash_percentage': round((result['total_smashes'] / total_shots) * 100, 2) if total_shots > 0 else 0,
                'clear_percentage': round((result['total_clears'] / total_shots) * 100, 2) if total_shots > 0 else 0,
                'drop_percentage': round((result['total_drops'] / total_shots) * 100, 2) if total_shots > 0 else 0,
                'drive_percentage': round((result['total_drives'] / total_shots) * 100, 2) if total_shots > 0 else 0,
                'net_shot_percentage': round((result['total_net_shots'] / total_shots) * 100, 2) if total_shots > 0 else 0,
                'lob_percentage': round((result['total_lobs'] / total_shots) * 100, 2) if total_shots > 0 else 0,
                'kill_percentage': round((result['total_kills'] / total_shots) * 100, 2) if total_shots > 0 else 0,
                'total_shots': total_shots,
                'winner_to_error_ratio': round(result['total_winners'] / result['total_unforced_errors'], 2) if result['total_unforced_errors'] > 0 else float('inf')
            }
            
            return {**result, **distribution}
        
        return result
    
    def get_rally_length_analysis(self, player_id: int) -> Dict:
        """Analyze performance by rally length"""
        query = """
        SELECT 
            SUM(short_rallies_played) as total_short_rallies,
            SUM(short_rallies_won) as short_rallies_won,
            SUM(medium_rallies_played) as total_medium_rallies,
            SUM(medium_rallies_won) as medium_rallies_won,
            SUM(long_rallies_played) as total_long_rallies,
            SUM(long_rallies_won) as long_rallies_won,
            COUNT(*) as total_matches
        FROM match_statistics 
        WHERE player_id = ?
        """
        result = self.execute_query(query, (player_id,))[0]
        
        if result:
            analysis = {
                'short_rally_win_rate': round((result['short_rallies_won'] / result['total_short_rallies']) * 100, 2) if result['total_short_rallies'] > 0 else 0,
                'medium_rally_win_rate': round((result['medium_rallies_won'] / result['total_medium_rallies']) * 100, 2) if result['total_medium_rallies'] > 0 else 0,
                'long_rally_win_rate': round((result['long_rallies_won'] / result['total_long_rallies']) * 100, 2) if result['total_long_rallies'] > 0 else 0,
                'preferred_rally_length': None
            }
            
            # Determine preferred rally length
            win_rates = [
                ('short', analysis['short_rally_win_rate']),
                ('medium', analysis['medium_rally_win_rate']),
                ('long', analysis['long_rally_win_rate'])
            ]
            analysis['preferred_rally_length'] = max(win_rates, key=lambda x: x[1])[0]
            
            return {**result, **analysis}
        
        return result
    
    def get_tournament_performance(self, tournament_id: int) -> Dict:
        """Get comprehensive tournament statistics"""
        query = """
        SELECT 
            t.*,
            COUNT(DISTINCT m.match_id) as total_matches,
            COUNT(DISTINCT mp.player_id) as total_players,
            AVG(m.duration_minutes) as avg_match_duration,
            MAX(m.duration_minutes) as longest_match,
            MIN(m.duration_minutes) as shortest_match
        FROM tournaments t
        LEFT JOIN matches m ON t.tournament_id = m.tournament_id AND m.status = 'COMPLETED'
        LEFT JOIN match_participants mp ON m.match_id = mp.match_id
        WHERE t.tournament_id = ?
        GROUP BY t.tournament_id
        """
        return self.execute_query(query, (tournament_id,))[0] if self.execute_query(query, (tournament_id,)) else {}
    
    def get_top_performers(self, metric: str = 'win_percentage', limit: int = 10, min_matches: int = 5) -> List[Dict]:
        """Get top performers by specified metric"""
        
        valid_metrics = {
            'win_percentage': 'AVG(CASE WHEN mp.is_winner = 1 THEN 1.0 ELSE 0.0 END) * 100',
            'total_matches': 'COUNT(DISTINCT m.match_id)',
            'avg_points_won': 'AVG(ms.points_won * 1.0 / NULLIF(ms.points_played, 0)) * 100',
            'winner_ratio': 'AVG(ms.winners * 1.0 / NULLIF(ms.unforced_errors, 0))',
            'ace_percentage': 'AVG(ms.service_aces * 1.0 / NULLIF(ms.total_serves, 0)) * 100'
        }
        
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric. Choose from: {list(valid_metrics.keys())}")
        
        query = f"""
        SELECT 
            p.player_id,
            p.first_name || ' ' || p.last_name as player_name,
            p.nationality,
            p.gender,
            p.world_ranking,
            COUNT(DISTINCT m.match_id) as total_matches,
            SUM(CASE WHEN mp.is_winner = 1 THEN 1 ELSE 0 END) as matches_won,
            ROUND(AVG(CASE WHEN mp.is_winner = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as win_percentage,
            ROUND({valid_metrics[metric]}, 2) as metric_value
        FROM players p
        JOIN match_participants mp ON p.player_id = mp.player_id
        JOIN matches m ON mp.match_id = m.match_id AND m.status = 'COMPLETED'
        LEFT JOIN match_statistics ms ON p.player_id = ms.player_id AND m.match_id = ms.match_id
        GROUP BY p.player_id, p.first_name, p.last_name, p.nationality, p.gender, p.world_ranking
        HAVING COUNT(DISTINCT m.match_id) >= ?
        ORDER BY metric_value DESC
        LIMIT ?
        """
        
        return self.execute_query(query, (min_matches, limit))
    
    def get_match_insights(self, match_id: int) -> Dict:
        """Get detailed insights for a specific match"""
        # Basic match info
        match_query = """
        SELECT 
            m.*,
            t.tournament_name,
            t.location,
            t.tournament_type
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.tournament_id
        WHERE m.match_id = ?
        """
        match_info = self.execute_query(match_query, (match_id,))
        if not match_info:
            return {}
        
        match_info = match_info[0]
        
        # Players in the match
        players_query = """
        SELECT 
            mp.*,
            p.first_name || ' ' || p.last_name as player_name,
            p.nationality,
            p.world_ranking
        FROM match_participants mp
        JOIN players p ON mp.player_id = p.player_id
        WHERE mp.match_id = ?
        ORDER BY mp.team_position
        """
        players = self.execute_query(players_query, (match_id,))
        
        # Game results
        games_query = """
        SELECT * FROM games 
        WHERE match_id = ? 
        ORDER BY game_number
        """
        games = self.execute_query(games_query, (match_id,))
        
        # Match statistics
        stats_query = """
        SELECT 
            ms.*,
            p.first_name || ' ' || p.last_name as player_name
        FROM match_statistics ms
        JOIN players p ON ms.player_id = p.player_id
        WHERE ms.match_id = ?
        """
        statistics = self.execute_query(stats_query, (match_id,))
        
        return {
            'match_info': match_info,
            'players': players,
            'games': games,
            'statistics': statistics
        }
    
    def compare_players(self, player_ids: List[int]) -> Dict:
        """Compare multiple players across key metrics"""
        if len(player_ids) < 2:
            raise ValueError("At least 2 players required for comparison")
        
        comparisons = {}
        
        for player_id in player_ids:
            profile = self.get_player_profile(player_id)
            stats = self.get_player_statistics_summary(player_id)
            shot_analysis = self.get_shot_distribution_analysis(player_id)
            rally_analysis = self.get_rally_length_analysis(player_id)
            
            comparisons[player_id] = {
                'name': f"{profile.get('first_name', '')} {profile.get('last_name', '')}",
                'nationality': profile.get('nationality', ''),
                'ranking': profile.get('world_ranking'),
                'matches_played': profile.get('total_matches', 0),
                'win_percentage': profile.get('win_percentage', 0),
                'points_won_percentage': stats.get('points_won_percentage', 0),
                'winner_to_error_ratio': stats.get('winner_to_error_ratio', 0),
                'ace_percentage': stats.get('ace_percentage', 0),
                'preferred_rally_length': rally_analysis.get('preferred_rally_length', 'unknown'),
                'shot_distribution': {
                    'smash': shot_analysis.get('smash_percentage', 0),
                    'clear': shot_analysis.get('clear_percentage', 0),
                    'drop': shot_analysis.get('drop_percentage', 0),
                    'net_shot': shot_analysis.get('net_shot_percentage', 0)
                }
            }
        
        return comparisons
    
    def get_performance_trends(self, player_id: int, days: int = 90) -> List[Dict]:
        """Analyze performance trends over time"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        query = """
        SELECT 
            DATE(m.match_date) as match_date,
            mp.is_winner,
            m.duration_minutes,
            ms.points_won * 1.0 / NULLIF(ms.points_played, 0) * 100 as points_won_pct,
            ms.winners,
            ms.unforced_errors,
            ms.service_aces * 1.0 / NULLIF(ms.total_serves, 0) * 100 as ace_pct
        FROM matches m
        JOIN match_participants mp ON m.match_id = mp.match_id AND mp.player_id = ?
        LEFT JOIN match_statistics ms ON m.match_id = ms.match_id AND ms.player_id = ?
        WHERE m.match_date >= ? AND m.status = 'COMPLETED'
        ORDER BY m.match_date DESC
        """
        
        return self.execute_query(query, (player_id, player_id, cutoff_date))
    
    def generate_scouting_report(self, player_id: int) -> Dict:
        """Generate comprehensive scouting report for a player"""
        profile = self.get_player_profile(player_id)
        stats_summary = self.get_player_statistics_summary(player_id)
        shot_analysis = self.get_shot_distribution_analysis(player_id)
        rally_analysis = self.get_rally_length_analysis(player_id)
        performance_by_tournament = self.get_performance_by_tournament_type(player_id)
        recent_matches = self.get_recent_matches(player_id, 5)
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if stats_summary.get('winner_to_error_ratio', 0) > 1.5:
            strengths.append("Excellent shot accuracy and low error rate")
        elif stats_summary.get('winner_to_error_ratio', 0) < 0.8:
            weaknesses.append("High unforced error rate")
        
        if stats_summary.get('ace_percentage', 0) > 8:
            strengths.append("Strong serving game")
        elif stats_summary.get('ace_percentage', 0) < 3:
            weaknesses.append("Weak serving game")
        
        if shot_analysis.get('smash_percentage', 0) > 25:
            strengths.append("Aggressive attacking style")
        
        if rally_analysis.get('long_rally_win_rate', 0) > rally_analysis.get('short_rally_win_rate', 0):
            strengths.append("Strong endurance and long rally performance")
        else:
            strengths.append("Quick point finishing ability")
        
        return {
            'player_info': {
                'name': f"{profile.get('first_name', '')} {profile.get('last_name', '')}",
                'nationality': profile.get('nationality', ''),
                'age': self._calculate_age(profile.get('birth_date')),
                'ranking': profile.get('world_ranking'),
                'dominant_hand': profile.get('dominant_hand')
            },
            'performance_overview': {
                'total_matches': profile.get('total_matches', 0),
                'win_percentage': profile.get('win_percentage', 0),
                'recent_form': self._calculate_recent_form(recent_matches)
            },
            'playing_style': {
                'shot_distribution': shot_analysis,
                'rally_preference': rally_analysis,
                'strengths': strengths,
                'weaknesses': weaknesses
            },
            'tournament_performance': performance_by_tournament,
            'recent_matches': recent_matches[:5]
        }
    
    def _calculate_age(self, birth_date: str) -> Optional[int]:
        """Calculate age from birth date"""
        if not birth_date:
            return None
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.now()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return None
    
    def _calculate_recent_form(self, recent_matches: List[Dict]) -> str:
        """Calculate recent form based on last 5 matches"""
        if not recent_matches:
            return "No recent data"
        
        wins = sum(1 for match in recent_matches if match.get('is_winner'))
        total = len(recent_matches)
        win_rate = (wins / total) * 100
        
        if win_rate >= 80:
            return "Excellent"
        elif win_rate >= 60:
            return "Good"
        elif win_rate >= 40:
            return "Average"
        else:
            return "Poor"
    
    def export_analysis_to_json(self, analysis_data: Dict, filename: str):
        """Export analysis results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(analysis_data, f, indent=2, default=str)
            print(f"Analysis exported to {filename}")
        except Exception as e:
            print(f"Error exporting analysis: {e}")

if __name__ == "__main__":
    # Example usage
    analyzer = BadmintonAnalyzer("badminton_test.db")
    
    # Get top performers
    print("Top 5 players by win percentage:")
    top_players = analyzer.get_top_performers('win_percentage', limit=5)
    for player in top_players:
        print(f"  {player['player_name']} ({player['nationality']}): {player['win_percentage']}%")
    
    # Generate scouting report for first player
    if top_players:
        player_id = top_players[0]['player_id']
        scouting_report = analyzer.generate_scouting_report(player_id)
        print(f"\nScouting Report for {scouting_report['player_info']['name']}:")
        print(f"  Matches: {scouting_report['performance_overview']['total_matches']}")
        print(f"  Win Rate: {scouting_report['performance_overview']['win_percentage']}%")
        print(f"  Strengths: {', '.join(scouting_report['playing_style']['strengths'][:2])}")
    
    analyzer.close_db()