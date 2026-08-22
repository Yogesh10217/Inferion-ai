package com.llmengine.sdk;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ControlPlaneClient {
    private final String baseUrl;
    private final HttpClient client;

    public ControlPlaneClient(String baseUrl) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.client = HttpClient.newHttpClient();
    }

    public String getSummary() throws Exception {
        HttpRequest req = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/control-plane/summary"))
                .GET()
                .build();
        HttpResponse<String> resp = client.send(req, HttpResponse.BodyHandlers.ofString());
        return resp.body();
    }
}
