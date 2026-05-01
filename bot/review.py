import os
import requests
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def fetch_pr_diff():

    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr_number = os.environ.get("PR_NUMBER")

    if not all([github_token, repo, pr_number]):
        raise ValueError("Missing required envirnonment variables")

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3.diff"
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch PR diff: {response.status_code} - {response.text}")

    return response.text

def post_review_comment(review):
    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr_number = os.environ.get("PR_NUMBER")

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {"body": review}
    response = requests.post(url, headers=headers, json=data, timeout=30)

    if response.status_code != 201:
        raise Exception(f"Failed to post comment: {response.status_code} - {response.text}")
    print("Review posted successfully")


diff = fetch_pr_diff()

print("Fetched PR diff successfully")
print("DIFF PREVIEW:")
print(diff[:1000])

response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": f"Review this code diff and flag any bugs or issues:\n\n{diff}"
        }
    ]
)

print("AI review completed")
print("PRism bot has been triggered")
print("Pull request has been opened or updated")

if not response.content or not hasattr(response.content[0], 'text'):
    raise Exception("Claude has returned empty or invalid response")
review = response.content[0].text

post_review_comment(review)
