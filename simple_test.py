from gemini_rotator import GeminiRotator

# Initialize the client
try:
    ai_client = GeminiRotator()
    print("Client initialized.")
except Exception as e:
    print(f"Initialization failed: {e}")
    exit()

# Use a very simple, basic prompt
simple_prompt = "What is 2 + 2?"

print(f"Sending simple prompt: '{simple_prompt}'")
response = ai_client.generate_content(
    model_name="gemini-2.5-flash",  # Use a basic model for testing
    prompt=simple_prompt
)

if response:
    content = response.get("choices", [{}])[0].get("message", {}).get("content")
    print("\n--- Simple Test Response ---")
    print(content)
else:
    print("\n--- Simple Test Failed ---")