from openai import OpenAI

client = OpenAI(
        api_key="YOUR_OPENAI_API_KEY_HERE_PAID"  # Replace with your actual OpenAI API key
)

response = client.responses.create(
    model="gpt-5.6-luna",
    tools=[{"type": "web_search"}],
     
   
)

print(response.output_text)