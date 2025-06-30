import pandas as pd
import numpy as np
import os

def generate_training_data():
    """Generate more realistic and diverse training data for better accuracy"""
    
    # Enhanced account access examples with specific keywords
    account_access_examples = [
        # Login/Password issues
        ("I can't log into my account and it's driving me crazy!", "account_access", "negative", 0.2),
        ("Your login system is broken, I've been trying for hours", "account_access", "negative", 0.1),
        ("Password reset isn't working, this is frustrating", "account_access", "negative", 0.3),
        ("I'm locked out of my account, need help immediately", "account_access", "negative", 0.2),
        ("Can't access my profile, getting error messages", "account_access", "neutral", 0.5),
        ("Having trouble logging in, could you assist?", "account_access", "neutral", 0.6),
        ("Login issue resolved, thank you for the help", "account_access", "positive", 0.8),
        
        # More specific account access issues
        ("Forgot my password, reset link not working", "account_access", "negative", 0.3),
        ("Account suspended, don't know why", "account_access", "negative", 0.2),
        ("Two-factor authentication not working", "account_access", "negative", 0.3),
        ("Username and password not being accepted", "account_access", "negative", 0.3),
        ("Can't sign in, keeps saying invalid credentials", "account_access", "negative", 0.3),
        ("Account locked after too many attempts", "account_access", "negative", 0.3),
        ("Security questions not working", "account_access", "negative", 0.3),
        ("Email verification not working for login", "account_access", "negative", 0.3),
        ("Account deactivated, need to reactivate", "account_access", "neutral", 0.5),
        ("Need help recovering my account", "account_access", "neutral", 0.5),
        ("How do I change my password?", "account_access", "neutral", 0.6),
        ("Need to update my login information", "account_access", "neutral", 0.6),
        ("Account settings not saving", "account_access", "negative", 0.4),
        ("Profile won't update, getting errors", "account_access", "negative", 0.4),
        ("Can't access dashboard, login fails", "account_access", "negative", 0.3),
        ("Session keeps timing out", "account_access", "negative", 0.4),
        ("Single sign-on not working", "account_access", "negative", 0.3),
        ("Authentication error when logging in", "account_access", "negative", 0.3),
        ("Account credentials not recognized", "account_access", "negative", 0.3),
        ("Login page won't load", "account_access", "negative", 0.4),
        ("Can't remember my security question answer", "account_access", "neutral", 0.5),
        ("Need to verify my identity to access account", "account_access", "neutral", 0.6),
        ("Account recovery successful, thank you!", "account_access", "positive", 0.8),
        ("Password reset worked perfectly", "account_access", "positive", 0.8),
        ("Sign-in process is smooth now", "account_access", "positive", 0.8),
        ("Login credentials updated successfully", "account_access", "positive", 0.8),
    ]
    
    # Enhanced shipping examples with specific keywords
    shipping_examples = [
        ("My package is lost and no one can tell me where it is!", "shipping", "negative", 0.1),
        ("Order was supposed to arrive yesterday, still nothing", "shipping", "negative", 0.3),
        ("Package damaged during shipping, very disappointed", "shipping", "negative", 0.2),
        ("Delivery was delayed without any notification", "shipping", "negative", 0.3),
        ("Wrong item delivered, this is unacceptable", "shipping", "negative", 0.2),
        ("Tracking shows delivered but I never received it", "shipping", "negative", 0.1),
        ("Package arrived late but in good condition", "shipping", "neutral", 0.6),
        ("Delivery was on time, thank you", "shipping", "positive", 0.8),
        ("Fast shipping, received earlier than expected!", "shipping", "positive", 0.9),
        ("Courier never showed up", "shipping", "negative", 0.2),
        ("Package left at wrong address", "shipping", "negative", 0.2),
        ("Shipping cost was too expensive", "shipping", "negative", 0.4),
        ("Express delivery failed", "shipping", "negative", 0.3),
        ("Tracking number doesn't work", "shipping", "negative", 0.3),
        ("Shipment stuck in transit", "shipping", "negative", 0.3),
        ("Box was crushed during delivery", "shipping", "negative", 0.2),
        ("Delivery truck missed my address", "shipping", "negative", 0.3),
        ("Package requires signature but no one home", "shipping", "neutral", 0.5),
        ("Delivery scheduled for tomorrow", "shipping", "neutral", 0.7),
        ("Tracking updated, package on the way", "shipping", "positive", 0.7),
        ("Great packaging, item arrived safely", "shipping", "positive", 0.8),
        ("Delivery driver was very professional", "shipping", "positive", 0.8),
    ]
    
    # Technical Support Examples
    technical_support_examples = [
        ("Your app keeps crashing, this is ridiculous", "technical_support", "negative", 0.2),
        ("Website is down, can't access anything", "technical_support", "negative", 0.3),
        ("Having technical difficulties with the platform", "technical_support", "neutral", 0.5),
        ("Need help setting up my new device", "technical_support", "neutral", 0.6),
        ("Could you walk me through the installation?", "technical_support", "neutral", 0.7),
        ("Technical issue resolved quickly, great support!", "technical_support", "positive", 0.9),
        ("Your tech team is amazing, fixed everything", "technical_support", "positive", 0.9),
        ("Software bug causing issues", "technical_support", "negative", 0.3),
        ("System error message keeps appearing", "technical_support", "negative", 0.3),
        ("Database connection failed", "technical_support", "negative", 0.3),
        ("API not responding", "technical_support", "negative", 0.3),
        ("Browser compatibility issues", "technical_support", "negative", 0.4),
        ("Need technical documentation", "technical_support", "neutral", 0.6),
        ("How do I configure the settings?", "technical_support", "neutral", 0.6),
        ("Installation guide was helpful", "technical_support", "positive", 0.8),
        ("System running smoothly now", "technical_support", "positive", 0.8),
    ]
    
    # Billing Issues
    billing_examples = [
        ("I was charged twice for the same order!", "billing", "negative", 0.1),
        ("Unexpected charges on my account, need explanation", "billing", "negative", 0.3),
        ("Billing error, please fix this immediately", "billing", "negative", 0.2),
        ("Question about my invoice", "billing", "neutral", 0.6),
        ("Need clarification on recent charges", "billing", "neutral", 0.5),
        ("Billing issue resolved, thank you", "billing", "positive", 0.8),
        ("Credit card declined", "billing", "negative", 0.3),
        ("Refund not processed", "billing", "negative", 0.3),
        ("Payment failed", "billing", "negative", 0.3),
        ("Subscription cancelled but still charged", "billing", "negative", 0.2),
        ("Invoice amount is incorrect", "billing", "negative", 0.3),
        ("Need receipt for purchase", "billing", "neutral", 0.6),
        ("Update payment method", "billing", "neutral", 0.6),
        ("Payment processed successfully", "billing", "positive", 0.8),
    ]
    
    # Product Quality Issues
    product_quality_examples = [
        ("Product doesn't work as advertised, want refund", "product_quality", "negative", 0.1),
        ("Item broke after one day, poor quality", "product_quality", "negative", 0.2),
        ("Not what I expected, very disappointed", "product_quality", "negative", 0.3),
        ("Product quality is terrible", "product_quality", "negative", 0.2),
        ("Item has defects, need replacement", "product_quality", "negative", 0.3),
        ("Product is okay but not great", "product_quality", "neutral", 0.5),
        ("Product works as expected", "product_quality", "positive", 0.7),
        ("Excellent quality, very satisfied!", "product_quality", "positive", 0.9),
        ("Material feels cheap", "product_quality", "negative", 0.3),
        ("Color is different from website", "product_quality", "negative", 0.4),
        ("Size doesn't match description", "product_quality", "negative", 0.3),
        ("Product missing parts", "product_quality", "negative", 0.2),
        ("Instructions unclear", "product_quality", "negative", 0.4),
        ("Good value for money", "product_quality", "positive", 0.7),
        ("Premium quality materials", "product_quality", "positive", 0.8),
    ]
    
    # Compliments
    compliment_examples = [
        ("Your customer service is outstanding!", "compliment", "positive", 0.9),
        ("Thank you for the excellent support", "compliment", "positive", 0.9),
        ("Best customer service I've ever experienced", "compliment", "positive", 1.0),
        ("Your team is amazing, keep up the good work", "compliment", "positive", 0.9),
        ("Really appreciate your quick response", "compliment", "positive", 0.8),
        ("You guys are the best!", "compliment", "positive", 0.9),
        ("Five star service!", "compliment", "positive", 0.9),
        ("Highly recommend your company", "compliment", "positive", 0.9),
        ("Exceeded my expectations", "compliment", "positive", 0.9),
        ("Professional and helpful staff", "compliment", "positive", 0.8),
    ]
    
    # General Inquiries
    general_examples = [
        ("What are your business hours?", "general", "neutral", 0.7),
        ("How can I contact support?", "general", "neutral", 0.6),
        ("Do you offer international shipping?", "general", "neutral", 0.7),
        ("What's your return policy?", "general", "neutral", 0.6),
        ("Thank you for the information", "general", "positive", 0.8),
        ("Where is your headquarters?", "general", "neutral", 0.7),
        ("Do you have a mobile app?", "general", "neutral", 0.7),
        ("What payment methods do you accept?", "general", "neutral", 0.7),
        ("How long is the warranty?", "general", "neutral", 0.6),
        ("Information was very helpful", "general", "positive", 0.8),
    ]
    
    # Refund Requests
    refund_examples = [
        ("I want my money back, this is unacceptable", "refund", "negative", 0.2),
        ("Need to return this item and get refunded", "refund", "negative", 0.4),
        ("Can I get a refund for this order?", "refund", "neutral", 0.5),
        ("How do I process a return?", "refund", "neutral", 0.6),
        ("Refund processed quickly, thank you", "refund", "positive", 0.8),
        ("Return merchandise authorization needed", "refund", "neutral", 0.5),
        ("Exchange instead of refund", "refund", "neutral", 0.6),
        ("Partial refund request", "refund", "neutral", 0.5),
        ("Store credit instead of cash refund", "refund", "neutral", 0.6),
        ("Refund policy is fair", "refund", "positive", 0.7),
    ]
    
    # Combine all examples
    all_examples = (account_access_examples + shipping_examples + technical_support_examples + 
                   billing_examples + product_quality_examples + compliment_examples + 
                   general_examples + refund_examples)
    
    # Add more synthetic variations for better balance
    synthetic_data = []
    
    # Account access synthetic variations
    account_keywords = ['login', 'password', 'account', 'sign in', 'authentication', 'credentials', 'username']
    account_problems = ['not working', 'failed', 'error', 'locked', 'suspended', 'blocked', 'invalid']
    
    for i in range(15):
        keyword = np.random.choice(account_keywords)
        problem = np.random.choice(account_problems)
        intensity = np.random.choice(['', 'very', 'extremely', 'really'])
        
        if np.random.random() < 0.7:  # 70% negative
            messages = [
                f"My {keyword} is {problem}",
                f"{keyword.title()} {problem}, {intensity} frustrated",
                f"Can't get {keyword} to work, {problem}",
                f"{keyword.title()} keeps saying {problem}"
            ]
            synthetic_data.append((np.random.choice(messages), "account_access", "negative", np.random.uniform(0.1, 0.4)))
        else:
            synthetic_data.append((f"{keyword.title()} working perfectly now", "account_access", "positive", np.random.uniform(0.7, 0.9)))
    
    # Shipping synthetic variations
    shipping_keywords = ['package', 'delivery', 'shipment', 'order', 'tracking', 'courier']
    shipping_problems = ['late', 'missing', 'damaged', 'lost', 'delayed', 'wrong']
    
    for i in range(15):
        keyword = np.random.choice(shipping_keywords)
        problem = np.random.choice(shipping_problems)
        
        if np.random.random() < 0.7:  # 70% negative
            messages = [
                f"My {keyword} is {problem}",
                f"{keyword.title()} {problem}, need help",
                f"{keyword.title()} arrived {problem}",
                f"Where is my {keyword}? It's {problem}"
            ]
            synthetic_data.append((np.random.choice(messages), "shipping", "negative", np.random.uniform(0.1, 0.4)))
        else:
            synthetic_data.append((f"{keyword.title()} arrived perfectly", "shipping", "positive", np.random.uniform(0.7, 0.9)))
    
    # Create DataFrame
    df = pd.DataFrame(all_examples, columns=['message', 'issue_type', 'sentiment', 'satisfaction_score'])
    
    # Add synthetic data
    if synthetic_data:
        synthetic_df = pd.DataFrame(synthetic_data, columns=['message', 'issue_type', 'sentiment', 'satisfaction_score'])
        df = pd.concat([df, synthetic_df], ignore_index=True)
    
    # Shuffle the data
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save to files
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/training_data.csv', index=False)
    
    # Create test data (smaller subset)
    test_df = df.sample(n=min(30, len(df)//4), random_state=42)
    test_df.to_csv('data/test_data.csv', index=False)
    
    print(f"✅ Generated {len(df)} training examples")
    print(f"✅ Generated {len(test_df)} test examples")
    print(f"📊 Issue type distribution:")
    issue_counts = df['issue_type'].value_counts()
    for issue_type, count in issue_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   {issue_type}: {count} examples ({percentage:.1f}%)")
    
    print(f"📊 Sentiment distribution:")
    sentiment_counts = df['sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   {sentiment}: {count} examples ({percentage:.1f}%)")
    
    return df

if __name__ == "__main__":
    generate_training_data()
