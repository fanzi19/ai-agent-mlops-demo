import pandas as pd
import numpy as np
import os

def generate_training_data():
    """Generate more realistic and diverse training data for better accuracy"""
    
    # More comprehensive and realistic training examples
    training_examples = [
        # Account Access Issues - Negative
        ("I can't log into my account and it's driving me crazy!", "account_access", "negative", 0.2),
        ("Your login system is broken, I've been trying for hours", "account_access", "negative", 0.1),
        ("Password reset isn't working, this is frustrating", "account_access", "negative", 0.3),
        ("I'm locked out of my account, need help immediately", "account_access", "negative", 0.2),
        ("Can't access my profile, getting error messages", "account_access", "neutral", 0.5),
        ("Having trouble logging in, could you assist?", "account_access", "neutral", 0.6),
        ("Login issue resolved, thank you for the help", "account_access", "positive", 0.8),
        
        # Shipping Issues - Mostly Negative
        ("My package is lost and no one can tell me where it is!", "shipping", "negative", 0.1),
        ("Order was supposed to arrive yesterday, still nothing", "shipping", "negative", 0.3),
        ("Package damaged during shipping, very disappointed", "shipping", "negative", 0.2),
        ("Delivery was delayed without any notification", "shipping", "negative", 0.3),
        ("Wrong item delivered, this is unacceptable", "shipping", "negative", 0.2),
        ("Tracking shows delivered but I never received it", "shipping", "negative", 0.1),
        ("Package arrived late but in good condition", "shipping", "neutral", 0.6),
        ("Delivery was on time, thank you", "shipping", "positive", 0.8),
        ("Fast shipping, received earlier than expected!", "shipping", "positive", 0.9),
        
        # Technical Support - Mixed
        ("Your app keeps crashing, this is ridiculous", "technical_support", "negative", 0.2),
        ("Website is down, can't access anything", "technical_support", "negative", 0.3),
        ("Having technical difficulties with the platform", "technical_support", "neutral", 0.5),
        ("Need help setting up my new device", "technical_support", "neutral", 0.6),
        ("Could you walk me through the installation?", "technical_support", "neutral", 0.7),
        ("Technical issue resolved quickly, great support!", "technical_support", "positive", 0.9),
        ("Your tech team is amazing, fixed everything", "technical_support", "positive", 0.9),
        
        # Billing Issues - Negative/Neutral
        ("I was charged twice for the same order!", "billing", "negative", 0.1),
        ("Unexpected charges on my account, need explanation", "billing", "negative", 0.3),
        ("Billing error, please fix this immediately", "billing", "negative", 0.2),
        ("Question about my invoice", "billing", "neutral", 0.6),
        ("Need clarification on recent charges", "billing", "neutral", 0.5),
        ("Billing issue resolved, thank you", "billing", "positive", 0.8),
        
        # Product Issues - Negative
        ("Product doesn't work as advertised, want refund", "product_quality", "negative", 0.1),
        ("Item broke after one day, poor quality", "product_quality", "negative", 0.2),
        ("Not what I expected, very disappointed", "product_quality", "negative", 0.3),
        ("Product quality is terrible", "product_quality", "negative", 0.2),
        ("Item has defects, need replacement", "product_quality", "negative", 0.3),
        ("Product is okay but not great", "product_quality", "neutral", 0.5),
        ("Product works as expected", "product_quality", "positive", 0.7),
        ("Excellent quality, very satisfied!", "product_quality", "positive", 0.9),
        
        # Compliments - Positive
        ("Your customer service is outstanding!", "compliment", "positive", 0.9),
        ("Thank you for the excellent support", "compliment", "positive", 0.9),
        ("Best customer service I've ever experienced", "compliment", "positive", 1.0),
        ("Your team is amazing, keep up the good work", "compliment", "positive", 0.9),
        ("Really appreciate your quick response", "compliment", "positive", 0.8),
        ("You guys are the best!", "compliment", "positive", 0.9),
        
        # General Inquiries - Neutral/Positive
        ("What are your business hours?", "general", "neutral", 0.7),
        ("How can I contact support?", "general", "neutral", 0.6),
        ("Do you offer international shipping?", "general", "neutral", 0.7),
        ("What's your return policy?", "general", "neutral", 0.6),
        ("Thank you for the information", "general", "positive", 0.8),
        
        # Refund Requests - Negative/Neutral
        ("I want my money back, this is unacceptable", "refund", "negative", 0.2),
        ("Need to return this item and get refunded", "refund", "negative", 0.4),
        ("Can I get a refund for this order?", "refund", "neutral", 0.5),
        ("How do I process a return?", "refund", "neutral", 0.6),
        ("Refund processed quickly, thank you", "refund", "positive", 0.8),
    ]
    
    # Add more variations with different phrasings
    variations = []
    
    # Lost package variations
    lost_package_phrases = [
        ("Package never arrived, where is it?", "shipping", "negative", 0.2),
        ("My order is missing, been waiting for weeks", "shipping", "negative", 0.1),
        ("Shipment lost in transit, very frustrated", "shipping", "negative", 0.2),
        ("Order disappeared, tracking shows nothing", "shipping", "negative", 0.2),
        ("Package vanished, need immediate help", "shipping", "negative", 0.1),
    ]
    
    # Bad experience phrases
    bad_experience_phrases = [
        ("Worst experience ever with your company", "general", "negative", 0.1),
        ("Terrible service, will never buy again", "general", "negative", 0.1),
        ("Awful experience, completely disappointed", "general", "negative", 0.1),
        ("Horrible customer service, very upset", "general", "negative", 0.1),
        ("Bad experience overall, not recommended", "general", "negative", 0.2),
    ]
    
    # Combine all examples
    all_examples = training_examples + lost_package_phrases + bad_experience_phrases
    
    # Create DataFrame
    df = pd.DataFrame(all_examples, columns=['message', 'issue_type', 'sentiment', 'satisfaction_score'])
    
    # Add more synthetic variations
    synthetic_data = []
    base_negative_words = ['terrible', 'awful', 'horrible', 'worst', 'bad', 'disappointed', 'frustrated', 'angry']
    base_positive_words = ['excellent', 'amazing', 'great', 'wonderful', 'fantastic', 'perfect', 'outstanding']
    
    # Generate more shipping issues
    for i in range(20):
        if np.random.random() < 0.7:  # 70% negative shipping
            word = np.random.choice(base_negative_words)
            messages = [
                f"My package is {word}, still haven't received it",
                f"Shipping service is {word}, order is late",
                f"Delivery is {word}, where is my order?",
                f"{word.title()} shipping experience, package missing"
            ]
            synthetic_data.append((np.random.choice(messages), "shipping", "negative", np.random.uniform(0.1, 0.3)))
        else:
            word = np.random.choice(base_positive_words)
            messages = [
                f"Shipping was {word}, received quickly",
                f"{word.title()} delivery service, very happy",
                f"Package arrived safely, {word} job"
            ]
            synthetic_data.append((np.random.choice(messages), "shipping", "positive", np.random.uniform(0.8, 1.0)))
    
    # Add synthetic data
    synthetic_df = pd.DataFrame(synthetic_data, columns=['message', 'issue_type', 'sentiment', 'satisfaction_score'])
    df = pd.concat([df, synthetic_df], ignore_index=True)
    
    # Save to files
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/training_data.csv', index=False)
    
    # Create test data (smaller subset)
    test_df = df.sample(n=min(20, len(df)//4), random_state=42)
    test_df.to_csv('data/test_data.csv', index=False)
    
    print(f"✅ Generated {len(df)} training examples")
    print(f"✅ Generated {len(test_df)} test examples")
    print(f"📊 Issue type distribution:")
    print(df['issue_type'].value_counts())
    print(f"📊 Sentiment distribution:")
    print(df['sentiment'].value_counts())
    
    return df

if __name__ == "__main__":
    generate_training_data()
