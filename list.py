import google.generativeai as genai
import os

api_key = os.getenv("AIzaSyBjRibjvGhaOtfcoV0LTcI_7w3qVvox0ng")
genai.configure(api_key=api_key)
models = genai.list_models()
for m in models:
    print(m.name, m.supported_generation_methods)