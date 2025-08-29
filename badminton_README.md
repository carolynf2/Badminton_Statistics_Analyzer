# Badminton Statistics Analyzer

A comprehensive Python application for analyzing badminton match statistics using SQL databases and advanced visualization tools. This system generates synthetic badminton data and provides detailed analytics for players, matches, and tournaments.

## Features

### 🏸 Core Analytics
- **Player Performance Analysis**: Win rates, shot distributions, rally preferences
- **Head-to-Head Comparisons**: Historical matchup analysis between players  
- **Match Insights**: Detailed breakdown of individual matches
- **Tournament Statistics**: Performance across different tournament types
- **Scouting Reports**: Comprehensive player profiles with strengths/weaknesses

### 📊 Visualizations  
- **Performance Radar Charts**: Multi-dimensional player analysis
- **Shot Distribution Pie Charts**: Playing style visualization
- **Performance Timelines**: Trend analysis over time
- **Interactive Dashboards**: Comprehensive HTML reports
- **Heatmaps**: Tournament performance analysis

### 🗄️ Database Features
- **Comprehensive Schema**: Covers players, tournaments, matches, statistics
- **Data Integrity**: Foreign key constraints and validation
- **Performance Optimized**: Indexed queries for fast analysis
- **Synthetic Data Generation**: Realistic test data with professional player names

## Installation

### Prerequisites
```bash
pip install sqlite3 pandas numpy matplotlib seaborn plotly
```

### Files Structure
```
badminton-analyzer/
├── badminton_schema.sql          # Database schema
├── badminton_data_generator.py   # Synthetic data generator
├── badminton_analyzer.py         # Core analytics engine
├── badminton_visualizer.py       # Visualization tools
├── badminton_app.py              # Main application
└── README.md                     # This file
```

## Quick Start

### 1. Setup and Test
```bash
# Run with automatic setup and testing
python badminton_app.py --setup --test --interactive

# Or step by step:
python badminton_app.py --setup      # Setup database with synthetic data
python badminton_app.py --test       # Run comprehensive tests
python badminton_app.py --interactive # Enter interactive mode
```

### 2. Generate Data Only
```python
from badminton_data_generator import BadmintonDataGenerator

generator = BadmintonDataGenerator("my_badminton.db")
result = generator.generate_all_data(
    num_male_players=50,
    num_female_players=50,
    num_tournaments=10,
    matches_per_tournament=20
)
```

### 3. Basic Analysis
```python
from badminton_analyzer import BadmintonAnalyzer

analyzer = BadmintonAnalyzer("my_badminton.db")

# Get top performers
top_players = analyzer.get_top_performers('win_percentage', limit=10)
for player in top_players:
    print(f"{player['player_name']}: {player['win_percentage']}% win rate")

# Analyze specific player
player_id = top_players[0]['player_id']
scouting_report = analyzer.generate_scouting_report(player_id)
print(f"Strengths: {scouting_report['playing_style']['strengths']}")
```

### 4. Create Visualizations
```python
from badminton_visualizer import BadmintonVisualizer

visualizer = BadmintonVisualizer(analyzer)

# Generate comprehensive dashboard
player_id = 1
dashboard_html = visualizer.create_comprehensive_dashboard(
    player_id, 
    save_path="player_dashboard.html"
)

# Create individual charts
radar_chart = visualizer.plot_player_performance_radar(player_id)
shot_distribution = visualizer.plot_shot_distribution_pie(player_id)
```

## Database Schema

### Core Tables
- **players**: Player information (name, nationality, ranking, physical stats)
- **tournaments**: Tournament details (name, location, type, dates)
- **matches**: Match information (date, duration, participants, winner)
- **games**: Individual games within matches (scores, duration)
- **match_statistics**: Detailed shot and performance statistics
- **head_to_head**: Historical matchup records

### Key Relationships
```sql
-- Player participates in matches
players ←→ match_participants ←→ matches

-- Matches belong to tournaments  
matches → tournaments

-- Games are part of matches
games → matches

-- Statistics are recorded per player per match
match_statistics → players
match_statistics → matches
```

## API Reference

### BadmintonAnalyzer Class

#### Player Analysis Methods
```python
# Get player profile with basic stats
get_player_profile(player_id: int) -> Dict

# Get detailed statistics summary  
get_player_statistics_summary(player_id: int) -> Dict

# Analyze shot distribution and effectiveness
get_shot_distribution_analysis(player_id: int) -> Dict

# Analyze performance by rally length
get_rally_length_analysis(player_id: int) -> Dict

# Get recent match results
get_recent_matches(player_id: int, limit: int = 10) -> List[Dict]

# Generate comprehensive scouting report
generate_scouting_report(player_id: int) -> Dict
```

#### Comparison Methods
```python
# Compare multiple players
compare_players(player_ids: List[int]) -> Dict

# Get head-to-head record between two players
get_head_to_head(player1_id: int, player2_id: int) -> Dict

# Get top performers by metric
get_top_performers(metric: str, limit: int = 10, min_matches: int = 5) -> List[Dict]
```

#### Match Analysis Methods
```python  
# Get detailed match insights
get_match_insights(match_id: int) -> Dict

# Get tournament performance summary
get_tournament_performance(tournament_id: int) -> Dict

# Analyze performance trends over time
get_performance_trends(player_id: int, days: int = 90) -> List[Dict]
```

### BadmintonVisualizer Class

#### Chart Generation Methods
```python
# Create radar chart for player performance
plot_player_performance_radar(player_id: int, save_path: str = None) -> str

# Create pie chart for shot distribution  
plot_shot_distribution_pie(player_id: int, save_path: str = None) -> str

# Create timeline for performance trends
plot_performance_timeline(player_id: int, days: int = 90, save_path: str = None) -> str

# Create head-to-head comparison chart
plot_head_to_head_comparison(player1_id: int, player2_id: int, save_path: str = None) -> str

# Create comprehensive dashboard
create_comprehensive_dashboard(player_id: int, save_path: str = None) -> str
```

## Usage Examples

### Example 1: Player Performance Analysis
```python
from badminton_analyzer import BadmintonAnalyzer
from badminton_visualizer import BadmintonVisualizer

# Initialize analyzer
analyzer = BadmintonAnalyzer("badminton.db")
visualizer = BadmintonVisualizer(analyzer)

# Find top player
top_players = analyzer.get_top_performers('win_percentage', limit=1)
player_id = top_players[0]['player_id']
player_name = top_players[0]['player_name']

print(f"Analyzing {player_name}...")

# Get comprehensive analysis
profile = analyzer.get_player_profile(player_id)
stats = analyzer.get_player_statistics_summary(player_id)
shot_analysis = analyzer.get_shot_distribution_analysis(player_id)

# Print key metrics
print(f"Win Rate: {profile['win_percentage']}%")
print(f"Total Matches: {profile['total_matches']}")
print(f"Points Won: {stats['points_won_percentage']:.1f}%")
print(f"Winner/Error Ratio: {stats['winner_to_error_ratio']:.2f}")
print(f"Most Used Shot: Smash ({shot_analysis['smash_percentage']:.1f}%)")

# Create visualizations
dashboard = visualizer.create_comprehensive_dashboard(
    player_id, 
    f"{player_name.replace(' ', '_')}_dashboard.html"
)
print(f"Dashboard saved for {player_name}")
```

### Example 2: Head-to-Head Analysis
```python
# Compare two top players
top_players = analyzer.get_top_performers('win_percentage', limit=5)
player1_id = top_players[0]['player_id']
player2_id = top_players[1]['player_id']

# Get head-to-head record
h2h = analyzer.get_head_to_head(player1_id, player2_id)
if h2h:
    print(f"Head-to-Head: {h2h['player1_name']} vs {h2h['player2_name']}")
    print(f"Total Matches: {h2h['matches_played']}")
    print(f"Record: {h2h['player1_wins']}-{h2h['player2_wins']}")

# Create comparison visualization
comparison_chart = visualizer.plot_head_to_head_comparison(
    player1_id, 
    player2_id, 
    "head_to_head_comparison.html"
)

# Detailed comparison
comparison = analyzer.compare_players([player1_id, player2_id])
for player_id, data in comparison.items():
    print(f"\n{data['name']} ({data['nationality']}):")
    print(f"  Ranking: #{data['ranking'] or 'Unranked'}")
    print(f"  Win Rate: {data['win_percentage']:.1f}%") 
    print(f"  Preferred Rally Length: {data['preferred_rally_length']}")
```

## Testing

The application includes comprehensive testing:

```bash
python badminton_app.py --test
```

Tests cover:
- ✅ Database connectivity and data integrity
- ✅ Player analysis functions  
- ✅ Match analysis capabilities
- ✅ Visualization generation
- ✅ Performance benchmarks
- ✅ Error handling

## Interactive Mode

Run the interactive CLI:

```bash  
python badminton_app.py --interactive
```

Features:
1. **View Top Performers** - Rankings by various metrics
2. **Analyze Specific Player** - Detailed scouting reports
3. **Compare Players** - Side-by-side comparisons  
4. **Match Analysis** - Deep dive into specific matches
5. **Generate Dashboards** - Create interactive HTML reports
6. **Tournament Statistics** - Overview of all tournaments

## Performance

The system is optimized for performance:
- **Database**: Indexed queries for sub-second response times
- **Memory**: Efficient data structures and lazy loading  
- **Visualization**: Plotly for interactive charts with good performance
- **Scalability**: Handles 100+ players and 1000+ matches efficiently

## Sample Data

The synthetic data generator creates realistic badminton data:
- **Real Player Names**: Uses actual professional badminton players
- **Realistic Statistics**: Win rates, shot distributions based on real patterns
- **Tournament Variety**: Different BWF tournament types and locations
- **Match Details**: Proper game scores, rally lengths, shot statistics

---

**Start exploring badminton analytics by running:**
```bash
python badminton_app.py --setup --interactive
```