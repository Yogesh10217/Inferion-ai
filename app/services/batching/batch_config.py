from dataclasses import dataclass

@dataclass
class BatchConfig:
    enabled: bool = True
    max_batch_size: int = 10
    max_batch_wait_ms: int = 50
    max_queue_tokens: int = 10000
