#!/usr/bin/env python3
"""
Analytics Dashboard Server - Standalone with AI Insights
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
from datetime import datetime, timedelta
import os
import requests

app = Flask(__name__)

class DashboardData:
    def __init__(self):
        self.db_path = "/workspace/data/analytics.db"
    
    def get_dashboard_data(self, days=7):
        """Get all dashboard data from existing database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute('''
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='interactions'
                ''')
                
                if not cursor.fetchone():
                    return {
                        "overview": {
                            "total_interactions": 0,
                            "high_priority": 0,
                            "negative_sentiment": 0,
                            "emails_sent": 0,
                            "avg_confidence": 0,
                            "avg_response_time": 0
                        },
                        "issue_distribution": [],
                        "sentiment_distribution": [],
                        "recent_interactions": [],
                        "message": "No data yet - send some requests to the AI service first"
                    }
                
                # Overview metrics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_interactions,
                        COUNT(CASE WHEN priority = 'high' THEN 1 END) as high_priority,
                        COUNT(CASE WHEN sentiment = 'negative' THEN 1 END) as negative_sentiment,
                        COUNT(CASE WHEN email_sent = 1 THEN 1 END) as emails_sent,
                        AVG(confidence) as avg_confidence,
                        AVG(response_time_ms) as avg_response_time
                    FROM interactions 
                    WHERE timestamp >= datetime('now', '-{} days')
                '''.format(days))
                
                overview = cursor.fetchone()
                
                # Issue distribution
                cursor.execute('''
                    SELECT issue_type, COUNT(*) as count
                    FROM interactions 
                    WHERE timestamp >= datetime('now', '-{} days')
                    GROUP BY issue_type
                    ORDER BY count DESC
                '''.format(days))
                
                issue_distribution = cursor.fetchall()
                
                # Sentiment distribution
                cursor.execute('''
                    SELECT sentiment, COUNT(*) as count
                    FROM interactions 
                    WHERE timestamp >= datetime('now', '-{} days')
                    GROUP BY sentiment
                '''.format(days))
                
                sentiment_distribution = cursor.fetchall()
                
                # Recent interactions
                cursor.execute('''
                    SELECT timestamp, customer_id, customer_tier, issue_type, 
                           sentiment, priority, email_sent
                    FROM interactions 
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''')
                
                recent_interactions = cursor.fetchall()
                
                return {
                    "overview": {
                        "total_interactions": overview[0] if overview else 0,
                        "high_priority": overview[1] if overview else 0,
                        "negative_sentiment": overview[2] if overview else 0,
                        "emails_sent": overview[3] if overview else 0,
                        "avg_confidence": round(overview[4] or 0, 3) if overview else 0,
                        "avg_response_time": round(overview[5] or 0, 1) if overview else 0
                    },
                    "issue_distribution": [
                        {"issue_type": row[0], "count": row[1]}
                        for row in issue_distribution
                    ],
                    "sentiment_distribution": [
                        {"sentiment": row[0], "count": row[1]}
                        for row in sentiment_distribution
                    ],
                    "recent_interactions": [
                        {
                            "timestamp": row[0],
                            "customer_id": row[1],
                            "customer_tier": row[2],
                            "issue_type": row[3],
                            "sentiment": row[4],
                            "priority": row[5],
                            "email_sent": bool(row[6])
                        }
                        for row in recent_interactions
                    ]
                }
                
        except Exception as e:
            return {"error": str(e)}

    def get_insights(self, limit=5):
        """Get latest insights from insights service"""
        try:
            response = requests.get('http://localhost:5003/api/insights', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('insights', [])
            else:
                return []
        except:
            return []

dashboard_data = DashboardData()

@app.route('/')
def dashboard():
    """Serve the dashboard HTML"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/data')
def api_data():
    """API endpoint for dashboard data"""
    days = int(request.args.get('days', 7))
    data = dashboard_data.get_dashboard_data(days)
    return jsonify(data)

@app.route('/api/insights')
def api_insights():
    """API endpoint for insights data"""
    insights = dashboard_data.get_insights()
    return jsonify({"insights": insights})

# Updated DASHBOARD_TEMPLATE with insights section
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Customer Support Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .controls {
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
        }
        
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        
        .content {
            padding: 30px;
        }
        
        .overview-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card-title {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            font-weight: 600;
        }
        
        .card-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        /* AI Insights Section */
        .insights-section {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            border: 2px solid #667eea;
        }
        
        .insight-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            transition: transform 0.2s ease;
        }
        
        .insight-card:hover {
            transform: translateX(5px);
        }
        
        .insight-high { border-left-color: #dc3545; }
        .insight-medium { border-left-color: #ffc107; }
        .insight-low { border-left-color: #28a745; }
        
        .insight-title {
            font-weight: bold;
            margin-bottom: 8px;
            color: #333;
        }
        
        .insight-message {
            color: #666;
            line-height: 1.4;
            margin-bottom: 8px;
        }
        
        .insight-meta {
            font-size: 0.8em;
            color: #999;
            display: flex;
            justify-content: space-between;
        }
        
        .insight-type {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7em;
        }
        
        .charts-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .chart-title {
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #333;
            font-weight: 600;
        }
        
        .recent-interactions {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .interactions-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .interactions-table th,
        .interactions-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .interactions-table th {
            background: #f8f9fa;
            font-weight: 600;
        }
        
        .sentiment-positive { color: #28a745; font-weight: bold; }
        .sentiment-negative { color: #dc3545; font-weight: bold; }
        .sentiment-neutral { color: #6c757d; }
        
        .priority-high { 
            background: #dc3545; 
            color: white; 
            padding: 4px 8px; 
            border-radius: 12px; 
            font-size: 0.8em;
        }
        
        .priority-medium { 
            background: #ffc107; 
            color: #333; 
            padding: 4px 8px; 
            border-radius: 12px; 
            font-size: 0.8em;
        }
        
        .priority-low { 
            background: #28a745; 
            color: white; 
            padding: 4px 8px; 
            border-radius: 12px; 
            font-size: 0.8em;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #666;
        }
        
        .no-data {
            text-align: center;
            padding: 50px;
            color: #666;
            background: #f8f9fa;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🤖 AI Customer Support Analytics</h1>
            <p>Real-time insights and metrics with AI-powered recommendations</p>
        </div>
        
        <div class="controls">
            <div class="last-updated">
                Last updated: <span id="lastUpdated">Loading...</span>
            </div>
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
        </div>
        
        <div class="content">
            <div id="loading" class="loading">Loading dashboard data...</div>
            
            <div id="dashboard-content" style="display: none;">
                <!-- Overview Cards -->
                <div class="overview-cards">
                    <div class="card">
                        <div class="card-title">Total Interactions</div>
                        <div class="card-value" id="totalInteractions">0</div>
                    </div>
                    <div class="card">
                        <div class="card-title">High Priority</div>
                        <div class="card-value" id="highPriority">0</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Negative Sentiment</div>
                        <div class="card-value" id="negativeSentiment">0</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Emails Sent</div>
                        <div class="card-value" id="emailsSent">0</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Avg Confidence</div>
                        <div class="card-value" id="avgConfidence">0%</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Avg Response Time</div>
                        <div class="card-value" id="avgResponseTime">0ms</div>
                    </div>
                </div>
                
                <!-- AI Insights Section -->
                <div class="insights-section">
                    <div class="chart-title">🤖 AI-Powered Insights & Recommendations</div>
                    <div id="insightsContainer">
                        <div class="loading">Loading AI insights...</div>
                    </div>
                </div>
                
                <!-- Charts -->
                <div class="charts-section">
                    <div class="chart-container">
                        <div class="chart-title">Issue Type Distribution</div>
                        <canvas id="issueChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">Sentiment Distribution</div>
                        <canvas id="sentimentChart"></canvas>
                    </div>
                </div>
                
                <!-- Recent Interactions -->
                <div class="recent-interactions">
                    <div class="chart-title">Recent Interactions</div>
                    <table class="interactions-table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Customer</th>
                                <th>Tier</th>
                                <th>Issue</th>
                                <th>Sentiment</th>
                                <th>Priority</th>
                                <th>Email</th>
                            </tr>
                        </thead>
                        <tbody id="recentInteractionsTable">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let issueChart, sentimentChart;
        
        async function loadDashboardData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                if (data.message) {
                    document.getElementById('loading').innerHTML = 
                        '<div class="no-data">📊 ' + data.message + '<br><br>Try running some test requests first!</div>';
                    return;
                }
                
                updateOverviewCards(data.overview);
                updateCharts(data);
                updateRecentInteractions(data.recent_interactions);
                await loadInsights(); // Load AI insights
                
                document.getElementById('loading').style.display = 'none';
                document.getElementById('dashboard-content').style.display = 'block';
                document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
                
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                document.getElementById('loading').innerHTML = 
                    '<div class="no-data">❌ Error loading data: ' + error.message + '</div>';
            }
        }
        
        async function loadInsights() {
            try {
                const response = await fetch('/api/insights');
                const data = await response.json();
                updateInsightsSection(data.insights);
            } catch (error) {
                console.error('Error loading insights:', error);
                updateInsightsSection([]);
            }
        }
        
        function updateInsightsSection(insights) {
            const container = document.getElementById('insightsContainer');
            
            if (insights.length === 0) {
                container.innerHTML = '<div class="no-data">🤖 No AI insights yet. Generate some data first or check if the insights service is running!</div>';
                return;
            }
            
            const insight = insights[0];
            
            // Ensure key_findings is an array of strings
            const keyFindings = Array.isArray(insight.key_findings) ? insight.key_findings : [];
            const alerts = Array.isArray(insight.alerts) ? insight.alerts : [];
            const recommendations = Array.isArray(insight.recommendations) ? insight.recommendations : [];
            
            container.innerHTML = `
                <div class="insight-card insight-${insight.severity}">
                    <div class="insight-title">${insight.title}</div>
                    <div class="insight-message">${insight.overview}</div>
                    
                    <div style="margin: 15px 0;">
                        <strong>🔍 Key Findings:</strong>
                        <ul style="margin: 5px 0 0 20px;">
                            ${keyFindings.length > 0 ? 
                                keyFindings.map(finding => `<li>${String(finding)}</li>`).join('') : 
                                '<li>No key findings available</li>'
                            }
                        </ul>
                    </div>
                    
                    ${alerts.length > 0 ? `
                    <div style="margin: 15px 0;">
                        <strong>⚠️ Alerts:</strong>
                        <ul style="margin: 5px 0 0 20px; color: #dc3545;">
                            ${alerts.map(alert => `<li>${String(alert)}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                    
                    <div style="margin: 15px 0;">
                        <strong>💡 Recommendations:</strong>
                        <ul style="margin: 5px 0 0 20px;">
                            ${recommendations.length > 0 ? 
                                recommendations.map(rec => `<li>${String(rec)}</li>`).join('') : 
                                '<li>No recommendations available</li>'
                            }
                        </ul>
                    </div>
                    
                    <div style="margin: 15px 0;">
                        <strong>📈 Trends:</strong> ${insight.trends || 'No trend data available'}
                    </div>
                    
                    <div class="insight-meta">
                        <span class="insight-type">${insight.type}</span>
                        <span>Data Points: ${insight.data_points} | Updated: ${new Date(insight.generated_at).toLocaleString()}</span>
                    </div>
                </div>
            `;
        }
        
        function updateOverviewCards(overview) {
            document.getElementById('totalInteractions').textContent = overview.total_interactions;
            document.getElementById('highPriority').textContent = overview.high_priority;
            document.getElementById('negativeSentiment').textContent = overview.negative_sentiment;
            document.getElementById('emailsSent').textContent = overview.emails_sent;
            document.getElementById('avgConfidence').textContent = (overview.avg_confidence * 100).toFixed(1) + '%';
            document.getElementById('avgResponseTime').textContent = overview.avg_response_time + 'ms';
        }
        
        function updateCharts(data) {
            // Issue Distribution Chart
            const issueCtx = document.getElementById('issueChart').getContext('2d');
            if (issueChart) issueChart.destroy();
            
            if (data.issue_distribution.length > 0) {
                issueChart = new Chart(issueCtx, {
                    type: 'doughnut',
                    data: {
                        labels: data.issue_distribution.map(item => item.issue_type),
                        datasets: [{
                            data: data.issue_distribution.map(item => item.count),
                            backgroundColor: [
                                '#667eea', '#764ba2', '#f093fb', '#f5576c',
                                '#4facfe', '#00f2fe', '#a8edea', '#fed6e3'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
            
            // Sentiment Distribution Chart
            const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
            if (sentimentChart) sentimentChart.destroy();
            
            if (data.sentiment_distribution.length > 0) {
                const sentimentColors = {
                    'positive': '#28a745',
                    'negative': '#dc3545',
                    'neutral': '#6c757d'
                };
                
                sentimentChart = new Chart(sentimentCtx, {
                    type: 'pie',
                    data: {
                        labels: data.sentiment_distribution.map(item => item.sentiment),
                        datasets: [{
                            data: data.sentiment_distribution.map(item => item.count),
                            backgroundColor: data.sentiment_distribution.map(item => 
                                sentimentColors[item.sentiment] || '#6c757d'
                            )
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
        }
        
        function updateRecentInteractions(interactions) {
            const tbody = document.getElementById('recentInteractionsTable');
            tbody.innerHTML = '';
            
            if (interactions.length === 0) {
                const row = tbody.insertRow();
                row.innerHTML = '<td colspan="7" style="text-align: center; color: #666;">No interactions yet</td>';
                return;
            }
            
            interactions.forEach(interaction => {
                const row = tbody.insertRow();
                
                // Format timestamp
                const timestamp = new Date(interaction.timestamp).toLocaleString();
                
                row.innerHTML = `
                    <td>${timestamp}</td>
                    <td>${interaction.customer_id}</td>
                    <td>${interaction.customer_tier}</td>
                    <td>${interaction.issue_type}</td>
                    <td class="sentiment-${interaction.sentiment}">${interaction.sentiment}</td>
                    <td><span class="priority-${interaction.priority}">${interaction.priority}</span></td>
                    <td>${interaction.email_sent ? '✅' : '❌'}</td>
                `;
            });
        }
        
        function refreshData() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('dashboard-content').style.display = 'none';
            loadDashboardData();
        }
        
        // Load data on page load
        document.addEventListener('DOMContentLoaded', loadDashboardData);
        
        // Auto-refresh every 30 seconds
        setInterval(loadDashboardData, 30000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🎯 Starting Analytics Dashboard Server...")
    print("📊 Dashboard will be available at: http://localhost:5002")
    print("🤖 AI Insights integrated from port 5003")
    print("🔄 Auto-refreshes every 30 seconds")
    print("💡 Send some requests to your AI service first to see data!")
    
    app.run(host='0.0.0.0', port=5002, debug=True)