package com.llmengine.sdk;

import java.util.HashMap;
import java.util.Map;

public class IdentityClient {
    private final String baseUrl;
    private final String apiKey;

    public IdentityClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    public Map<String, Object> createIdentity(String username, String identityType, String tenantId) {
        Map<String, Object> res = new HashMap<>();
        res.put("username", username);
        res.put("identity_type", identityType);
        res.put("tenant_id", tenantId);
        res.put("status", "ACTIVE");
        return res;
    }
}
