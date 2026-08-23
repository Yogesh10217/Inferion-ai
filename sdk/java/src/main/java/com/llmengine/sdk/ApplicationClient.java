package com.llmengine.sdk;

import java.util.HashMap;
import java.util.Map;

public class ApplicationClient {
    private final String baseUrl;
    private final String apiKey;

    public ApplicationClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    public Map<String, Object> createApplication(String name, String appType, String tenantId) {
        Map<String, Object> response = new HashMap<>();
        response.put("application_id", "app_" + name.toLowerCase().replace(" ", "_"));
        response.put("name", name);
        response.put("app_type", appType);
        response.put("tenant_id", tenantId);
        response.put("status", "DRAFT");
        return response;
    }
}
