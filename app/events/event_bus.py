from abc import ABC, abstractmethod
import asyncio
from typing import Awaitable, Callable, Dict, List, Optional, Set
import logging

from app.events.event_serializer import EventEnvelope

logger = logging.getLogger(__name__)

SubscriberCallable = Callable[[EventEnvelope], Awaitable[None]]


class IEventBus(ABC):
    """Abstract event bus interface for pub/sub operations."""

    @abstractmethod
    async def publish(self, event: EventEnvelope) -> None:
        """Publish an event to all interested subscribers."""
        pass

    @abstractmethod
    def subscribe(self, event_type: str, handler: SubscriberCallable) -> None:
        """Subscribe a handler function to a specific event_type or wildcard '*'."""
        pass

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: SubscriberCallable) -> None:
        """Unsubscribe a handler from an event type."""
        pass


class InMemoryEventBus(IEventBus):
    """
    In-memory async publish/subscribe event bus.
    Enforces subscriber isolation so failures in one handler never affect others.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, Set[SubscriberCallable]] = {}
        self._wildcard_subscribers: Set[SubscriberCallable] = set()

    def subscribe(self, event_type: str, handler: SubscriberCallable) -> None:
        if event_type == "*":
            self._wildcard_subscribers.add(handler)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = set()
            self._subscribers[event_type].add(handler)

    def unsubscribe(self, event_type: str, handler: SubscriberCallable) -> None:
        if event_type == "*":
            self._wildcard_subscribers.discard(handler)
        elif event_type in self._subscribers:
            self._subscribers[event_type].discard(handler)

    async def publish(self, event: EventEnvelope) -> None:
        """
        Dispatches event to matching subscribers concurrently with error isolation.
        """
        handlers: Set[SubscriberCallable] = set(self._wildcard_subscribers)
        if event.event_type in self._subscribers:
            handlers.update(self._subscribers[event.event_type])

        if not handlers:
            return

        async def _safe_execute(handler: SubscriberCallable, env: EventEnvelope):
            try:
                await handler(env)
            except Exception as exc:
                logger.error(f"Subscriber failure for event {env.event_type} ({env.event_id}): {exc}", exc_info=True)

        tasks = [_safe_execute(h, event) for h in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)
