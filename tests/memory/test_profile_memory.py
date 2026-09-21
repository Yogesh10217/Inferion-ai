"""
Tests for Profile Memory (Tier 4)
"""

from app.memory.profile_memory import ProfileMemory


def test_profile_memory_lifecycle():
    pm = ProfileMemory()
    prof = pm.create_profile(
        "user_101",
        {
            "preferred_language": "python",
            "preferred_framework": "fastapi",
            "interests": ["ai", "microservices"],
        },
    )

    assert prof.user_id == "user_101"
    assert prof.preferred_framework == "fastapi"
    assert "ai" in prof.interests

    updated = pm.update_profile("user_101", {"preferred_framework": "django"})
    assert updated.preferred_framework == "django"

    retrieved = pm.get_profile("user_101")
    assert retrieved.preferred_framework == "django"

    assert pm.delete_profile("user_101") is True
    assert pm.delete_profile("user_101") is False
