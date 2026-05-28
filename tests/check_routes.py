"""Check registered routes."""
from app import create_app

app = create_app()
print("Registered routes:")
for rule in app.url_map.iter_rules():
    if not rule.rule.startswith("/static"):
        methods = rule.methods - {"HEAD", "OPTIONS"}
        print(f"  {rule.rule}  [{', '.join(methods)}]")
