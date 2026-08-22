package com.llmengine.sdk;

import java.util.HashMap;
import java.util.Map;

public class IntegrationClient {
    private final String baseUrl;
    private final String apiKey;

    public IntegrationClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    public Map<String, Object> registerIntegration(String name, String category, String tenantId) {
        Map<String, Object> res = new HashMap<>();
        res.put("name", name);
        res.put("category", category);
        res.put("tenant_id", tenantId);
        res.put("status", "ACTIVE");
        return res;
    }
}
