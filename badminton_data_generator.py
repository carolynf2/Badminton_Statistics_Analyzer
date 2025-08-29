"""
Badminton Statistics Data Generator
Generates synthetic badminton match data for testing the statistics analyzer
"""

import sqlite3
import random
import datetime
from typing import List, Dict, Tuple
import numpy as np

class BadmintonDataGenerator:
    """Generates realistic synthetic badminton match data"""
    
    def __init__(self, db_path: str = "badminton.db"):
        self.db_path = db_path
        self.conn = None
        
        # Real player names and countries for realistic data
        self.male_players = [
            ("Viktor", "Axelsen", "DEN"),
            ("Kento", "Momota", "JPN"),
            ("Anders", "Antonsen", "DEN"),
            ("Chou", "Tien-chen", "TPE"),
            ("Anthony", "Ginting", "INA"),
            ("Jonatan", "Christie", "INA"),
            ("Lee", "Zii Jia", "MAS"),
            ("Loh", "Kean Yew", "SGP"),
            ("Kidambi", "Srikanth", "IND"),
            ("HS", "Prannoy", "IND"),
            ("Lakshya", "Sen", "IND"),
            ("Lin", "Dan", "CHN"),
            ("Chen", "Long", "CHN"),
            ("Shi", "Yuqi", "CHN"),
            ("Zhao", "Junpeng", "CHN")
        ]
        
        self.female_players = [
            ("Akane", "Yamaguchi", "JPN"),
            ("Tai", "Tzu-ying", "TPE"),
            ("Carolina", "Marin", "ESP"),
            ("An", "Se-young", "KOR"),
            ("Ratchanok", "Intanon", "THA"),
            ("Pusarla", "Sindhu", "IND"),
            ("Nozomi", "Okuhara", "JPN"),
            ("Mia", "Blichfeldt", "DEN"),
            ("He", "Bingjiao", "CHN"),
            ("Wang", "Zhiyi", "CHN"),
            ("Chen", "Yufei", "CHN"),
            ("Saina", "Nehwal", "IND"),
            ("Gregoria", "Tunjung", "INA"),
            ("Fitriani", "Fitriani", "INA"),
            ("Busanan", "Ongbamrungphan", "THA")
        ]
        
        self.tournaments = [
            ("All England Open", "Birmingham", "GBR", "BWF_SUPER_1000"),
            ("China Open", "Changzhou", "CHN", "BWF_SUPER_1000"),
            ("Denmark Open", "Odense", "DEN", "BWF_SUPER_750"),
            ("French Open", "Paris", "FRA", "BWF_SUPER_750"),
            ("Indonesia Open", "Jakarta", "INA", "BWF_SUPER_1000"),
            ("Japan Open", "Tokyo", "JPN", "BWF_SUPER_750"),
            ("Malaysia Open", "Kuala Lumpur", "MAS", "BWF_SUPER_750"),
            ("Singapore Open", "Singapore", "SGP", "BWF_SUPER_500"),
            ("Thailand Open", "Bangkok", "THA", "BWF_SUPER_500"),
            ("India Open", "New Delhi", "IND", "BWF_SUPER_500"),
            ("World Championships", "Various", "BWF", "WORLD_CHAMPIONSHIPS"),
            ("Olympics", "Various", "IOC", "OLYMPICS")
        ]
        
        self.shot_types = ["SMASH", "CLEAR", "DROP", "DRIVE", "NET_SHOT", "LOB", "KILL", "ERROR", "FAULT"]
        self.rounds = ["QUALIFYING", "R64", "R32", "R16", "QF", "SF", "F"]
    
    def connect_db(self):
        """Connect to SQLite database and create schema"""
        self.conn = sqlite3.connect(self.db_path)
        
        # Read and execute schema
        try:
            with open('badminton_schema.sql', 'r') as f:
                schema = f.read()
                self.conn.executescript(schema)
        except FileNotFoundError:
            print("Warning: Schema file not found. Make sure badminton_schema.sql exists.")
            
        self.conn.commit()
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def generate_players(self, num_male: int = 50, num_female: int = 50):
        """Generate player data"""
        players = []
        
        # Add male players
        for i in range(num_male):
            if i < len(self.male_players):
                first, last, country = self.male_players[i]
            else:
                first = f"Player{i+1}"
                last = f"Male"
                country = random.choice(["USA", "GBR", "FRA", "GER", "ESP", "ITA"])
            
            birth_year = random.randint(1990, 2005)
            birth_date = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            
            player = {
                'player_id': i + 1,
                'first_name': first,
                'last_name': last,
                'nationality': country,
                'birth_date': birth_date,
                'gender': 'M',
                'height_cm': random.randint(165, 190),
                'weight_kg': random.randint(60, 85),
                'dominant_hand': random.choice(['R', 'L']),
                'world_ranking': i + 1 if i < 100 else None
            }
            players.append(player)
        
        # Add female players
        for i in range(num_female):
            if i < len(self.female_players):
                first, last, country = self.female_players[i]
            else:
                first = f"Player{i+1}"
                last = f"Female"
                country = random.choice(["USA", "GBR", "FRA", "GER", "ESP", "ITA"])
            
            birth_year = random.randint(1990, 2005)
            birth_date = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            
            player = {
                'player_id': num_male + i + 1,
                'first_name': first,
                'last_name': last,
                'nationality': country,
                'birth_date': birth_date,
                'gender': 'F',
                'height_cm': random.randint(155, 180),
                'weight_kg': random.randint(50, 75),
                'dominant_hand': random.choice(['R', 'L']),
                'world_ranking': i + 1 if i < 100 else None
            }
            players.append(player)
        
        # Insert players into database
        insert_query = '''
            INSERT INTO players (player_id, first_name, last_name, nationality, birth_date, 
                               gender, height_cm, weight_kg, dominant_hand, world_ranking)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        for player in players:
            self.conn.execute(insert_query, (
                player['player_id'], player['first_name'], player['last_name'],
                player['nationality'], player['birth_date'], player['gender'],
                player['height_cm'], player['weight_kg'], player['dominant_hand'],
                player['world_ranking']
            ))
        
        self.conn.commit()
        return players
    
    def generate_tournaments(self, year: int = 2024, num_tournaments: int = 10):
        """Generate tournament data"""
        tournaments = []
        
        for i in range(min(num_tournaments, len(self.tournaments))):
            name, location, country, tournament_type = self.tournaments[i]
            
            # Generate random dates within the year
            start_month = random.randint(1, 12)
            start_day = random.randint(1, 28)
            start_date = f"{year}-{start_month:02d}-{start_day:02d}"
            
            # Tournament typically lasts 5-7 days
            duration = random.randint(5, 7)
            end_date = (datetime.datetime(year, start_month, start_day) + 
                       datetime.timedelta(days=duration)).strftime("%Y-%m-%d")
            
            tournament = {
                'tournament_id': i + 1,
                'tournament_name': name,
                'location': location,
                'country': country,
                'tournament_type': tournament_type,
                'surface': random.choice(['WOOD', 'SYNTHETIC']),
                'prize_money': random.randint(100000, 1500000) if tournament_type != 'OTHER' else 50000,
                'start_date': start_date,
                'end_date': end_date,
                'status': 'COMPLETED'
            }
            tournaments.append(tournament)
        
        # Insert tournaments into database
        insert_query = '''
            INSERT INTO tournaments (tournament_id, tournament_name, location, country, 
                                   tournament_type, surface, prize_money, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        for tournament in tournaments:
            self.conn.execute(insert_query, (
                tournament['tournament_id'], tournament['tournament_name'], tournament['location'],
                tournament['country'], tournament['tournament_type'], tournament['surface'],
                tournament['prize_money'], tournament['start_date'], tournament['end_date'],
                tournament['status']
            ))
        
        self.conn.commit()
        return tournaments
    
    def generate_matches(self, tournaments: List[Dict], players: List[Dict], matches_per_tournament: int = 20):
        """Generate match data"""
        matches = []
        match_id = 1
        
        male_players = [p for p in players if p['gender'] == 'M']
        female_players = [p for p in players if p['gender'] == 'F']
        
        for tournament in tournaments:
            tournament_start = datetime.datetime.strptime(tournament['start_date'], "%Y-%m-%d")
            tournament_end = datetime.datetime.strptime(tournament['end_date'], "%Y-%m-%d")
            tournament_duration = (tournament_end - tournament_start).days
            
            for match_num in range(matches_per_tournament):
                # Random match date within tournament period
                match_date = tournament_start + datetime.timedelta(
                    days=random.randint(0, tournament_duration)
                )
                
                # Generate match details
                match_type = random.choice(['MS', 'WS'])  # Focus on singles for simplicity
                
                if match_type == 'MS':
                    available_players = male_players
                else:
                    available_players = female_players
                
                if len(available_players) < 2:
                    continue
                
                # Select two different players
                player1, player2 = random.sample(available_players, 2)
                
                # Determine winner (bias towards lower ranking/higher skill)
                if player1.get('world_ranking') and player2.get('world_ranking'):
                    # Lower ranking number = higher skill, more likely to win
                    prob_p1_wins = player2['world_ranking'] / (player1['world_ranking'] + player2['world_ranking'])
                else:
                    prob_p1_wins = 0.5
                
                winner_id = player1['player_id'] if random.random() < prob_p1_wins else player2['player_id']
                
                match = {
                    'match_id': match_id,
                    'tournament_id': tournament['tournament_id'],
                    'match_date': match_date.strftime("%Y-%m-%d"),
                    'match_time': f"{random.randint(9,20):02d}:{random.choice(['00','30']):02d}:00",
                    'round': random.choice(self.rounds),
                    'court': f"Court {random.randint(1,8)}",
                    'match_type': match_type,
                    'best_of': 3,
                    'duration_minutes': random.randint(25, 90),
                    'winner_id': winner_id,
                    'status': 'COMPLETED',
                    'temperature_celsius': random.randint(18, 26),
                    'humidity_percent': random.randint(40, 80),
                    'players': [player1, player2]
                }
                
                matches.append(match)
                match_id += 1
        
        # Insert matches into database
        insert_match_query = '''
            INSERT INTO matches (match_id, tournament_id, match_date, match_time, round, 
                               court, match_type, best_of, duration_minutes, winner_id, status,
                               temperature_celsius, humidity_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        insert_participant_query = '''
            INSERT INTO match_participants (participant_id, match_id, player_id, partner_id, 
                                          team_position, is_winner)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        participant_id = 1
        for match in matches:
            # Insert match
            self.conn.execute(insert_match_query, (
                match['match_id'], match['tournament_id'], match['match_date'],
                match['match_time'], match['round'], match['court'],
                match['match_type'], match['best_of'], match['duration_minutes'],
                match['winner_id'], match['status'], match['temperature_celsius'],
                match['humidity_percent']
            ))
            
            # Insert participants
            for i, player in enumerate(match['players']):
                is_winner = player['player_id'] == match['winner_id']
                self.conn.execute(insert_participant_query, (
                    participant_id, match['match_id'], player['player_id'],
                    None, i + 1, is_winner
                ))
                participant_id += 1
        
        self.conn.commit()
        return matches
    
    def generate_game_results(self, matches: List[Dict]):
        """Generate game-by-game results for matches"""
        games = []
        game_id = 1
        
        for match in matches:
            # Determine number of games (2 or 3 for best of 3)
            num_games = random.choice([2, 3])
            winner_id = match['winner_id']
            
            winner_games = 0
            loser_games = 0
            
            if num_games == 2:
                winner_games = 2
                loser_games = 0
            else:  # num_games == 3
                winner_games = 2
                loser_games = 1
            
            games_won_by_winner = 0
            
            for game_num in range(1, num_games + 1):
                # Determine if winner wins this game
                if games_won_by_winner < winner_games:
                    if num_games - game_num + 1 <= winner_games - games_won_by_winner:
                        # Must win remaining games
                        winner_wins_game = True
                    else:
                        # Can afford to lose this game
                        winner_wins_game = random.choice([True, False])
                else:
                    winner_wins_game = False
                
                if winner_wins_game:
                    winner_score = 21
                    loser_score = random.randint(10, 19)
                    winner_team = 1 if match['players'][0]['player_id'] == winner_id else 2
                    games_won_by_winner += 1
                else:
                    loser_score = 21
                    winner_score = random.randint(10, 19)
                    winner_team = 2 if match['players'][0]['player_id'] == winner_id else 1
                
                # Assign scores to teams
                if winner_team == 1:
                    team1_score = winner_score if winner_wins_game else loser_score
                    team2_score = loser_score if winner_wins_game else winner_score
                else:
                    team1_score = loser_score if winner_wins_game else winner_score
                    team2_score = winner_score if winner_wins_game else loser_score
                
                game = {
                    'game_id': game_id,
                    'match_id': match['match_id'],
                    'game_number': game_num,
                    'team1_score': team1_score,
                    'team2_score': team2_score,
                    'winner_team': winner_team,
                    'duration_minutes': random.randint(8, 25),
                    'max_rally_length': random.randint(15, 45)
                }
                
                games.append(game)
                game_id += 1
        
        # Insert games into database
        insert_query = '''
            INSERT INTO games (game_id, match_id, game_number, team1_score, team2_score,
                             winner_team, duration_minutes, max_rally_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        for game in games:
            self.conn.execute(insert_query, (
                game['game_id'], game['match_id'], game['game_number'],
                game['team1_score'], game['team2_score'], game['winner_team'],
                game['duration_minutes'], game['max_rally_length']
            ))
        
        self.conn.commit()
        return games
    
    def generate_match_statistics(self, matches: List[Dict]):
        """Generate detailed match statistics for players"""
        statistics = []
        stat_id = 1
        
        for match in matches:
            for player in match['players']:
                is_winner = player['player_id'] == match['winner_id']
                
                # Generate realistic statistics
                total_shots = random.randint(50, 150)
                
                # Winners and errors (winner typically has better ratio)
                if is_winner:
                    winners = random.randint(15, 35)
                    unforced_errors = random.randint(8, 20)
                else:
                    winners = random.randint(10, 25)
                    unforced_errors = random.randint(15, 30)
                
                # Serving statistics
                total_serves = random.randint(20, 40)
                service_aces = random.randint(0, 5)
                service_faults = random.randint(0, 8)
                
                # Shot distribution
                smashes = random.randint(5, 20)
                clears = random.randint(10, 30)
                drops = random.randint(8, 25)
                drives = random.randint(5, 15)
                net_shots = random.randint(8, 20)
                lobs = random.randint(3, 12)
                
                # Rally statistics
                short_rallies = random.randint(10, 25)
                medium_rallies = random.randint(8, 20)
                long_rallies = random.randint(2, 10)
                
                total_points = short_rallies + medium_rallies + long_rallies
                
                if is_winner:
                    points_won = int(total_points * random.uniform(0.55, 0.7))
                else:
                    points_won = int(total_points * random.uniform(0.3, 0.45))
                
                stat = {
                    'stat_id': stat_id,
                    'match_id': match['match_id'],
                    'player_id': player['player_id'],
                    'total_serves': total_serves,
                    'service_aces': service_aces,
                    'service_faults': service_faults,
                    'short_serves': random.randint(5, total_serves//2),
                    'long_serves': random.randint(5, total_serves//2),
                    'flick_serves': random.randint(0, total_serves//4),
                    'total_shots': total_shots,
                    'winners': winners,
                    'unforced_errors': unforced_errors,
                    'forced_errors': random.randint(5, 15),
                    'smashes': smashes,
                    'clears': clears,
                    'drops': drops,
                    'drives': drives,
                    'net_shots': net_shots,
                    'lobs': lobs,
                    'kills': random.randint(0, 8),
                    'net_points_won': random.randint(0, 15),
                    'net_points_played': random.randint(5, 20),
                    'backcourt_points_won': random.randint(5, 25),
                    'backcourt_points_played': random.randint(10, 30),
                    'short_rallies_won': random.randint(0, short_rallies),
                    'medium_rallies_won': random.randint(0, medium_rallies),
                    'long_rallies_won': random.randint(0, long_rallies),
                    'short_rallies_played': short_rallies,
                    'medium_rallies_played': medium_rallies,
                    'long_rallies_played': long_rallies,
                    'points_won': points_won,
                    'points_played': total_points
                }
                
                statistics.append(stat)
                stat_id += 1
        
        # Insert statistics into database
        insert_query = '''
            INSERT INTO match_statistics (
                stat_id, match_id, player_id, total_serves, service_aces, service_faults,
                short_serves, long_serves, flick_serves, total_shots, winners, unforced_errors,
                forced_errors, smashes, clears, drops, drives, net_shots, lobs, kills,
                net_points_won, net_points_played, backcourt_points_won, backcourt_points_played,
                short_rallies_won, medium_rallies_won, long_rallies_won, short_rallies_played,
                medium_rallies_played, long_rallies_played, points_won, points_played
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        for stat in statistics:
            self.conn.execute(insert_query, (
                stat['stat_id'], stat['match_id'], stat['player_id'],
                stat['total_serves'], stat['service_aces'], stat['service_faults'],
                stat['short_serves'], stat['long_serves'], stat['flick_serves'],
                stat['total_shots'], stat['winners'], stat['unforced_errors'],
                stat['forced_errors'], stat['smashes'], stat['clears'],
                stat['drops'], stat['drives'], stat['net_shots'],
                stat['lobs'], stat['kills'], stat['net_points_won'],
                stat['net_points_played'], stat['backcourt_points_won'],
                stat['backcourt_points_played'], stat['short_rallies_won'],
                stat['medium_rallies_won'], stat['long_rallies_won'],
                stat['short_rallies_played'], stat['medium_rallies_played'],
                stat['long_rallies_played'], stat['points_won'], stat['points_played']
            ))
        
        self.conn.commit()
        return statistics
    
    def generate_all_data(self, num_male_players: int = 30, num_female_players: int = 30, 
                         num_tournaments: int = 8, matches_per_tournament: int = 15):
        """Generate complete dataset"""
        print("Connecting to database...")
        self.connect_db()
        
        print("Generating players...")
        players = self.generate_players(num_male_players, num_female_players)
        print(f"Generated {len(players)} players")
        
        print("Generating tournaments...")
        tournaments = self.generate_tournaments(num_tournaments=num_tournaments)
        print(f"Generated {len(tournaments)} tournaments")
        
        print("Generating matches...")
        matches = self.generate_matches(tournaments, players, matches_per_tournament)
        print(f"Generated {len(matches)} matches")
        
        print("Generating game results...")
        games = self.generate_game_results(matches)
        print(f"Generated {len(games)} games")
        
        print("Generating match statistics...")
        statistics = self.generate_match_statistics(matches)
        print(f"Generated {len(statistics)} match statistics records")
        
        print("Data generation completed successfully!")
        
        self.close_db()
        return {
            'players': len(players),
            'tournaments': len(tournaments),
            'matches': len(matches),
            'games': len(games),
            'statistics': len(statistics)
        }

if __name__ == "__main__":
    generator = BadmintonDataGenerator("badminton_test.db")
    result = generator.generate_all_data()
    print("\nData generation summary:")
    for key, value in result.items():
        print(f"  {key.title()}: {value}")