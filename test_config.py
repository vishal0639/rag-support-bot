"""Quick test to verify .env configuration"""
import config

print("="*50)
print("Configuration Test")
print("="*50)

# Test OpenAI API Key
if config.OPENAI_API_KEY:
    if config.OPENAI_API_KEY.startswith(('sk-', 'sk-proj-')):
        print("✅ OPENAI_API_KEY: Configured correctly")
        print(f"   Key starts with: {config.OPENAI_API_KEY[:10]}...")
    else:
        print("❌ OPENAI_API_KEY: Invalid format (should start with 'sk-')")
        print(f"   Current value: {config.OPENAI_API_KEY[:20]}...")
else:
    print("❌ OPENAI_API_KEY: Not set!")
    print("   Please add your OpenAI API key to .env file")

# Test TARGET_WEBSITE
if config.TARGET_WEBSITE:
    print(f"✅ TARGET_WEBSITE: {config.TARGET_WEBSITE}")
else:
    print("❌ TARGET_WEBSITE: Not set!")

# Test MAX_PAGES
print(f"✅ MAX_PAGES: {config.MAX_PAGES}")

print("="*50)
print("\nIf all items show ✅, you're ready to go!")
print("Next step: python indexer.py --reset")
print("="*50)

