# Extensible Plugin Framework (Phase 4.0)

The **Plugin Framework** enables enterprise developers to extend the Inferion AI without modifying the core gateway codebase.

---

## Architecture Overview

```
 ┌─────────────────────────────────────────────────────────┐
 │                      PluginManager                      │
 └───────┬──────────────┬──────────────┬──────────────┬────┘
         │              │              │              │
 ┌───────▼──────┐┌──────▼──────┐┌──────▼──────┐┌──────▼──────┐
 │ LocalStore   ││  Registry   ││ Lifecycle   ││ Executor    │
 └──────────────┘└─────────────┘└─────────────┘└─────────────┘
```

The core engine remains completely decoupled from installed plugins. Plugins execute inside asynchronous isolation barriers with configurable timeout limits and strict permission boundaries.

---

## Plugin Manifest Schema (`manifest.json`)

```json
{
  "id": "hello_world",
  "name": "Hello World Plugin",
  "version": "1.0.0",
  "description": "Demonstrates basic lifecycle hooks and event handlers",
  "author": "AGY Engineering",
  "license": "MIT",
  "entrypoint": "plugin.py:HelloWorldPlugin",
  "minimum_engine_version": "1.0.0",
  "dependencies": {},
  "permissions": [
    {
      "action": "events.publish",
      "resource": "*"
    }
  ]
}
```

---

## Lifecycle State Machine

Plugins transition through 7 distinct states:

`DISCOVERED` -> `LOADED` -> `INITIALIZED` -> `ENABLED` -> `RUNNING` -> `DISABLED` -> `UNLOADED`

Only valid state transitions are permitted by the `PluginLifecycleManager`.

---

## Runtime Hook Reference

| Hook Name | Method Name | Description |
| :--- | :--- | :--- |
| `startup` | `on_startup` | Fired when system initializes |
| `shutdown` | `on_shutdown` | Fired on graceful shutdown |
| `before_request` | `on_before_request` | Pre-processing incoming request payloads |
| `after_request` | `on_after_request` | Post-processing responses before sending to client |
| `before_inference` | `on_before_inference` | Intercepting provider payloads |
| `after_inference` | `on_after_inference` | Accessing inference metrics & tokens |
| `provider_selected` | `on_provider_selected` | Fired when router chooses a provider |
| `provider_failed` | `on_provider_failed` | Fired when a provider request fails |
| `plugin_loaded` | `on_plugin_loaded` | Fired after a plugin is loaded into memory |
| `plugin_unloaded` | `on_plugin_unloaded` | Fired after a plugin is unloaded |

---

## Reference Example Plugins

Located under `app/plugins/examples/`:
1. `hello_world`: Basic lifecycle logging reference.
2. `metrics_logger`: Logs metrics upon inference completion.
3. `request_logger`: Logs incoming models and headers.
4. `audit_logger`: Audits provider selection decisions.
5. `response_modifier`: Attaches custom attributes to outputs.
6. `health_checker`: Monitors system health.
7. `event_listener`: Listens to provider failures and publishes bus events.

---

## Admin REST APIs

- `GET /v1/plugins`: List all registered plugins and statuses.
- `GET /v1/plugins/{id}`: Detailed manifest and health diagnostics.
- `POST /v1/plugins/install`: Install plugin by ID.
- `POST /v1/plugins/uninstall/{id}`: Uninstall and purge plugin.
- `POST /v1/plugins/enable/{id}`: Enable plugin.
- `POST /v1/plugins/disable/{id}`: Disable plugin.
- `POST /v1/plugins/reload/{id}`: Reload plugin into memory.
- `GET /v1/plugins/{id}/health`: Diagnostic health check.
