#!/usr/bin/env bash
# Post-create hook for the qscreen-filing-tool dev container.
#
# Installs the GitHub CLI + the helper tools used by the bench / docs / CI
# surface. The Python extras are installed separately by `postCreateCommand`
# in devcontainer.json so the cache key is the right one for pip.

set -euo pipefail

echo ">>> qscreen-filing-tool dev container: post-create"

# GitHub CLI — used to trigger workflows, post bench PR comments, and
# manage releases without leaving the container.
if ! command -v gh >/dev/null 2>&1; then
    echo ">>> installing gh CLI"
    (type -p wget >/dev/null || (apt-get update && apt-get install -y wget)) \
        && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
            | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
        && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
        && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
            > /etc/apt/sources.list.d/github-cli.list \
        && apt-get update \
        && apt-get install -y gh
fi

# A few niceties — git-delta for nicer diffs, jq for JSON inspection.
for pkg in git-delta jq; do
    if ! command -v "${pkg%%-*}" >/dev/null 2>&1; then
        echo ">>> installing $pkg"
        apt-get install -y "$pkg" || true
    fi
done

echo ">>> post-create done. Try: make help"
echo ">>>                 make install-dev && make test && make bench"