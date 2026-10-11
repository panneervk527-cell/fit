from google import genai

# If your API key is stored in an environment variable, you can just use genai.Client()
client = genai.Client(api_key="AQ.Ab8RN6IePvC4X2QmEfpH7w-8Le8HTmRoEVmrJuO40JyPgXf40w")

try:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents="Hello"
    )
    print(response.text)
except Exception as e:
    print(f"An error occurred: {e}")
