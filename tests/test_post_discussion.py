#!/usr/bin/env python3
"""Tests for scripts/post-discussion.py — the release-announcement script.

The script is the only thing standing between a malformed release Discussion
(e.g. title="Released v", empty body) and the public announcements category.
These tests pin the validation contract so a refactor can't silently
re-introduce the empty-post bug.

Two layers:
  1. In-process tests load the module and call main() directly with mocked
     GraphQL responses — verify validation and body composition cheaply.
  2. Subprocess tests run `python post-discussion.py` end-to-end so the
     __main__ SystemExit wrapper and CLI entry are also covered.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "post-discussion.py"


def _load_module():
    """Import post-discussion.py as a module without running __main__."""
    spec = importlib.util.spec_from_file_location("post_discussion", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# 1. Validation contract: refuse empty TAG / NAME with exit 2
# ---------------------------------------------------------------------------


def test_empty_tag_returns_2():
    """The original bug: empty TAG used to silently post a broken Discussion."""
    mod = _load_module()
    with mock.patch.dict(
        os.environ,
        {"GH_TOKEN": "fake", "TAG": "", "NAME": "x", "URL": "u", "BODY": "b"},
        clear=True,
    ):
        rc = mod.main()
    assert rc == 2


def test_missing_tag_returns_2():
    """Default behavior when TAG is unset must also refuse."""
    mod = _load_module()
    env = {"GH_TOKEN": "fake", "NAME": "x"}
    with mock.patch.dict(os.environ, env, clear=True):
        rc = mod.main()
    assert rc == 2


def test_empty_name_returns_2():
    """NAME must also be required — title without a name is useless."""
    mod = _load_module()
    with mock.patch.dict(
        os.environ,
        {"GH_TOKEN": "fake", "TAG": "v1.7.0", "NAME": "", "URL": "u", "BODY": "b"},
        clear=True,
    ):
        rc = mod.main()
    assert rc == 2


def test_missing_name_returns_2():
    mod = _load_module()
    env = {"GH_TOKEN": "fake", "TAG": "v1.7.0"}
    with mock.patch.dict(os.environ, env, clear=True):
        rc = mod.main()
    assert rc == 2


def test_whitespace_only_tag_returns_2():
    """A tag of '   ' should not slip through .strip() — verify the strip
    is applied before the empty-check."""
    mod = _load_module()
    with mock.patch.dict(
        os.environ,
        {"GH_TOKEN": "fake", "TAG": "   ", "NAME": "x", "URL": "u", "BODY": "b"},
        clear=True,
    ):
        rc = mod.main()
    assert rc == 2


# ---------------------------------------------------------------------------
# 2. Happy path: with valid inputs, the script reaches the createDiscussion
#    GraphQL call with the right variables composed.
# ---------------------------------------------------------------------------


def _categories_response():
    return {
        "data": {
            "repository": {
                "discussionCategories": {
                    "nodes": [
                        {"id": "C1", "slug": "announcements"},
                        {"id": "C2", "slug": "general"},
                    ]
                }
            }
        }
    }


def _repo_response():
    return {"data": {"repository": {"id": "R1"}}}


def _create_response():
    return {"data": {"createDiscussion": {"discussion": {"url": "https://gh/x/D1"}}}}


def test_valid_inputs_reach_create_discussion():
    """Sanity: with TAG + NAME + URL + BODY, the script posts to GraphQL."""
    mod = _load_module()
    with (
        mock.patch.dict(
            os.environ,
            {
                "GH_TOKEN": "fake",
                "TAG": "v1.7.0",
                "NAME": "Test release",
                "URL": "https://gh/x/releases/v1.7.0",
                "BODY": "## Notes\nbody",
            },
            clear=True,
        ),
        mock.patch.object(
            mod,
            "graphql",
            side_effect=[
                _categories_response(),
                _repo_response(),
                _create_response(),
            ],
        ) as g,
    ):
        rc = mod.main()
    assert rc == 0
    assert g.call_count == 3
    # The 3rd call is createDiscussion. graphql() takes positional args
    # (token, query, variables), so variables are at index 2.
    create_vars = g.call_args_list[2].args[2]
    title = create_vars["title"]
    assert title.startswith("Released v1.7.0")
    assert "Test release" in title
    body = create_vars["body"]
    assert "## Notes" in body
    assert "Quick links" in body
    assert create_vars["repo"] == "R1"
    assert create_vars["cat"] == "C1"  # the announcements category ID


def test_tag_strips_v_prefix_in_pip_install_line():
    """The composed pip-install line should use the version WITHOUT 'v'."""
    mod = _load_module()
    with (
        mock.patch.dict(
            os.environ,
            {"GH_TOKEN": "fake", "TAG": "v2.3.4", "NAME": "x", "URL": "u", "BODY": "b"},
            clear=True,
        ),
        mock.patch.object(
            mod,
            "graphql",
            side_effect=[
                _categories_response(),
                _repo_response(),
                _create_response(),
            ],
        ) as g,
    ):
        mod.main()
    create_vars = g.call_args_list[2].args[2]
    body = create_vars["body"]
    assert "qscreen_filing_tool-2.3.4-" in body
    assert "qscreen_filing_tool-v2.3.4-" not in body


def test_url_appears_in_release_notes_link():
    """The Quick-links block must include the supplied release URL."""
    mod = _load_module()
    with (
        mock.patch.dict(
            os.environ,
            {
                "GH_TOKEN": "fake",
                "TAG": "v1.7.0",
                "NAME": "x",
                "URL": "https://example.com/my-release",
                "BODY": "b",
            },
            clear=True,
        ),
        mock.patch.object(
            mod,
            "graphql",
            side_effect=[
                _categories_response(),
                _repo_response(),
                _create_response(),
            ],
        ) as g,
    ):
        mod.main()
    body = g.call_args_list[2].args[2]["body"]
    assert "https://example.com/my-release" in body


# ---------------------------------------------------------------------------
# 3. Error paths: GraphQL errors + missing category both exit non-zero
# ---------------------------------------------------------------------------


def test_graphql_error_returns_1():
    """If the createDiscussion mutation returns errors, exit non-zero."""
    mod = _load_module()
    err = {"errors": [{"message": "boom"}]}
    with (
        mock.patch.dict(
            os.environ,
            {"GH_TOKEN": "fake", "TAG": "v1.7.0", "NAME": "x", "URL": "u", "BODY": "b"},
            clear=True,
        ),
        mock.patch.object(
            mod,
            "graphql",
            side_effect=[
                _categories_response(),
                _repo_response(),
                err,
            ],
        ),
    ):
        rc = mod.main()
    assert rc == 1


def test_missing_announcements_category_returns_1():
    """If the Announcements category isn't there, refuse — don't silently
    fall through to whatever default GraphQL picks."""
    mod = _load_module()
    no_announce = {
        "data": {
            "repository": {
                "discussionCategories": {
                    "nodes": [{"id": "C2", "slug": "general"}],  # no announcements
                }
            }
        }
    }
    with (
        mock.patch.dict(
            os.environ,
            {"GH_TOKEN": "fake", "TAG": "v1.7.0", "NAME": "x", "URL": "u", "BODY": "b"},
            clear=True,
        ),
        mock.patch.object(mod, "graphql", side_effect=[no_announce]),
    ):
        rc = mod.main()
    assert rc == 1


def test_missing_token_raises_keyerror():
    """No GH_TOKEN should be a hard failure (the script's own guard,
    not ours). Verifies the script requires the env var explicitly."""
    mod = _load_module()
    with (
        mock.patch.dict(
            os.environ,
            {"TAG": "v1.7.0", "NAME": "x"},  # no GH_TOKEN
            clear=True,
        ),
        pytest.raises(KeyError),
    ):
        mod.main()


# ---------------------------------------------------------------------------
# 4. Subprocess end-to-end: validates the __main__ SystemExit wrapper
# ---------------------------------------------------------------------------


def test_subprocess_empty_tag_exits_2():
    """End-to-end: `python post-discussion.py` with empty TAG exits 2."""
    env = {**os.environ, "GH_TOKEN": "fake", "TAG": "", "NAME": "x", "URL": "u", "BODY": "b"}
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 2
    assert "TAG" in proc.stderr


def test_subprocess_empty_name_exits_2():
    env = {**os.environ, "GH_TOKEN": "fake", "TAG": "v1.7.0", "NAME": "", "URL": "u", "BODY": "b"}
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 2
    assert "NAME" in proc.stderr


def test_subprocess_missing_token_exits_1():
    """Missing GH_TOKEN raises KeyError; the __main__ wrapper turns that
    into a non-zero exit. The exact code is whatever Python emits."""
    env = {k: v for k, v in os.environ.items() if k != "GH_TOKEN"}
    env.update({"TAG": "v1.7.0", "NAME": "x"})
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode != 0
