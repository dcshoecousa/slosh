from pathlib import Path    

for item in Path("/home/stan/workspace/slosh").rglob("*.Identifier"):
    item.unlink()