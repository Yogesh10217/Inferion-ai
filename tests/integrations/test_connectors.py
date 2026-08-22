"""Unit tests for SaaS connectors (Slack, GitHub, Jira, REST)."""

import pytest
from app.integrations.connector import SlackConnector, GitHubConnector, JiraConnector, RESTConnector


def test_saas_connectors_execution():
    slack = SlackConnector()
    assert slack.health_check() is True
    res_slack = slack.execute("post_message", {"channel": "alerts"})
    assert res_slack["status"] == "SUCCESS"

    github = GitHubConnector()
    assert github.health_check() is True
    res_gh = github.execute("create_issue", {"repo": "org/repo"})
    assert res_gh["status"] == "SUCCESS"

    jira = JiraConnector()
    res_jira = jira.execute("create_ticket")
    assert res_jira["ticket_id"] == "JIRA-101"
