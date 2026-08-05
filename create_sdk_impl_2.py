import os
import re

PROJECT_ROOT = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine"

def write_file(rel_path, content):
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# --- 3. GO SDK ---
write_file("sdk/go/knowledge.go", """
package llmengine

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
)

type KnowledgeClient struct {
	client *Client
}

func (k *KnowledgeClient) doReq(ctx context.Context, method, path string, body interface{}) (*http.Response, error) {
	var bodyReader *bytes.Reader
	if body != nil {
		buf, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		bodyReader = bytes.NewReader(buf)
	} else {
		bodyReader = bytes.NewReader([]byte{})
	}

	req, err := http.NewRequestWithContext(ctx, method, k.client.baseURL+path, bodyReader)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", "application/json")
	if k.client.apiKey != "" {
		req.Header.Set("X-API-Key", k.client.apiKey)
	}
	if k.client.orgID != "" {
		req.Header.Set("X-Organization-ID", k.client.orgID)
	}

	res, err := k.client.hc.Do(req)
	if err != nil {
		return nil, err
	}
	if res.StatusCode >= 400 {
		res.Body.Close()
		return nil, fmt.Errorf("request failed with status: %d", res.StatusCode)
	}
	return res, nil
}

func (k *KnowledgeClient) Create(ctx context.Context, name, description string) (map[string]interface{}, error) {
	res, err := k.doReq(ctx, "POST", "/v1/knowledge/create", map[string]string{"name": name, "description": description})
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	var out map[string]interface{}
	json.NewDecoder(res.Body).Decode(&out)
	return out, nil
}

func (k *KnowledgeClient) List(ctx context.Context) (map[string]interface{}, error) {
	res, err := k.doReq(ctx, "GET", "/v1/knowledge/list", nil)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	var out map[string]interface{}
	json.NewDecoder(res.Body).Decode(&out)
	return out, nil
}

// Additional Go methods...
""")

go_client_file = os.path.join(PROJECT_ROOT, "sdk/go/client.go")
if os.path.exists(go_client_file):
    with open(go_client_file, "r") as f:
        go_client_code = f.read()
    if "Knowledge *KnowledgeClient" not in go_client_code:
        go_client_code = go_client_code.replace("type Client struct {", "type Client struct {\n\tKnowledge *KnowledgeClient")
        go_client_code = re.sub(
            r"return &Client{.*?hc:.*?}",
            r"c := &Client{\n\t\tbaseURL: cfg.BaseURL,\n\t\tapiKey:  cfg.APIKey,\n\t\torgID:   cfg.OrganizationID,\n\t\thc:      &http.Client{Timeout: cfg.Timeout},\n\t}\n\tc.Knowledge = &KnowledgeClient{client: c}\n\treturn c",
            go_client_code,
            flags=re.DOTALL
        )
        with open(go_client_file, "w") as f:
            f.write(go_client_code)


# --- 4. JAVA SDK ---
write_file("sdk/java/pom.xml", """
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.llmengine</groupId>
    <artifactId>sdk</artifactId>
    <version>1.0.0</version>
</project>
""")


# --- 5. CLI UPDATES (use SDK exclusively) ---
write_file("cli/knowledge.py", """
import argparse
import sys
import json
import os
import yaml
from llm_engine.client import LLMEngineClient

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

BASE_URL = os.environ.get("KNOWLEDGE_API_URL", "http://localhost:8000")

def get_client():
    return LLMEngineClient(base_url=BASE_URL)

def format_output(data, fmt):
    if fmt == "json":
        print(json.dumps(data, indent=2))
    elif fmt == "yaml":
        print(yaml.dump(data))
    elif fmt == "table":
        if isinstance(data, dict):
            for k, v in data.items():
                print(f"{k}: {v}")
        else:
            print(data)
    elif fmt == "markdown":
        print("```json\\n" + json.dumps(data, indent=2) + "\\n```")

def handle_create(args):
    print(f"Creating index '{args.name}'...")
    client = get_client()
    data = client.knowledge.create(args.name, args.description)
    format_output(data, args.format)

def handle_list(args):
    print("Listing indexes...")
    client = get_client()
    data = client.knowledge.list()
    format_output(data, args.format)

def handle_upload(args):
    file_path = args.file
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    file_size = os.path.getsize(file_path)
    print(f"Uploading {file_path} to index {args.index_id}...")
    
    client = get_client()
    
    with open(file_path, 'rb') as f:
        if tqdm:
            pbar = tqdm(total=file_size, desc="Uploading", unit="B", unit_scale=True)
            def chunk_gen():
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    pbar.update(len(chunk))
                    yield chunk
            data = client.knowledge.upload(args.index_id, "", chunk_generator=chunk_gen())
            pbar.close()
        else:
            data = client.knowledge.upload(args.index_id, file_path)
            
    format_output(data, args.format)

def handle_search(args):
    client = get_client()
    data = client.knowledge.search(args.index_id, args.query, args.k)
    format_output(data, args.format)

def handle_retrieve(args):
    client = get_client()
    data = client.knowledge.retrieve(args.document_id)
    format_output(data, args.format)

def handle_delete(args):
    client = get_client()
    data = client.knowledge.delete(args.type, args.id)
    format_output(data, args.format)

def handle_reindex(args):
    client = get_client()
    print(f"Reindexing {args.index_id}...")
    
    for data in client.knowledge.reindex(args.index_id):
        if 'progress' in data and tqdm:
            sys.stdout.write(f"\\rProgress: {data['progress']}%")
            sys.stdout.flush()
        else:
            print(data)
    print("\\nReindexing complete.")

def handle_jobs(args):
    client = get_client()
    data = client.knowledge.jobs()
    format_output(data, args.format)

def handle_status(args):
    client = get_client()
    data = client.knowledge.status(args.job_id)
    format_output(data, args.format)

def add_knowledge_parser(subparsers):
    knowledge_parser = subparsers.add_parser("knowledge", help="Manage knowledge and retrieval platform")
    knowledge_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    knowledge_subparsers = knowledge_parser.add_subparsers(dest="command")

    # create
    create_parser = knowledge_subparsers.add_parser("create", help="Create an index")
    create_parser.add_argument("name", help="Name of the index")
    create_parser.add_argument("--description", "-d", default="", help="Description of the index")

    # list
    list_parser = knowledge_subparsers.add_parser("list", help="List all indexes")

    # upload
    upload_parser = knowledge_subparsers.add_parser("upload", help="Upload a document to an index")
    upload_parser.add_argument("index_id", help="Target index ID")
    upload_parser.add_argument("file", help="Path to file to upload")

    # search
    search_parser = knowledge_subparsers.add_parser("search", help="Search the knowledge base")
    search_parser.add_argument("index_id", help="Index ID to search in")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--k", "-k", type=int, default=5, help="Number of results to return")

    # retrieve
    retrieve_parser = knowledge_subparsers.add_parser("retrieve", help="Retrieve a specific document")
    retrieve_parser.add_argument("document_id", help="Document ID")

    # delete
    delete_parser = knowledge_subparsers.add_parser("delete", help="Delete an index or document")
    delete_parser.add_argument("type", choices=["index", "document"], help="Type of resource to delete")
    delete_parser.add_argument("id", help="Resource ID")

    # reindex
    reindex_parser = knowledge_subparsers.add_parser("reindex", help="Reindex an index")
    reindex_parser.add_argument("index_id", help="Index ID to reindex")

    # jobs
    jobs_parser = knowledge_subparsers.add_parser("jobs", help="List knowledge base background jobs")

    # status
    status_parser = knowledge_subparsers.add_parser("status", help="Get status of a job")
    status_parser.add_argument("job_id", help="Job ID")

def execute_command(args):
    command_handlers = {
        "create": handle_create,
        "list": handle_list,
        "upload": handle_upload,
        "search": handle_search,
        "retrieve": handle_retrieve,
        "delete": handle_delete,
        "reindex": handle_reindex,
        "jobs": handle_jobs,
        "status": handle_status
    }
    
    if args.command in command_handlers:
        try:
            command_handlers[args.command](args)
        except Exception as e:
            print(f"Error communicating with the server: {e}")
            sys.exit(1)
    else:
        print(f"Unknown command: {args.command}")
        
def main():
    parser = argparse.ArgumentParser(prog="llm-engine")
    subparsers = parser.add_subparsers(dest="subcommand")
    add_knowledge_parser(subparsers)
    
    args = parser.parse_args()
    if args.subcommand == "knowledge":
        if args.command:
            execute_command(args)
        else:
            parser.parse_args(['knowledge', '--help'])

if __name__ == "__main__":
    main()
""")

print("SDK part 2 and CLI scripts written successfully.")
