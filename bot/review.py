import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# example function to test the PR check
diff = """
+ def add(a, b):
+   return a - b

"""
# ai prompt
response = client.messages.create(
    model = "claude-opus-4-5",
    max_tokens = 1024,
    messages = [
        {"role": "user", "content": f"Review this code diff and flag any bugs or issues:\n\n{diff}"}
    ]

)

print("PRism bot has been triggered")
print("Pull request has been opened or updated")
print(response.content[0].text)