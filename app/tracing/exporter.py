class ExporterRegistry:
    def __init__(self):
        self.exporters = {}
        
    def register(self, name: str, exporter):
        self.exporters[name] = exporter
