class PluginError(Exception):
    pass


class PluginLoadError(PluginError):
    pass


class PluginPermissionError(PluginError):
    pass


class PluginLifecycleError(PluginError):
    pass


class PluginExecutionError(PluginError):
    pass


class PluginDependencyError(PluginError):
    pass
