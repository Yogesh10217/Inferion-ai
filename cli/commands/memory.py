"""
CLI Commands for Enterprise Memory Subsystem
"""

import argparse
import sys
import json
import os
import yaml

from sdk.python.llm_engine.client import LLMEngineClient

BASE_URL = os.environ.get("MEMORY_API_URL", "http://localhost:8000")


def get_client():
    return LLMEngineClient(base_url=BASE_URL)


def format_output(data, fmt):
    if fmt == "json":
        print(json.dumps(data, indent=2))
    elif fmt == "yaml":
        print(yaml.dump(data))
    elif fmt == "table":
        if isinstance(data, list):
            for item in data:
                print("---")
                if isinstance(item, dict):
                    for k, v in item.items():
                        print(f"{k}: {v}")
                else:
                    print(item)
        elif isinstance(data, dict):
            for k, v in data.items():
                print(f"{k}: {v}")
        else:
            print(data)
    elif fmt == "markdown":
        print("```json\n" + json.dumps(data, indent=2) + "\n```")


def handle_create(args):
    print(f"Creating memory entry...")
    client = get_client()
    data = client.memory.create(content=args.content, context_hint=args.context_hint, user_id=args.user_id)
    format_output(data, args.format)


def handle_list(args):
    print("Listing memory entries...")
    client = get_client()
    data = client.memory.list(memory_type=args.type)
    format_output(data, args.format)


def handle_get(args):
    print(f"Getting memory '{args.id}'...")
    client = get_client()
    data = client.memory.get(args.id)
    format_output(data, args.format)


def handle_search(args):
    print(f"Searching memory for '{args.query}'...")
    client = get_client()
    data = client.memory.search(args.query, top_k=args.top_k)
    format_output(data, args.format)


def handle_compress(args):
    print(f"Compressing session '{args.session_id}'...")
    client = get_client()
    data = client.memory.compress(args.session_id)
    format_output(data, args.format)


def handle_summarize(args):
    print("Summarizing text...")
    client = get_client()
    data = client.memory.summarize(args.text)
    format_output(data, args.format)


def handle_archive(args):
    print(f"Archiving memory '{args.id}'...")
    client = get_client()
    data = client.memory.archive(args.id)
    format_output(data, args.format)


def handle_profile(args):
    print(f"Fetching profile for user '{args.user_id}'...")
    client = get_client()
    data = client.memory.get_profile(args.user_id)
    format_output(data, args.format)


def handle_analytics(args):
    print("Fetching memory analytics...")
    client = get_client()
    data = client.memory.analytics()
    format_output(data, args.format)


def add_memory_parser(subparsers):
    mem_parser = subparsers.add_parser("memory", help="Manage enterprise contextual memory")
    mem_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    mem_subparsers = mem_parser.add_subparsers(dest="command")

    # create
    create_p = mem_subparsers.add_parser("create", help="Create a memory record")
    create_p.add_argument("content", help="Memory content text")
    create_p.add_argument("--context-hint", help="Context hint")
    create_p.add_argument("--user-id", help="User ID")

    # list
    list_p = mem_subparsers.add_parser("list", help="List memory records")
    list_p.add_argument("--type", help="Filter by memory_type")

    # get
    get_p = mem_subparsers.add_parser("get", help="Get a memory record by ID")
    get_p.add_argument("id", help="Memory ID")

    # search
    search_p = mem_subparsers.add_parser("search", help="Search memory records")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--top-k", type=int, default=10, help="Top K results")

    # compress
    compress_p = mem_subparsers.add_parser("compress", help="Compress conversation memory")
    compress_p.add_argument("session_id", help="Session ID")

    # summarize
    sum_p = mem_subparsers.add_parser("summarize", help="Summarize text content")
    sum_p.add_argument("text", help="Text to summarize")

    # archive
    arc_p = mem_subparsers.add_parser("archive", help="Archive a memory record")
    arc_p.add_argument("id", help="Memory ID")

    # profile
    prof_p = mem_subparsers.add_parser("profile", help="Get user profile memory")
    prof_p.add_argument("--user-id", default="default_user", help="User ID")

    # analytics
    mem_subparsers.add_parser("analytics", help="Get memory analytics")
