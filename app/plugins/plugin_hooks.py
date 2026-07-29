from enum import Enum


class PluginHook(str, Enum):
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    BEFORE_REQUEST = "before_request"
    AFTER_REQUEST = "after_request"
    BEFORE_INFERENCE = "before_inference"
    AFTER_INFERENCE = "after_inference"
    PROVIDER_SELECTED = "provider_selected"
    PROVIDER_FAILED = "provider_failed"
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_UNLOADED = "plugin_unloaded"
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
