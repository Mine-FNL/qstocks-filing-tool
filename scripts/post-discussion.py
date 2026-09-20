#!/usr/bin/env python3
"""Post a release announcement to the repo's GitHub Discussions.

Used by .github/workflows/discussion-on-release.yml. Reads the release
metadata from env (TAG, NAME, URL, BODY), looks up the Announcements
category ID, and creates a Discussion with a body containing the
release notes + a quick-links block.

The GITHUB_TOKEN env var must have `discussions: write` scope (the
workflow sets that at the job level).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

GRAPHQL_URL = "https://api.github.com/graphql"
OWNER = "Mine-FNL"
REPO = "qstocks-filing-tool"


def graphql(token: str, query: str, variables: dict) -> dict:
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main() -> int:
    token = os.environ["GH_TOKEN"]
    tag = os.environ.get("TAG", "").strip()
    name = os.environ.get("NAME", "").strip()
    url = os.environ.get("URL", "").strip()
    body = os.environ.get("BODY") or ""

    # Guard: refuse to post a malformed announcement. On workflow_dispatch
    # without inputs we used to post a Discussion titled "Released v"
    # with an empty body. Hard-fail instead so the run is visibly red.
    if not tag:
        print(
            "ERROR: TAG env var is empty. Set TAG=vX.Y.Z for releases, "
            "or pass --input tag=... for workflow_dispatch re-runs.",
            file=sys.stderr,
        )
        return 2
    if not name:
        print(
            "ERROR: NAME env var is empty. workflow_dispatch re-runs "
            "must supply tag + name (and ideally url + body).",
            file=sys.stderr,
        )
        return 2
    if not url:
        print(
            "WARNING: URL is empty; the Release notes link will be a "
            "placeholder. Set github.event.release.html_url or pass "
            "--input url=...",
            file=sys.stderr,
        )

    version = tag.lstrip("v")

    title = f"Released v{version} — {name}".strip(" —")

    # Find the Announcements category ID.
    cats_resp = graphql(
        token,
        """
        query Categories($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            discussionCategories(first: 20) { nodes { id slug } }
          }
        }
        """,
        {"owner": OWNER, "name": REPO},
    )
    cat_id = None
    for c in cats_resp["data"]["repository"]["discussionCategories"]["nodes"]:
        if c["slug"] == "announcements":
            cat_id = c["id"]
            break
    if not cat_id:
        print("ERROR: announcements category not found", file=sys.stderr)
        return 1

    # Find the repository node ID (needed for the createDiscussion mutation).
    repo_resp = graphql(
        token,
        """
        query RepoId($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) { id }
        }
        """,
        {"owner": OWNER, "name": REPO},
    )
    repo_id = repo_resp["data"]["repository"]["id"]

    # Compose the Discussion body. Three consecutive dashes inside a
    # markdown block become a horizontal rule.
    post = (
        f"{body}\n\n"
        f"---\n\n"
        f"### Quick links\n\n"
        f"- [Release notes]({url})\n"
        f"- [Live bench report]"
        f"(https://mine-fnl.github.io/qstocks-filing-tool/demo.html)\n"
        f"- [Whitepaper (PDF)]"
        f"(https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.pdf)\n"
        f"- [Investor one-pager]"
        f"(https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/investor-one-pager/one-pager.pdf)\n"
        f"- [Marketing site](https://qscreen-filing-tool.vercel.app/)\n\n"
        f"### Try it\n\n"
        f"```sh\n"
        f"pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest/download/"
        f"qscreen_filing_tool-{version}-py3-none-any.whl\n"
        f"qscreen-demo\n"
        f"```\n\n"
        f"<sub>Posted automatically by discussion-on-release.yml. "
        f"To disable, delete the workflow file or remove the "
        f"`discussions: write` permission.</sub>"
    )

    # Create the Discussion.
    create_resp = graphql(
        token,
        """
        mutation CreateDiscussion(
          $title: String!, $body: String!, $repo: ID!, $cat: ID!
        ) {
          createDiscussion(input: {
            repositoryId: $repo, categoryId: $cat,
            title: $title, body: $body
          }) { discussion { url } }
        }
        """,
        {"title": title, "body": post, "repo": repo_id, "cat": cat_id},
    )
    if "errors" in create_resp:
        print("GraphQL errors:", create_resp["errors"], file=sys.stderr)
        return 1

    discussion_url = create_resp["data"]["createDiscussion"]["discussion"]["url"]
    print(f"Posted: {discussion_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
