import anthropic
import requests
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


#real def function to trigger the PR check
def fetch_pr_diff():
    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPO")
    pr_number = os.environ.get("PR_NUMBER")

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    headers = {
        "Authorization": f"bearer {github_token}",
        "Accept": "application/vnd.github.v3.diff"

    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch PR diff: {response.status_code} - {response.text}")
    return response.text

diff = fetch_pr_diff()
print("Fetched PR diff successfully")
print("DIFF REVIEW:")
print(diff[:1000])


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