#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText

def test_gmail_methods():
    """Test different Gmail authentication methods"""
    
    gmail_email = input("Enter your Gmail address: ").strip()
    
    print("\n🔧 Choose authentication method:")
    print("1. App Password (16 characters)")
    print("2. Regular Gmail password (with less secure apps enabled)")
    
    method = input("Choice (1 or 2): ").strip()
    
    if method == "1":
        password = input("Enter your App Password (no spaces): ").strip()
        auth_type = "App Password"
    elif method == "2":
        password = input("Enter your regular Gmail password: ").strip()
        auth_type = "Regular Password"
    else:
        print("❌ Invalid choice")
        return
    
    print(f"\n🔍 Testing {auth_type} authentication...")
    print(f"📧 Email: {gmail_email}")
    print(f"🔐 Password length: {len(password)} characters")
    
    try:
        # Create test message
        msg = MIMEText("🧪 Gmail authentication test successful!")
        msg['Subject'] = "Gmail Auth Test"
        msg['From'] = gmail_email
        msg['To'] = gmail_email
        
        # Connect and send
        print("📡 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 Authenticating...")
        server.login(gmail_email, password)
        
        print("📧 Sending test email...")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ SUCCESS! {auth_type} authentication works!")
        print(f"📬 Check your inbox: {gmail_email}")
        
        return True, gmail_email, password, auth_type
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        
        if "App passwords aren't working" in str(e) or "BadCredentials" in str(e):
            print("\n💡 Troubleshooting suggestions:")
            print("1. Generate a NEW App Password")
            print("2. Or enable 'Less secure app access' and use regular password")
            print("3. Make sure 2-Step Verification is ON")
        
        return False, None, None, None
        
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False, None, None, None

if __name__ == "__main__":
    print("🚀 Gmail Authentication Tester")
    print("=" * 35)
    
    success, email, password, auth_type = test_gmail_methods()
    
    if success:
        print(f"\n📝 Working credentials found:")
        print(f"   Email: {email}")
        print(f"   Auth: {auth_type}")
        print(f"   Password: {'*' * len(password)}")
        
        # Offer to update .env.real
        update = input("\nUpdate .env.real with working credentials? (y/n): ").strip().lower()
        if update == 'y':
            with open('.env.real', 'w') as f:
                f.write(f"# Working Gmail Configuration\n")
                f.write(f"GMAIL_EMAIL={email}\n")
                f.write(f"GMAIL_APP_PASSWORD={password}\n")
                f.write(f"TEST_EMAIL={email}\n")
                f.write(f"USE_REAL_EMAIL=true\n")
            print("✅ .env.real updated!")
    else:
        print("\n🔧 Next steps:")
        print("1. Try generating a new App Password")
        print("2. Or enable 'Less secure app access'")
        print("3. Verify 2-Step Verification is ON")
