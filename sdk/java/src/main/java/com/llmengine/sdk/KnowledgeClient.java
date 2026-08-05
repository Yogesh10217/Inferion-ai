package com.llmengine.sdk;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

public class KnowledgeClient {
    private String apiKey;
    private String baseUrl = "http://localhost:8000";
    private HttpClient httpClient;

    public KnowledgeClient(String apiKey) {
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
    }

    public KnowledgeClient(String apiKey, String baseUrl) {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.httpClient = HttpClient.newHttpClient();
    }

    private HttpRequest.Builder getBuilder(String path) {
        return HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + path))
                .header("X-API-Key", apiKey)
                .header("Content-Type", "application/json");
    }

    private String sendRequest(HttpRequest request) throws IOException, InterruptedException {
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() >= 400) {
            throw new RuntimeException("API request failed with status: " + response.statusCode());
        }
        return response.body();
    }

    public String create(String jsonBody) throws IOException, InterruptedException {
        HttpRequest request = getBuilder("/v1/knowledge")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();
        return sendRequest(request);
    }

    public String list() throws IOException, InterruptedException {
        HttpRequest request = getBuilder("/v1/knowledge")
                .GET()
                .build();
        return sendRequest(request);
    }

    public String upload(String knowledgeId, File file) throws IOException, InterruptedException {
        String boundary = UUID.randomUUID().toString();
        byte[] fileBytes = Files.readAllBytes(file.toPath());
        
        StringBuilder body = new StringBuilder();
        body.append("--").append(boundary).append("\r\n");
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"").append(file.getName()).append("\"\r\n");
        body.append("Content-Type: application/octet-stream\r\n\r\n");
        
        byte[] headerBytes = body.toString().getBytes(StandardCharsets.UTF_8);
        byte[] footerBytes = ("\r\n--" + boundary + "--\r\n").getBytes(StandardCharsets.UTF_8);
        
        byte[] fullBytes = new byte[headerBytes.length + fileBytes.length + footerBytes.length];
        System.arraycopy(headerBytes, 0, fullBytes, 0, headerBytes.length);
        System.arraycopy(fileBytes, 0, fullBytes, headerBytes.length, fileBytes.length);
        System.arraycopy(footerBytes, 0, fullBytes, headerBytes.length + fileBytes.length, footerBytes.length);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/v1/knowledge/" + knowledgeId + "/upload"))
                .header("X-API-Key", apiKey)
                .header("Content-Type", "multipart/form-data; boundary=" + boundary)
                .POST(HttpRequest.BodyPublishers.ofByteArray(fullBytes))
                .build();

        return sendRequest(request);
    }

    public String search(String knowledgeId, String query) throws IOException, InterruptedException {
        String jsonBody = "{\"query\": \"" + query.replace("\"", "\\\"") + "\"}";
        HttpRequest request = getBuilder("/v1/knowledge/" + knowledgeId + "/search")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();
        return sendRequest(request);
    }

    public String retrieve(String knowledgeId) throws IOException, InterruptedException {
        HttpRequest request = getBuilder("/v1/knowledge/" + knowledgeId)
                .GET()
                .build();
        return sendRequest(request);
    }

    public String delete(String knowledgeId) throws IOException, InterruptedException {
        HttpRequest request = getBuilder("/v1/knowledge/" + knowledgeId)
                .DELETE()
                .build();
        return sendRequest(request);
    }

    public String reindex(String knowledgeId) throws IOException, InterruptedException {
        HttpRequest request = getBuilder("/v1/knowledge/" + knowledgeId + "/reindex")
                .POST(HttpRequest.BodyPublishers.noBody())
                .build();
        return sendRequest(request);
    }

    public String jobs(String knowledgeId) throws IOException, InterruptedException {
        HttpRequest request = getBuilder("/v1/knowledge/" + knowledgeId + "/jobs")
                .GET()
                .build();
        return sendRequest(request);
    }

    public String status(String knowledgeId) throws IOException, InterruptedException {
        HttpRequest request = getBuilder("/v1/knowledge/" + knowledgeId + "/status")
                .GET()
                .build();
        return sendRequest(request);
    }
}
