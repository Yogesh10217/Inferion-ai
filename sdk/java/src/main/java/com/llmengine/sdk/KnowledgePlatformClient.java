package com.llmengine.sdk;

import java.util.HashMap;
import java.util.Map;

public class KnowledgePlatformClient {
    private final String baseUrl;
    private final String apiKey;

    public KnowledgePlatformClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    public Map<String, Object> createKnowledge(String title, String content, String tenantId) {
        Map<String, Object> res = new HashMap<>();
        res.put("title", title);
        res.put("tenant_id", tenantId);
        res.put("status", "ACTIVE");
        return res;
    }
}
