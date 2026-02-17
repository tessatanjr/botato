from ollama import Client

client = Client()

# Test 7B
resp_7b = client.chat(
    model="llama2:7b-chat-q4",
    messages=[{"role":"user", "content":"Echo Hello Tyler tq for helping me run...u r d goat"}]
)
print("7B output:", resp_7b["message"]["content"])

# Test 13B (GPU required)
resp_13b = client.chat(
    model="llama2:13b-chat-q4",
    messages=[{"role":"user", "content":"Express deep and heartfelt gratitude to a friend who helped u run a model. wish him happy chinese new year"}]
)
print("13B output:", resp_13b["message"]["content"])
