from openai import OpenAI
 
# pip install openai 
# if you saved the key under a different environment variable name, you can do something like:
client = OpenAI(
  api_key="<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>",
)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud"},
    {"role": "user", "content": "what is coding"}
  ]
)

print(completion.choices[0].message.content)