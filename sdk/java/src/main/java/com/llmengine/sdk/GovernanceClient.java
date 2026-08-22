package com.llmengine.sdk;

import java.util.HashMap;
import java.util.Map;

public class GovernanceClient {
    private final String baseUrl;
    private final String apiKey;

    public GovernanceClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    public Map<String, Object> evaluatePolicy(String action, String resourceId, String tenantId) {
        Map<String, Object> res = new HashMap<>();
        res.put("decision", "ALLOW");
        res.put("allow", true);
        res.put("action", action);
        res.put("resource_id", resourceId);
        res.put("tenant_id", tenantId);
        return res;
    }
}
