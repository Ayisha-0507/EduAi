import openai
import os

# ─────────────────────────────────────────────────────────────────────────────
#  EduAI — Model Availability Checker
#  Author : Ayisha
#  Reads API key from .streamlit/secrets.toml (never hardcoded).
# ─────────────────────────────────────────────────────────────────────────────

def _load_api_key():
    """Load the OpenRouter API key from .streamlit/secrets.toml or env var."""
    # 1. Try environment variable first
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key

    # 2. Try reading from .streamlit/secrets.toml
    secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        with open(secrets_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY"):
                    # Parse: OPENROUTER_API_KEY = "sk-or-..."
                    _, _, value = line.partition("=")
                    return value.strip().strip('"').strip("'")

    return None


def check_models():
    """Load API key and list all models available on OpenRouter."""
    try:
        print("--- OpenRouter Model Checker ---")
        print("This tool will help you see exactly which models your API key can access.")

        api_key = _load_api_key()

        if not api_key:
            print("\n❌ Error: API Key not found.")
            print("   Set it in .streamlit/secrets.toml as OPENROUTER_API_KEY")
            print("   or as an environment variable: OPENROUTER_API_KEY")
            return

        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

        print("\n✅ API Key configured. Fetching available models...")
        print("==============================================")

        models = client.models.list()
        found_models = False
        for m in models.data:
            print(f"✅ Model found: {m.id}")
            found_models = True

        print("==============================================")

        if found_models:
            print(f"\n💡 {len(models.data)} models available.")
            print("\nChecking your configured models:")
            target_ids = [
                "deepseek/deepseek-r1-0528:free",
                "arcee-ai/trinity-large-preview:free",
                "nousresearch/hermes-3-llama-3.1-405b:free",
                "black-forest-labs/flux.2-klein-4b",
                "nvidia/nemotron-nano-12b-v2-vl:free",
                "qwen/qwen3-vl-30b-a3b-thinking",
            ]
            for tid in target_ids:
                status = "✅ Available" if any(m.id == tid for m in models.data) else "❌ Not found"
                print(f"  {status}: {tid}")
        else:
            print("\n🤔 No models found for this API key. Please double-check your key.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("   This might be due to an invalid API key or a network issue.")

if __name__ == "__main__":
    check_models()

