import argparse
import sys
import json
import os
import yaml
from sdk.python.llm_engine.client import LLMEngineClient

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
        print("```json\n" + json.dumps(data, indent=2) + "\n```")

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
            sys.stdout.write(f"\rProgress: {data['progress']}%")
            sys.stdout.flush()
        else:
            print(data)
    print("\nReindexing complete.")

def handle_citations(args):
    client = get_client()
    data = client.knowledge.citations(args.query, args.index_id)
    format_output(data, args.format)

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

    # citations
    citations_parser = knowledge_subparsers.add_parser("citations", help="Get citations for a query")
    citations_parser.add_argument("query", help="Query text")
    citations_parser.add_argument("index_id", help="Target index ID")

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
        "citations": handle_citations,
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
