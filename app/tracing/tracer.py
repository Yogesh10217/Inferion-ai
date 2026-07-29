import logging

class TracerConfig:
    def __init__(self):
        self.enabled = True

_tracer_config = TracerConfig()

def get_tracer(name: str):
    import logging
    return logging.getLogger(f"tracer.{name}")
