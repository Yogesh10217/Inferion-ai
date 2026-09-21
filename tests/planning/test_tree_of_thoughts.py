"""
Tests for Tree of Thoughts Engine
"""

from app.reasoning.tree_of_thoughts import TreeOfThoughtsEngine


def test_tree_of_thoughts_search():
    tot = TreeOfThoughtsEngine(max_depth=2, max_branches=2)
    res = tot.search_best_path("Evaluate cloud migration")

    assert res["best_score"] > 0.0
    assert len(res["best_path"]) >= 2
    assert res["total_nodes_generated"] > 1
