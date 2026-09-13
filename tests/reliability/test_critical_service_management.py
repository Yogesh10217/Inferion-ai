"""
Tests for Critical Service Management Module.
"""

from app.reliability.critical_service_management import CriticalService, CriticalServiceManager, ServiceCriticality


def test_critical_service_recovery_ordering():
    manager = CriticalServiceManager()
    s1 = CriticalService("s1", "Analytics", ServiceCriticality.LOW, priority=4, recovery_order=1)
    s2 = CriticalService("s2", "Core Database", ServiceCriticality.CRITICAL, priority=1, recovery_order=1)
    s3 = CriticalService("s3", "Auth Service", ServiceCriticality.CRITICAL, priority=1, recovery_order=2)

    manager.register_service(s1)
    manager.register_service(s2)
    manager.register_service(s3)

    seq = manager.get_recovery_sequence()
    assert [s.service_id for s in seq] == ["s2", "s3", "s1"]
    assert len(manager.get_critical_services()) == 2
