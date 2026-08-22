package com.llmengine.sdk;

import java.util.HashMap;
import java.util.Map;

public class DeveloperPlatformClient {
    private final String baseUrl;
    private final String apiKey;

    public DeveloperPlatformClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    public Map<String, Object> createProject(String name, String tenantId) {
        Map<String, Object> res = new HashMap<>();
        res.put("name", name);
        res.put("tenant_id", tenantId);
        res.put("status", "ACTIVE");
        return res;
    }
}
