"""
Badminton Statistics Visualizer
Advanced visualization and reporting tools for badminton analytics
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from badminton_analyzer import BadmintonAnalyzer
import json
from datetime import datetime

class BadmintonVisualizer:
    """Advanced visualization for badminton statistics"""
    
    def __init__(self, analyzer: BadmintonAnalyzer):
        self.analyzer = analyzer
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Custom color schemes
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'success': '#C73E1D',
            'background': '#F5F5F5'
        }
    
    def plot_player_performance_radar(self, player_id: int, save_path: Optional[str] = None) -> str:
        """Create radar chart for player performance metrics"""
        
        # Get player data
        profile = self.analyzer.get_player_profile(player_id)
        stats = self.analyzer.get_player_statistics_summary(player_id)
        shot_analysis = self.analyzer.get_shot_distribution_analysis(player_id)
        rally_analysis = self.analyzer.get_rally_length_analysis(player_id)
        
        player_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}"
        
        # Prepare data for radar chart
        metrics = {
            'Win Rate': min(profile.get('win_percentage', 0), 100),
            'Points Won %': min(stats.get('points_won_percentage', 0), 100),
            'Ace %': min(stats.get('ace_percentage', 0) * 5, 100),  # Scale up for visibility
            'Winner/Error Ratio': min(stats.get('winner_to_error_ratio', 0) * 20, 100),  # Scale up
            'Short Rally Win %': min(rally_analysis.get('short_rally_win_rate', 0), 100),
            'Medium Rally Win %': min(rally_analysis.get('medium_rally_win_rate', 0), 100),
            'Long Rally Win %': min(rally_analysis.get('long_rally_win_rate', 0), 100),
            'Attack %': min(shot_analysis.get('smash_percentage', 0) * 2, 100),  # Scale up
        }
        
        # Create plotly radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=list(metrics.values()),
            theta=list(metrics.keys()),
            fill='toself',
            name=player_name,
            line=dict(color=self.colors['primary']),
            fillcolor=f"rgba(46, 134, 171, 0.3)"
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title=f"Performance Radar - {player_name}",
            font=dict(size=12),
            width=600,
            height=500
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig.to_html()
    
    def plot_shot_distribution_pie(self, player_id: int, save_path: Optional[str] = None) -> str:
        """Create pie chart for shot distribution"""
        
        shot_analysis = self.analyzer.get_shot_distribution_analysis(player_id)
        profile = self.analyzer.get_player_profile(player_id)
        player_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}"
        
        # Prepare shot data
        shots = {
            'Smash': shot_analysis.get('total_smashes', 0),
            'Clear': shot_analysis.get('total_clears', 0),
            'Drop': shot_analysis.get('total_drops', 0),
            'Drive': shot_analysis.get('total_drives', 0),
            'Net Shot': shot_analysis.get('total_net_shots', 0),
            'Lob': shot_analysis.get('total_lobs', 0),
            'Kill': shot_analysis.get('total_kills', 0)
        }
        
        # Filter out zero values
        shots = {k: v for k, v in shots.items() if v > 0}
        
        if not shots:
            return "<p>No shot data available</p>"
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(shots.keys()),
            values=list(shots.values()),
            hole=0.3,
            textinfo='label+percent',
            textposition='auto'
        )])
        
        fig.update_layout(
            title=f"Shot Distribution - {player_name}",
            showlegend=True,
            width=500,
            height=400
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig.to_html()
    
    def plot_performance_timeline(self, player_id: int, days: int = 90, save_path: Optional[str] = None) -> str:
        """Create timeline chart for performance trends"""
        
        trends = self.analyzer.get_performance_trends(player_id, days)
        profile = self.analyzer.get_player_profile(player_id)
        player_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}"
        
        if not trends:
            return "<p>No performance data available for the specified period</p>"
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(trends)
        df['match_date'] = pd.to_datetime(df['match_date'])
        df['result'] = df['is_winner'].map({1: 'Win', 0: 'Loss'})
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Match Results', 'Points Won Percentage'),
            shared_xaxes=True,
            vertical_spacing=0.1
        )
        
        # Match results scatter
        colors = df['is_winner'].map({1: 'green', 0: 'red'})
        fig.add_trace(
            go.Scatter(
                x=df['match_date'],
                y=df['is_winner'],
                mode='markers',
                marker=dict(color=colors, size=10),
                text=df['result'],
                name='Match Results',
                yaxis='y1'
            ),
            row=1, col=1
        )
        
        # Points won percentage line
        fig.add_trace(
            go.Scatter(
                x=df['match_date'],
                y=df['points_won_pct'],
                mode='lines+markers',
                name='Points Won %',
                line=dict(color=self.colors['primary'])
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f"Performance Timeline - {player_name}",
            xaxis_title="Date",
            height=600,
            showlegend=True
        )
        
        fig.update_yaxes(title_text="Win/Loss", row=1, col=1)
        fig.update_yaxes(title_text="Points Won %", row=2, col=1)
        
        if save_path:
            fig.write_html(save_path)
        
        return fig.to_html()
    
    def plot_head_to_head_comparison(self, player1_id: int, player2_id: int, save_path: Optional[str] = None) -> str:
        """Create head-to-head comparison chart"""
        
        # Get player profiles
        p1_profile = self.analyzer.get_player_profile(player1_id)
        p2_profile = self.analyzer.get_player_profile(player2_id)
        
        p1_name = f"{p1_profile.get('first_name', '')} {p1_profile.get('last_name', '')}"
        p2_name = f"{p2_profile.get('first_name', '')} {p2_profile.get('last_name', '')}"
        
        # Get comparison data
        comparison = self.analyzer.compare_players([player1_id, player2_id])
        p1_data = comparison[player1_id]
        p2_data = comparison[player2_id]
        
        # Prepare comparison metrics
        metrics = [
            'win_percentage',
            'points_won_percentage',
            'winner_to_error_ratio',
            'ace_percentage'
        ]
        
        metric_labels = [
            'Win Percentage',
            'Points Won %',
            'Winner/Error Ratio',
            'Ace Percentage'
        ]
        
        p1_values = [p1_data.get(metric, 0) for metric in metrics]
        p2_values = [p2_data.get(metric, 0) for metric in metrics]
        
        # Normalize winner/error ratio and ace percentage for better comparison
        p1_values[2] = min(p1_values[2] * 10, 100)  # Scale winner/error ratio
        p2_values[2] = min(p2_values[2] * 10, 100)
        p1_values[3] = min(p1_values[3] * 5, 100)   # Scale ace percentage
        p2_values[3] = min(p2_values[3] * 5, 100)
        
        # Create bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=metric_labels,
            y=p1_values,
            name=p1_name,
            marker=dict(color=self.colors['primary'])
        ))
        
        fig.add_trace(go.Bar(
            x=metric_labels,
            y=p2_values,
            name=p2_name,
            marker=dict(color=self.colors['secondary'])
        ))
        
        fig.update_layout(
            title=f"Head-to-Head Comparison: {p1_name} vs {p2_name}",
            xaxis_title="Metrics",
            yaxis_title="Performance Score",
            barmode='group',
            height=500,
            showlegend=True
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig.to_html()
    
    def plot_tournament_performance_heatmap(self, player_id: int, save_path: Optional[str] = None) -> str:
        """Create heatmap for tournament performance"""
        
        performance = self.analyzer.get_performance_by_tournament_type(player_id)
        profile = self.analyzer.get_player_profile(player_id)
        player_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}"
        
        if not performance:
            return "<p>No tournament performance data available</p>"
        
        # Convert to DataFrame
        df = pd.DataFrame(performance)
        
        # Create matrix for heatmap
        tournaments = df['tournament_type'].tolist()
        metrics = ['matches_played', 'win_percentage', 'avg_points_won_pct']
        metric_labels = ['Matches Played', 'Win Percentage', 'Avg Points Won %']
        
        # Normalize data for better visualization
        heatmap_data = []
        for tournament in tournaments:
            row = []
            tournament_data = df[df['tournament_type'] == tournament].iloc[0]
            
            # Normalize each metric to 0-100 scale
            matches = min(tournament_data['matches_played'] * 10, 100)  # Scale matches
            win_pct = tournament_data['win_percentage'] or 0
            points_pct = tournament_data['avg_points_won_pct'] or 0
            
            row = [matches, win_pct, points_pct]
            heatmap_data.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=metric_labels,
            y=tournaments,
            colorscale='Blues',
            showscale=True
        ))
        
        fig.update_layout(
            title=f"Tournament Performance Heatmap - {player_name}",
            xaxis_title="Performance Metrics",
            yaxis_title="Tournament Types",
            height=400,
            width=600
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig.to_html()
    
    def create_comprehensive_dashboard(self, player_id: int, save_path: Optional[str] = None) -> str:
        """Create comprehensive dashboard with multiple visualizations"""
        
        profile = self.analyzer.get_player_profile(player_id)
        player_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}"
        
        # Create HTML dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Badminton Analytics Dashboard - {player_name}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .dashboard-header {{
                    text-align: center;
                    background-color: #2E86AB;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .stat-number {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #2E86AB;
                }}
                .stat-label {{
                    color: #666;
                    margin-top: 5px;
                }}
                .viz-container {{
                    background: white;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .viz-row {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-header">
                <h1>Badminton Analytics Dashboard</h1>
                <h2>{player_name} ({profile.get('nationality', 'Unknown')})</h2>
                <p>World Ranking: #{profile.get('world_ranking', 'Unranked')}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{profile.get('total_matches', 0)}</div>
                    <div class="stat-label">Total Matches</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{profile.get('win_percentage', 0):.1f}%</div>
                    <div class="stat-label">Win Percentage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{profile.get('tournaments_played', 0)}</div>
                    <div class="stat-label">Tournaments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{profile.get('avg_match_duration', 0):.0f}</div>
                    <div class="stat-label">Avg Match Duration (min)</div>
                </div>
            </div>
            
            <div class="viz-row">
                <div class="viz-container">
                    <h3>Performance Radar</h3>
                    {self.plot_player_performance_radar(player_id)}
                </div>
                <div class="viz-container">
                    <h3>Shot Distribution</h3>
                    {self.plot_shot_distribution_pie(player_id)}
                </div>
            </div>
            
            <div class="viz-container">
                <h3>Performance Timeline (Last 90 Days)</h3>
                {self.plot_performance_timeline(player_id, 90)}
            </div>
            
            <div class="viz-container">
                <h3>Tournament Performance</h3>
                {self.plot_tournament_performance_heatmap(player_id)}
            </div>
        </body>
        </html>
        """
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(html_content)
        
        return html_content
    
    def generate_match_report(self, match_id: int, save_path: Optional[str] = None) -> str:
        """Generate detailed match report with visualizations"""
        
        match_insights = self.analyzer.get_match_insights(match_id)
        
        if not match_insights:
            return "<p>Match not found</p>"
        
        match_info = match_insights['match_info']
        players = match_insights['players']
        games = match_insights['games']
        statistics = match_insights['statistics']
        
        # Create match report HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Match Report - {match_info['tournament_name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .match-header {{ background-color: #2E86AB; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .players-section {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
                .player-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .winner {{ border-left: 5px solid #28a745; }}
                .loser {{ border-left: 5px solid #dc3545; }}
                .games-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                .games-table th, .games-table td {{ border: 1px solid #ddd; padding: 10px; text-align: center; }}
                .games-table th {{ background-color: #f8f9fa; }}
            </style>
        </head>
        <body>
            <div class="match-header">
                <h1>Match Report</h1>
                <h2>{match_info['tournament_name']} - {match_info['round']}</h2>
                <p>Date: {match_info['match_date']} | Duration: {match_info['duration_minutes']} minutes</p>
                <p>Court: {match_info['court']} | Temperature: {match_info['temperature_celsius']}°C</p>
            </div>
        """
        
        # Add players section
        html_content += '<div class="players-section">'
        for i, player in enumerate(players):
            winner_class = "winner" if player['is_winner'] else "loser"
            status = "WINNER" if player['is_winner'] else "LOSER"
            
            html_content += f"""
            <div class="player-card {winner_class}">
                <h3>{player['player_name']} - {status}</h3>
                <p>Nationality: {player['nationality']}</p>
                <p>World Ranking: #{player['world_ranking'] if player['world_ranking'] else 'Unranked'}</p>
            </div>
            """
        
        html_content += '</div>'
        
        # Add games results
        if games:
            html_content += '''
            <h3>Game Results</h3>
            <table class="games-table">
                <tr><th>Game</th><th>Player 1</th><th>Player 2</th><th>Winner</th><th>Duration</th></tr>
            '''
            
            for game in games:
                html_content += f"""
                <tr>
                    <td>Game {game['game_number']}</td>
                    <td>{game['team1_score']}</td>
                    <td>{game['team2_score']}</td>
                    <td>Team {game['winner_team']}</td>
                    <td>{game['duration_minutes']} min</td>
                </tr>
                """
            
            html_content += '</table>'
        
        # Add statistics comparison if available
        if len(statistics) >= 2:
            html_content += '<h3>Match Statistics Comparison</h3>'
            # You could add a comparison chart here using the statistics data
        
        html_content += '</body></html>'
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(html_content)
        
        return html_content

if __name__ == "__main__":
    # Example usage
    analyzer = BadmintonAnalyzer("badminton_test.db")
    visualizer = BadmintonVisualizer(analyzer)
    
    # Get top player for demonstration
    top_players = analyzer.get_top_performers('win_percentage', limit=1)
    
    if top_players:
        player_id = top_players[0]['player_id']
        
        # Create dashboard
        dashboard = visualizer.create_comprehensive_dashboard(player_id, "player_dashboard.html")
        print(f"Dashboard created for {top_players[0]['player_name']}")
        
        # Create individual charts
        radar = visualizer.plot_player_performance_radar(player_id, "radar_chart.html")
        pie = visualizer.plot_shot_distribution_pie(player_id, "shot_distribution.html")
        timeline = visualizer.plot_performance_timeline(player_id, save_path="performance_timeline.html")
        
        print("Visualizations created successfully!")
    
    analyzer.close_db()