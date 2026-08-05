import os

PROJECT_ROOT = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine"

# 1. Update Python SDK
py_path = os.path.join(PROJECT_ROOT, "sdk/python/llm_engine/knowledge.py")
if os.path.exists(py_path):
    with open(py_path, "r") as f:
        py_code = f.read()
    
    if "def citations(" not in py_code:
        # insert into KnowledgeClient
        citations_sync = """
    def citations(self, query: str, index_id: str) -> dict:
        res = self._client.post("/v1/knowledge/citations", json={"query": query, "index_id": index_id})
        res.raise_for_status()
        return res.json()
"""
        py_code = py_code.replace("def jobs(self)", citations_sync.strip() + "\n\n    def jobs(self)")

        # insert into AsyncKnowledgeClient
        citations_async = """
    async def citations(self, query: str, index_id: str) -> dict:
        res = await self._client.post("/v1/knowledge/citations", json={"query": query, "index_id": index_id})
        res.raise_for_status()
        return res.json()
"""
        py_code = py_code.replace("async def jobs(self)", citations_async.strip() + "\n\n    async def jobs(self)")
        
        with open(py_path, "w") as f:
            f.write(py_code)


# 2. Update TS SDK
ts_path = os.path.join(PROJECT_ROOT, "sdk/typescript/src/knowledge.ts")
if os.path.exists(ts_path):
    with open(ts_path, "r") as f:
        ts_code = f.read()
    
    if "async citations(" not in ts_code:
        citations_ts = """
  async citations(query: string, indexId: string) {
    return this.request('POST', '/v1/knowledge/citations', { query, index_id: indexId });
  }
"""
        ts_code = ts_code.replace("async jobs() {", citations_ts.strip() + "\n\n  async jobs() {")
        
        with open(ts_path, "w") as f:
            f.write(ts_code)


# 3. Update Go SDK
go_path = os.path.join(PROJECT_ROOT, "sdk/go/knowledge.go")
if os.path.exists(go_path):
    with open(go_path, "r") as f:
        go_code = f.read()
    
    if "func (k *KnowledgeClient) Citations" not in go_code:
        citations_go = """
func (k *KnowledgeClient) Citations(ctx context.Context, query, indexID string) (map[string]interface{}, error) {
	res, err := k.doReq(ctx, "POST", "/v1/knowledge/citations", map[string]string{"query": query, "index_id": indexID})
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	var out map[string]interface{}
	json.NewDecoder(res.Body).Decode(&out)
	return out, nil
}
"""
        go_code += "\n" + citations_go
        
        with open(go_path, "w") as f:
            f.write(go_code)


# 4. Update CLI
cli_path = os.path.join(PROJECT_ROOT, "cli/knowledge.py")
if os.path.exists(cli_path):
    with open(cli_path, "r") as f:
        cli_code = f.read()
    
    if "def handle_citations(" not in cli_code:
        handle_citations = """
def handle_citations(args):
    client = get_client()
    data = client.knowledge.citations(args.query, args.index_id)
    format_output(data, args.format)
"""
        cli_code = cli_code.replace("def handle_jobs(args):", handle_citations.strip() + "\n\ndef handle_jobs(args):")
        
        parser_citations = """
    # citations
    citations_parser = knowledge_subparsers.add_parser("citations", help="Get citations for a query")
    citations_parser.add_argument("query", help="Query text")
    citations_parser.add_argument("index_id", help="Target index ID")
"""
        cli_code = cli_code.replace("# jobs", parser_citations.strip() + "\n\n    # jobs")
        
        cli_code = cli_code.replace('"reindex": handle_reindex,', '"reindex": handle_reindex,\n        "citations": handle_citations,')
        
        with open(cli_path, "w") as f:
            f.write(cli_code)

print("Patching citations complete.")
