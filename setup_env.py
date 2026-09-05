"""Create the local env file the compose services read (idempotent)."""

from pathlib import Path

ENV_FILE = Path(".envs/.django")
DEFAULTS = """USE_DOCKER=yes
IPYTHONDIR=/app/.ipython
"""

if ENV_FILE.is_file():
    print(f"{ENV_FILE} already exists.")
else:
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    ENV_FILE.write_text(DEFAULTS)
    print(f"{ENV_FILE} created.")
