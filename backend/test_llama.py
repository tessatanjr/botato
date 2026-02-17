from ollama import Client

client = Client()

# Test llama3
resp_7b = client.chat(
    model="llama3:latest",
    messages=[{"role":"user", "content":"Echo Hello Tyler tq for helping me run...u r d goat"}]
)
print("llama3:latest output:", resp_7b["message"]["content"])
