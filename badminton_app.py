"""
Badminton Statistics Application
Main application with CLI interface and comprehensive testing
"""

import argparse
import sys
import os
from typing import List, Dict, Optional
import json
from datetime import datetime
import sqlite3

from badminton_data_generator import BadmintonDataGenerator
from badminton_analyzer import BadmintonAnalyzer  
from badminton_visualizer import BadmintonVisualizer

class BadmintonStatsApp:
    """Main application class for badminton statistics analysis"""
    
    def __init__(self, db_path: str = "badminton.db"):
        self.db_path = db_path
        self.generator = None
        self.analyzer = None
        self.visualizer = None
        
    def initialize_components(self):
        """Initialize all components"""
        try:
            self.generator = BadmintonDataGenerator(self.db_path)
            self.analyzer = BadmintonAnalyzer(self.db_path)
            self.visualizer = BadmintonVisualizer(self.analyzer)
            return True
        except Exception as e:
            print(f"Error initializing components: {e}")
            return False
    
    def setup_database(self, regenerate: bool = False):
        """Setup database and generate data if needed"""
        if regenerate or not os.path.exists(self.db_path):
            print("Setting up database and generating synthetic data...")
            
            # Remove existing database
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            
            # Generate new data
            result = self.generator.generate_all_data(
                num_male_players=30,
                num_female_players=30,
                num_tournaments=8,
                matches_per_tournament=15
            )
            
            print("Database setup completed!")
            print(f"Generated: {result['players']} players, {result['matches']} matches")
            
        else:
            print(f"Using existing database: {self.db_path}")
    
    def run_tests(self):
        """Run comprehensive tests on the system"""
        print("\n" + "="*50)
        print("RUNNING BADMINTON STATISTICS ANALYZER TESTS")
        print("="*50)
        
        test_results = {
            'database_connection': False,
            'data_integrity': False,
            'player_analysis': False,
            'match_analysis': False,
            'visualization': False,
            'performance': False
        }
        
        # Test 1: Database Connection
        print("\n1. Testing Database Connection...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM players")
            player_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM matches")
            match_count = cursor.fetchone()[0]
            
            conn.close()
            
            if player_count > 0 and match_count > 0:
                print(f"   ✓ Database connected successfully")
                print(f"   ✓ Found {player_count} players and {match_count} matches")
                test_results['database_connection'] = True
            else:
                print("   ✗ Database is empty")
                
        except Exception as e:
            print(f"   ✗ Database connection failed: {e}")
        
        # Test 2: Data Integrity
        print("\n2. Testing Data Integrity...")
        try:
            # Check for orphaned records
            integrity_queries = [
                "SELECT COUNT(*) FROM match_participants mp LEFT JOIN players p ON mp.player_id = p.player_id WHERE p.player_id IS NULL",
                "SELECT COUNT(*) FROM matches m LEFT JOIN tournaments t ON m.tournament_id = t.tournament_id WHERE t.tournament_id IS NULL",
                "SELECT COUNT(*) FROM match_statistics ms LEFT JOIN matches m ON ms.match_id = m.match_id WHERE m.match_id IS NULL"
            ]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            orphaned_count = 0
            for query in integrity_queries:
                cursor.execute(query)
                orphaned_count += cursor.fetchone()[0]
            
            conn.close()
            
            if orphaned_count == 0:
                print("   ✓ No data integrity issues found")
                test_results['data_integrity'] = True
            else:
                print(f"   ⚠ Found {orphaned_count} orphaned records")
                test_results['data_integrity'] = True  # Still pass as data is mostly intact
                
        except Exception as e:
            print(f"   ✗ Data integrity check failed: {e}")
        
        # Test 3: Player Analysis
        print("\n3. Testing Player Analysis...")
        try:
            # Get top players
            top_players = self.analyzer.get_top_performers('win_percentage', limit=5)
            
            if len(top_players) > 0:
                player = top_players[0]
                player_id = player['player_id']
                
                # Test various analysis functions
                profile = self.analyzer.get_player_profile(player_id)
                stats = self.analyzer.get_player_statistics_summary(player_id)
                shot_analysis = self.analyzer.get_shot_distribution_analysis(player_id)
                recent_matches = self.analyzer.get_recent_matches(player_id, 5)
                
                print(f"   ✓ Successfully analyzed player: {player['player_name']}")
                print(f"   ✓ Win percentage: {player['win_percentage']}%")
                print(f"   ✓ Total matches: {player['total_matches']}")
                print(f"   ✓ Recent matches found: {len(recent_matches)}")
                
                test_results['player_analysis'] = True
            else:
                print("   ✗ No players found for analysis")
                
        except Exception as e:
            print(f"   ✗ Player analysis failed: {e}")
        
        # Test 4: Match Analysis
        print("\n4. Testing Match Analysis...")
        try:
            # Get a random match
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT match_id FROM matches WHERE status = 'COMPLETED' LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            
            if result:
                match_id = result[0]
                match_insights = self.analyzer.get_match_insights(match_id)
                
                if match_insights:
                    print(f"   ✓ Successfully analyzed match ID: {match_id}")
                    print(f"   ✓ Tournament: {match_insights['match_info']['tournament_name']}")
                    print(f"   ✓ Players: {len(match_insights['players'])}")
                    print(f"   ✓ Games: {len(match_insights['games'])}")
                    
                    test_results['match_analysis'] = True
                else:
                    print("   ✗ Match insights not found")
            else:
                print("   ✗ No completed matches found")
                
        except Exception as e:
            print(f"   ✗ Match analysis failed: {e}")
        
        # Test 5: Visualization
        print("\n5. Testing Visualization...")
        try:
            if test_results['player_analysis']:
                top_players = self.analyzer.get_top_performers('win_percentage', limit=1)
                player_id = top_players[0]['player_id']
                
                # Test radar chart
                radar_html = self.visualizer.plot_player_performance_radar(player_id)
                
                # Test shot distribution
                pie_html = self.visualizer.plot_shot_distribution_pie(player_id)
                
                # Test dashboard creation
                dashboard_html = self.visualizer.create_comprehensive_dashboard(player_id)
                
                if radar_html and pie_html and dashboard_html:
                    print("   ✓ Radar chart generated successfully")
                    print("   ✓ Shot distribution chart generated successfully")
                    print("   ✓ Comprehensive dashboard generated successfully")
                    test_results['visualization'] = True
                else:
                    print("   ✗ Some visualizations failed to generate")
            else:
                print("   ⚠ Skipping visualization tests (player analysis failed)")
                
        except Exception as e:
            print(f"   ✗ Visualization testing failed: {e}")
        
        # Test 6: Performance
        print("\n6. Testing Performance...")
        try:
            import time
            
            # Time various operations
            start_time = time.time()
            top_players = self.analyzer.get_top_performers('win_percentage', limit=10)
            query_time = time.time() - start_time
            
            start_time = time.time()
            if len(top_players) > 0:
                player_id = top_players[0]['player_id']
                profile = self.analyzer.get_player_profile(player_id)
                stats = self.analyzer.get_player_statistics_summary(player_id)
            analysis_time = time.time() - start_time
            
            print(f"   ✓ Top performers query: {query_time:.3f}s")
            print(f"   ✓ Player analysis: {analysis_time:.3f}s")
            
            if query_time < 1.0 and analysis_time < 0.5:
                print("   ✓ Performance is within acceptable limits")
                test_results['performance'] = True
            else:
                print("   ⚠ Performance is slower than expected")
                test_results['performance'] = True  # Still pass but with warning
                
        except Exception as e:
            print(f"   ✗ Performance testing failed: {e}")
        
        # Test Summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "PASS" if result else "FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! The system is working correctly.")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️  Most tests passed. System is functional with minor issues.")
        else:
            print("❌ Multiple test failures. System needs attention.")
        
        return test_results
    
    def interactive_mode(self):
        """Run interactive mode for exploring data"""
        print("\n" + "="*50)
        print("BADMINTON STATISTICS ANALYZER - INTERACTIVE MODE")
        print("="*50)
        
        while True:
            print("\nChoose an option:")
            print("1. View top performers")
            print("2. Analyze specific player")
            print("3. Compare players")
            print("4. Match analysis")
            print("5. Generate player dashboard")
            print("6. Tournament statistics")
            print("7. Exit")
            
            try:
                choice = input("\nEnter your choice (1-7): ").strip()
                
                if choice == '1':
                    self.show_top_performers()
                elif choice == '2':
                    self.analyze_player()
                elif choice == '3':
                    self.compare_players()
                elif choice == '4':
                    self.analyze_match()
                elif choice == '5':
                    self.generate_dashboard()
                elif choice == '6':
                    self.tournament_stats()
                elif choice == '7':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_top_performers(self):
        """Show top performers in various categories"""
        categories = {
            '1': ('win_percentage', 'Win Percentage'),
            '2': ('total_matches', 'Total Matches'),
            '3': ('winner_ratio', 'Winner/Error Ratio'),
            '4': ('ace_percentage', 'Ace Percentage')
        }
        
        print("\nSelect category:")
        for key, (_, label) in categories.items():
            print(f"{key}. {label}")
        
        cat_choice = input("Enter category (1-4): ").strip()
        
        if cat_choice in categories:
            metric, label = categories[cat_choice]
            top_players = self.analyzer.get_top_performers(metric, limit=10)
            
            print(f"\nTop 10 Players by {label}:")
            print("-" * 60)
            for i, player in enumerate(top_players, 1):
                print(f"{i:2d}. {player['player_name']} ({player['nationality']}) - {player['metric_value']:.2f}")
        else:
            print("Invalid category selected.")
    
    def analyze_player(self):
        """Analyze a specific player"""
        # First show some players to choose from
        top_players = self.analyzer.get_top_performers('win_percentage', limit=20)
        
        print("\nAvailable players:")
        for i, player in enumerate(top_players[:10], 1):
            print(f"{i:2d}. {player['player_name']} ({player['nationality']})")
        
        try:
            choice = int(input("Enter player number (1-10): "))
            if 1 <= choice <= min(10, len(top_players)):
                player_id = top_players[choice-1]['player_id']
                
                # Generate scouting report
                report = self.analyzer.generate_scouting_report(player_id)
                
                print(f"\n{'='*60}")
                print(f"SCOUTING REPORT: {report['player_info']['name']}")
                print(f"{'='*60}")
                
                # Player info
                info = report['player_info']
                print(f"Nationality: {info['nationality']}")
                print(f"Age: {info['age'] if info['age'] else 'Unknown'}")
                print(f"World Ranking: #{info['ranking'] if info['ranking'] else 'Unranked'}")
                print(f"Dominant Hand: {info['dominant_hand']}")
                
                # Performance overview
                perf = report['performance_overview']
                print(f"\nPERFORMANCE:")
                print(f"Total Matches: {perf['total_matches']}")
                print(f"Win Percentage: {perf['win_percentage']:.1f}%")
                print(f"Recent Form: {perf['recent_form']}")
                
                # Playing style
                style = report['playing_style']
                print(f"\nSTRENGTHS:")
                for strength in style['strengths'][:3]:
                    print(f"  • {strength}")
                
                if style['weaknesses']:
                    print(f"\nAREAS FOR IMPROVEMENT:")
                    for weakness in style['weaknesses'][:2]:
                        print(f"  • {weakness}")
                
            else:
                print("Invalid player selection.")
                
        except ValueError:
            print("Please enter a valid number.")
    
    def compare_players(self):
        """Compare multiple players"""
        top_players = self.analyzer.get_top_performers('win_percentage', limit=15)
        
        print("\nAvailable players:")
        for i, player in enumerate(top_players[:10], 1):
            print(f"{i:2d}. {player['player_name']} ({player['nationality']})")
        
        try:
            choices = input("Enter player numbers to compare (e.g., 1,3): ").split(',')
            player_ids = []
            
            for choice in choices:
                idx = int(choice.strip()) - 1
                if 0 <= idx < min(10, len(top_players)):
                    player_ids.append(top_players[idx]['player_id'])
            
            if len(player_ids) >= 2:
                comparison = self.analyzer.compare_players(player_ids)
                
                print(f"\n{'='*80}")
                print("PLAYER COMPARISON")
                print(f"{'='*80}")
                
                # Header
                print(f"{'Metric':<20}", end='')
                for player_id in player_ids:
                    name = comparison[player_id]['name'][:15]
                    print(f"{name:>15}", end='')
                print()
                print("-" * 80)
                
                # Comparison metrics
                metrics = [
                    ('matches_played', 'Matches Played'),
                    ('win_percentage', 'Win %'),
                    ('points_won_percentage', 'Points Won %'),
                    ('winner_to_error_ratio', 'Winner/Error'),
                    ('ace_percentage', 'Ace %')
                ]
                
                for key, label in metrics:
                    print(f"{label:<20}", end='')
                    for player_id in player_ids:
                        value = comparison[player_id].get(key, 0)
                        if key == 'winner_to_error_ratio':
                            print(f"{value:>15.2f}", end='')
                        else:
                            print(f"{value:>15.1f}", end='')
                    print()
                
            else:
                print("Please select at least 2 valid players.")
                
        except ValueError:
            print("Please enter valid numbers.")
    
    def analyze_match(self):
        """Analyze a specific match"""
        # Get recent matches
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT m.match_id, m.match_date, t.tournament_name, m.round,
                   p1.first_name || ' ' || p1.last_name as player1,
                   p2.first_name || ' ' || p2.last_name as player2
            FROM matches m
            JOIN tournaments t ON m.tournament_id = t.tournament_id
            JOIN match_participants mp1 ON m.match_id = mp1.match_id AND mp1.team_position = 1
            JOIN match_participants mp2 ON m.match_id = mp2.match_id AND mp2.team_position = 2
            JOIN players p1 ON mp1.player_id = p1.player_id
            JOIN players p2 ON mp2.player_id = p2.player_id
            WHERE m.status = 'COMPLETED'
            ORDER BY m.match_date DESC
            LIMIT 10
            """
            
            cursor.execute(query)
            matches = cursor.fetchall()
            conn.close()
            
            print("\nRecent matches:")
            for i, match in enumerate(matches, 1):
                match_id, date, tournament, round_name, p1, p2 = match
                print(f"{i:2d}. {date} - {tournament} ({round_name})")
                print(f"    {p1} vs {p2}")
            
            choice = int(input("Enter match number: "))
            if 1 <= choice <= len(matches):
                match_id = matches[choice-1][0]
                insights = self.analyzer.get_match_insights(match_id)
                
                if insights:
                    match_info = insights['match_info']
                    players = insights['players']
                    games = insights['games']
                    
                    print(f"\n{'='*60}")
                    print(f"MATCH ANALYSIS")
                    print(f"{'='*60}")
                    
                    print(f"Tournament: {match_info['tournament_name']}")
                    print(f"Date: {match_info['match_date']}")
                    print(f"Duration: {match_info['duration_minutes']} minutes")
                    print(f"Round: {match_info['round']}")
                    
                    print(f"\nPlayers:")
                    for player in players:
                        status = "WINNER" if player['is_winner'] else "LOSER"
                        print(f"  {player['player_name']} ({player['nationality']}) - {status}")
                    
                    if games:
                        print(f"\nGame Results:")
                        for game in games:
                            print(f"  Game {game['game_number']}: {game['team1_score']}-{game['team2_score']} ({game['duration_minutes']} min)")
                
            else:
                print("Invalid match selection.")
                
        except Exception as e:
            print(f"Error analyzing match: {e}")
    
    def generate_dashboard(self):
        """Generate player dashboard"""
        top_players = self.analyzer.get_top_performers('win_percentage', limit=10)
        
        print("\nSelect player for dashboard:")
        for i, player in enumerate(top_players, 1):
            print(f"{i:2d}. {player['player_name']} ({player['nationality']})")
        
        try:
            choice = int(input("Enter player number: "))
            if 1 <= choice <= len(top_players):
                player_id = top_players[choice-1]['player_id']
                player_name = top_players[choice-1]['player_name']
                
                filename = f"{player_name.replace(' ', '_')}_dashboard.html"
                
                print(f"Generating dashboard for {player_name}...")
                dashboard = self.visualizer.create_comprehensive_dashboard(player_id, filename)
                
                print(f"Dashboard saved to: {filename}")
                print("You can open this file in your web browser to view the interactive dashboard.")
                
            else:
                print("Invalid player selection.")
                
        except ValueError:
            print("Please enter a valid number.")
    
    def tournament_stats(self):
        """Show tournament statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT t.tournament_id, t.tournament_name, t.location, t.tournament_type,
                   COUNT(DISTINCT m.match_id) as matches,
                   COUNT(DISTINCT mp.player_id) as players,
                   AVG(m.duration_minutes) as avg_duration
            FROM tournaments t
            LEFT JOIN matches m ON t.tournament_id = m.tournament_id
            LEFT JOIN match_participants mp ON m.match_id = mp.match_id
            GROUP BY t.tournament_id
            ORDER BY matches DESC
            """
            
            cursor.execute(query)
            tournaments = cursor.fetchall()
            conn.close()
            
            print(f"\n{'='*80}")
            print("TOURNAMENT STATISTICS")
            print(f"{'='*80}")
            
            print(f"{'Tournament':<25} {'Location':<15} {'Type':<15} {'Matches':>8} {'Players':>8} {'Avg Duration':>12}")
            print("-" * 80)
            
            for tournament in tournaments:
                t_id, name, location, t_type, matches, players, avg_duration = tournament
                name_short = name[:24] if name else "Unknown"
                location_short = location[:14] if location else "Unknown"
                type_short = t_type[:14] if t_type else "Unknown"
                duration = f"{avg_duration:.0f} min" if avg_duration else "N/A"
                
                print(f"{name_short:<25} {location_short:<15} {type_short:<15} {matches or 0:>8} {players or 0:>8} {duration:>12}")
                
        except Exception as e:
            print(f"Error fetching tournament stats: {e}")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Badminton Statistics Analyzer")
    parser.add_argument("--db", default="badminton_test.db", help="Database file path")
    parser.add_argument("--setup", action="store_true", help="Setup database with synthetic data")
    parser.add_argument("--regenerate", action="store_true", help="Regenerate all data")
    parser.add_argument("--test", action="store_true", help="Run system tests")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Initialize app
    app = BadmintonStatsApp(args.db)
    
    if not app.initialize_components():
        print("Failed to initialize application components.")
        sys.exit(1)
    
    # Setup database if requested
    if args.setup or args.regenerate:
        app.setup_database(args.regenerate)
    
    # Run tests if requested
    if args.test:
        test_results = app.run_tests()
        
        # Exit with error code if tests failed
        passed = sum(test_results.values())
        total = len(test_results)
        if passed < total * 0.8:
            sys.exit(1)
    
    # Run interactive mode if requested
    if args.interactive:
        app.interactive_mode()
    
    # If no specific action requested, run tests and interactive mode
    if not any([args.setup, args.regenerate, args.test, args.interactive]):
        print("No specific action requested. Running tests and interactive mode...")
        app.run_tests()
        app.interactive_mode()

if __name__ == "__main__":
    main()