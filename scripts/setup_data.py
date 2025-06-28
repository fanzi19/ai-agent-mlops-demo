#!/usr/bin/env python3
"""
Setup customer support training data for AI Agent MLOps Demo
Generates realistic customer feedback and support interaction data
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_customer_feedback_data():
    """Generate realistic customer support feedback data"""
    
    # Customer issues and corresponding responses
    support_scenarios = [
        {
            "issue_type": "billing",
            "customer_message": "I was charged twice for my subscription this month. Can you help me get a refund?",
            "agent_response": "I apologize for the billing error. I can see the duplicate charge on your account. I'll process a refund for the extra charge right away. You should see it reflected in 3-5 business days.",
            "resolution_time_hours": 0.5,
            "customer_satisfaction": "high",
            "sentiment": "initially_frustrated_then_satisfied"
        },
        {
            "issue_type": "technical",
            "customer_message": "The app keeps crashing when I try to upload photos. This is really frustrating!",
            "agent_response": "I understand how frustrating that must be. Let's troubleshoot this together. Can you tell me what device you're using and when the crashes started happening?",
            "resolution_time_hours": 2.5,
            "customer_satisfaction": "medium",
            "sentiment": "frustrated"
        },
        {
            "issue_type": "product_inquiry",
            "customer_message": "Do you have any plans that include more storage space? I'm running out of room.",
            "agent_response": "Yes! We have several plans with increased storage. Our Premium plan offers 500GB and Pro plan offers 2TB. Would you like me to show you the pricing and features?",
            "resolution_time_hours": 0.25,
            "customer_satisfaction": "high",
            "sentiment": "curious"
        },
        {
            "issue_type": "account_access",
            "customer_message": "I forgot my password and the reset email isn't coming through.",
            "agent_response": "I can help you regain access to your account. Let me check if there are any issues with your email delivery. Can you confirm the email address associated with your account?",
            "resolution_time_hours": 1.0,
            "customer_satisfaction": "medium",
            "sentiment": "confused"
        },
        {
            "issue_type": "feature_request",
            "customer_message": "It would be great if you could add dark mode to the app. Many users have been asking for this.",
            "agent_response": "Thank you for the feedback! Dark mode is actually on our development roadmap. I'll add your vote to this feature request. We expect to release it in the next quarter.",
            "resolution_time_hours": 0.5,
            "customer_satisfaction": "high",
            "sentiment": "hopeful"
        },
        {
            "issue_type": "cancellation",
            "customer_message": "I want to cancel my subscription. Your service isn't meeting my needs.",
            "agent_response": "I'm sorry to hear our service isn't meeting your expectations. Before we proceed with cancellation, could you tell me what specific issues you've encountered? There might be solutions we can explore.",
            "resolution_time_hours": 3.0,
            "customer_satisfaction": "low",
            "sentiment": "disappointed"
        },
        {
            "issue_type": "shipping",
            "customer_message": "My order was supposed to arrive yesterday but I still haven't received it. Where is it?",
            "agent_response": "I apologize for the delay. Let me track your order right now. I can see there was a shipping delay due to weather conditions. Your package is currently out for delivery and should arrive today.",
            "resolution_time_hours": 0.75,
            "customer_satisfaction": "medium",
            "sentiment": "impatient"
        },
        {
            "issue_type": "refund",
            "customer_message": "The product I received was damaged. I'd like to return it for a full refund.",
            "agent_response": "I'm very sorry the product arrived damaged. I'll immediately process a return label for you and initiate a full refund. You'll receive the return label via email within an hour.",
            "resolution_time_hours": 1.5,
            "customer_satisfaction": "high",
            "sentiment": "disappointed_then_relieved"
        }
    ]
    
    # Customer demographics and behavior patterns
    customer_segments = [
        {"segment": "enterprise", "interaction_frequency": "high", "value_tier": "premium"},
        {"segment": "small_business", "interaction_frequency": "medium", "value_tier": "standard"},
        {"segment": "individual", "interaction_frequency": "low", "value_tier": "basic"},
        {"segment": "startup", "interaction_frequency": "high", "value_tier": "growth"}
    ]
    
    # Generate expanded dataset
    expanded_data = []
    
    for i in range(500):  # Generate 500 customer interactions
        scenario = random.choice(support_scenarios)
        segment = random.choice(customer_segments)
        
        # Generate timestamp (last 30 days)
        days_ago = random.randint(0, 30)
        timestamp = datetime.now() - timedelta(days=days_ago)
        
        interaction = {
            "interaction_id": f"ticket_{i:05d}",
            "timestamp": timestamp.isoformat(),
            "customer_id": f"cust_{random.randint(1000, 9999)}",
            "customer_segment": segment["segment"],
            "interaction_channel": random.choice(["email", "chat", "phone", "app"]),
            
            # Issue details
            "issue_type": scenario["issue_type"],
            "priority": random.choice(["low", "medium", "high", "urgent"]),
            "customer_message": scenario["customer_message"],
            
            # Agent response
            "agent_id": f"agent_{random.randint(1, 20):02d}",
            "agent_response": scenario["agent_response"],
            "response_quality_score": random.uniform(0.7, 1.0),
            
            # Resolution metrics
            "resolution_time_hours": scenario["resolution_time_hours"] + random.uniform(-0.5, 1.0),
            "first_contact_resolution": random.choice([True, False]),
            "escalated": random.choice([True, False]) if scenario["issue_type"] in ["technical", "billing"] else False,
            
            # Customer feedback
            "customer_satisfaction": scenario["customer_satisfaction"],
            "sentiment": scenario["sentiment"],
            "csat_score": random.randint(1, 5),  # 1-5 rating
            "nps_score": random.randint(-2, 2),  # Net Promoter Score
            
            # Additional metadata
            "product_line": random.choice(["mobile_app", "web_platform", "api_service", "hardware"]),
            "customer_tier": segment["value_tier"],
            "follow_up_required": random.choice([True, False]),
            "tags": random.sample(["urgent", "bug", "feature", "billing", "onboarding", "training"], k=random.randint(1, 3))
        }
        
        # Ensure resolution time is positive
        interaction["resolution_time_hours"] = max(0.1, interaction["resolution_time_hours"])
        
        expanded_data.append(interaction)
    
    return expanded_data

def generate_feedback_analytics(data):
    """Generate analytics data for customer feedback"""
    df = pd.DataFrame(data)
    
    analytics = {
        "total_interactions": len(data),
        "date_range": {
            "start": df['timestamp'].min(),
            "end": df['timestamp'].max()
        },
        "issue_distribution": df['issue_type'].value_counts().to_dict(),
        "satisfaction_metrics": {
            "avg_csat": df['csat_score'].mean(),
            "avg_nps": df['nps_score'].mean(),
            "high_satisfaction_rate": (df['customer_satisfaction'] == 'high').mean(),
            "first_contact_resolution_rate": df['first_contact_resolution'].mean()
        },
        "performance_metrics": {
            "avg_resolution_time_hours": df['resolution_time_hours'].mean(),
            "avg_response_quality": df['response_quality_score'].mean(),
            "escalation_rate": df['escalated'].mean()
        },
        "channel_distribution": df['interaction_channel'].value_counts().to_dict(),
        "segment_analysis": df.groupby('customer_segment').agg({
            'csat_score': 'mean',
            'resolution_time_hours': 'mean',
            'customer_satisfaction': lambda x: (x == 'high').mean()
        }).to_dict()
    }
    
    return analytics

def save_customer_data(data, analytics):
    """Save customer support data and analytics"""
    
    # Create data directory
    os.makedirs("/workspace/data", exist_ok=True)
    
    # Save main dataset
    json_path = "/workspace/data/customer_feedback.json"
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"✅ Saved customer feedback data to {json_path}")
    
    # Save as CSV for analysis
    df = pd.DataFrame(data)
    csv_path = "/workspace/data/customer_feedback.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Saved CSV data to {csv_path}")
    
    # Save analytics
    analytics_path = "/workspace/data/feedback_analytics.json"
    with open(analytics_path, 'w') as f:
        json.dump(analytics, f, indent=2, default=str)
    print(f"✅ Saved analytics to {analytics_path}")
    
    # Create training splits
    train_size = int(0.8 * len(data))
    train_data = data[:train_size]
    test_data = data[train_size:]
    
    with open("/workspace/data/train_data.json", 'w') as f:
        json.dump(train_data, f, indent=2, default=str)
    
    with open("/workspace/data/test_data.json", 'w') as f:
        json.dump(test_data, f, indent=2, default=str)
    
    print(f"✅ Created training split: {len(train_data)} train, {len(test_data)} test")
    
    return len(data)

def main():
    """Generate customer support training data"""
    print("🚀 Generating customer support training data...")
    
    try:
        # Generate customer feedback data
        print("📋 Creating customer interactions...")
        feedback_data = generate_customer_feedback_data()
        
        # Generate analytics
        print("📊 Computing analytics...")
        analytics = generate_feedback_analytics(feedback_data)
        
        # Save everything
        print("💾 Saving data...")
        count = save_customer_data(feedback_data, analytics)
        
        print(f"\n✅ Successfully generated {count} customer interactions!")
        
        # Print summary
        print("\n📈 Dataset Summary:")
        print(f"   • Total interactions: {analytics['total_interactions']}")
        print(f"   • Average CSAT: {analytics['satisfaction_metrics']['avg_csat']:.2f}/5")
        print(f"   • First contact resolution: {analytics['satisfaction_metrics']['first_contact_resolution_rate']:.1%}")
        print(f"   • Average resolution time: {analytics['performance_metrics']['avg_resolution_time_hours']:.1f} hours")
        
        print("\n🎯 Issue Types:")
        for issue, count in analytics['issue_distribution'].items():
            print(f"   • {issue}: {count}")
        
        print("\n📱 Channels:")
        for channel, count in analytics['channel_distribution'].items():
            print(f"   • {channel}: {count}")
            
    except Exception as e:
        print(f"❌ Error generating customer data: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
