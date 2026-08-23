package com.llmengine.sdk;

import java.util.Map;
import java.util.HashMap;

public class ArchitectureClient {
    private final String baseUrl;
    private final String apiKey;

    public ArchitectureClient(String baseUrl, String apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    public Map<String, Object> createNode(String name, String nodeType, String environment) {
        Map<String, Object> response = new HashMap<>();
        response.put("name", name);
        response.put("node_type", nodeType);
        response.put("environment", environment);
        response.put("status", "ACTIVE");
        return response;
    }

    public Map<String, Object> getTopology(String environment) {
        Map<String, Object> response = new HashMap<>();
        response.put("environment", environment);
        response.put("version", "1.0.0");
        return response;
    }
}
