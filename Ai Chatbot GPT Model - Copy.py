import openai

openai.api_key = "cV-your-api-key-here"

def chat_with_gpt(prompt):
  response = openai.ChatCompletion.create(
      model = "gpt-3.5-turbo",
      messages = [{"role": "user", "content":prompt}]

  )
  return response.choices[0].messages.content.strip()


  if ___name___==__main__:
    while True:
      user_input = input("You: ")
      if user_input.lower() in ["quit","bye","exit"]:
        break
      response = chat_with_gpt(user_input)
      print("Chatbot: ", response)