import json
from pydantic import BaseSettings
from github import Github

from ai_code_pal import get_chatgpt_suggestion


class Settings(BaseSettings):
    github_token: str
    github_event_path: str
    openai_api_key: str

    class Config:
        env_prefix = "INPUT_"


def get_changes_from_pull_request(pr):
    changes = []
    for file in pr.get_files():
        if file.patch is not None:
            changes.append(file.patch)
    return changes


def post_code_review_comments(pr, comments):
    for comment in comments:
        pr.create_review(body=comment, event="COMMENT")


def review_pull_request_from_gh_action():
    settings = Settings()
    github_token = settings.github_token
    event_path = settings.github_event_path

    gh = Github(github_token)

    # Get event payload
    with open(event_path, "r") as f:
        event_data = json.load(f)

    repo_name = event_data["repository"]["full_name"]
    pr_number = event_data["number"]
    review_pr(gh, repo_name, pr_number)


def review_pr(gh, repo_name, pr_number):
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    # Get changes in the pull request
    changes = get_changes_from_pull_request(pr)
    # Analyze the changes and get code review comments
    comments = []
    for change in changes:
        # We may need to split the changes into smaller code snippets
        # code_snippets = extract_code_snippets(change)
        code_snippets = [change]

        for code_snippet in code_snippets:
            comment = get_chatgpt_suggestion(code_snippet)

            if comment:
                comments.append(comment)
    # Post code review comments to the pull request
    post_code_review_comments(pr, comments)


if __name__ == "__main__":
    review_pull_request_from_gh_action()
