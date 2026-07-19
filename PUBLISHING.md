# Publishing guide

## GitHub

```bash
cd ~/xg-agent-sdk
git init
git add .
git commit -m "Initial release of xg-agent-sdk 0.1.0"
gh auth login
gh repo create xg-agent-sdk --public --source=. --remote=origin --push
```

## PyPI (recommended: Trusted Publishing)

1. Create project on https://pypi.org (or let first upload create it).
2. Account settings → **Publishing** → **Add a new pending publisher**:
   - PyPI project name: `xg-agent-sdk`
   - Owner: your GitHub username
   - Repository: `xg-agent-sdk`
   - Workflow: `publish.yml`
   - Environment: `pypi`
3. Create a GitHub Release (tag `v0.1.0`) — the `publish.yml` workflow uploads to PyPI.

### Manual upload (API token)

```bash
pip install -e ".[dev]"
python -m build
# Create token at https://pypi.org/manage/account/token/
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...   # your API token
twine upload dist/*
```

## Install after publish

```bash
pip install xg-agent-sdk
```

```python
from xg_agent_sdk import query, XGAgentOptions
```
