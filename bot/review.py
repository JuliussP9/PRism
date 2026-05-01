import os
import requests
import anthropic

def get_config():
    config = {
        "github_token": os.environ.get("GITHUB_TOKEN"),
        "repo": os.environ.get("GITHUB_REPOSITORY"),
        "pr_number": os.environ.get("PR_NUMBER"),
        "anthropic_key": os.environ.get("ANTHROPIC_API_KEY"),
    }
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    return config

def fetch_pr_diff(config):
    url = f"https://api.github.com/repos/{config['repo']}/pulls/{config['pr_number']}"
    headers = {
        "Authorization": f"Bearer {config['github_token']}",
        "Accept": "application/vnd.github.v3.diff"
    }
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch PR diff: {response.status_code}")
    return response.text

def post_review_comment(config, review):
    url = f"https://api.github.com/repos/{config['repo']}/issues/{config['pr_number']}/comments"
    headers = {
        "Authorization": f"Bearer {config['github_token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.post(url, headers=headers, json={"body": review}, timeout=30)
    if response.status_code != 201:
        raise Exception(f"Failed to post comment: {response.status_code}")
    print("Review posted successfully")

if __name__ == "__main__":
    config = get_config()
    client = anthropic.Anthropic(api_key=config["anthropic_key"])

    diff = fetch_pr_diff(config)
    if not diff.strip():
        raise Exception("PR diff is empty")

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

    if not response.content or not hasattr(response.content[0], 'text'):
        raise Exception("Claude returned empty or invalid response")

    review = response.content[0].text
    print(review)
    post_review_comment(config, review)
    