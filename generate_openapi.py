import os
import json

# Setup PYTHONPATH manually by modifying sys.path if needed
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def generate_openapi_spec():
    out_dir = "sdk/shared"
    os.makedirs(out_dir, exist_ok=True)
    
    spec = app.openapi()
    with open(os.path.join(out_dir, "openapi.json"), "w") as f:
        json.dump(spec, f, indent=2)

if __name__ == "__main__":
    generate_openapi_spec()
    print("OpenAPI spec generated.")
