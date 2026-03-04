# Contributing to CortexGIS

Thank you for your interest in contributing! We welcome bug reports, feature requests, and code contributions.

---

## 🐛 Reporting Issues

### Before submitting an issue:
1. Check existing [issues](https://github.com/yourusername/cortexgis/issues) for duplicates
2. Verify your CortexGIS version: `python -c "import cortexgis; print(cortexgis.__version__)"`
3. Include Python version: `python --version`

### When reporting:
- ✅ Provide clear, descriptive title
- ✅ Describe expected vs. actual behavior
- ✅ Include minimal reproducible example
- ✅ Paste logs/error messages (if applicable)
- ✅ OS, Python version, installed packages

---

## 💡 Feature Requests

Open an issue with `[FEATURE]` prefix:
- Describe the use case
- Suggest implementation approach if possible
- Include references (papers, tools, examples)

---

## 🔧 Code Contributions

### 1. Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/cortexgis.git
cd cortexgis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming**:
- `feature/add-xyz` — new feature
- `fix/issue-123` — bug fix (reference issue #123)
- `docs/update-readme` — documentation
- `test/coverage-xyz` — testing improvements

### 3. Make Changes

#### Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) conventions
- Use type hints for functions
- Keep lines ≤100 characters

#### Example:
```python
def execute_workflow(self, workflow: Dict[str, Any], output_dir: str = ".") -> Dict[str, Any]:
    """
    Execute a complete workflow.
    
    Args:
        workflow: Workflow JSON/dict
        output_dir: Directory to write outputs
    
    Returns:
        Execution summary dict
    """
    # Implementation...
```

#### Format with Black
```bash
black cortexgis/
```

#### Lint with Flake8
```bash
flake8 cortexgis/ --max-line-length=100
```

#### Type check with mypy
```bash
mypy cortexgis/
```

### 4. Write Tests

- Add tests in `tests/` directory
- Follow naming: `test_*.py`
- Achieve ≥80% coverage for new code

```bash
# Run tests
pytest tests/ -v

# Coverage report
pytest tests/ --cov=cortexgis --cov-report=html
```

### 5. Documentation

- Update docstrings (Google or NumPy style)
- Update relevant `.md` files
- Include examples for new features

### 6. Commit & Push

```bash
git add .
git commit -m "feat: add feature description

- Detailed explanation of changes
- Why this change is needed
- Any breaking changes
"

git push origin feature/your-feature-name
```

**Commit message format**:
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `test:` — tests
- `refactor:` — code refactoring
- `perf:` — performance improvement
- `ci:` — CI/CD changes

### 7. Create Pull Request

1. Go to GitHub and create PR from your branch
2. Fill in the PR template
3. Reference related issues: `Closes #123`
4. Describe changes concisely
5. Wait for review

---

## 📝 Contribution Areas

### Add New Tools

1. Create adapter in `executor/tool_adapters.py`:
```python
class MyGeoTool(GeoTool):
    def __init__(self):
        super().__init__("mytool", "Description")
    
    def execute(self, operation: str, params: Dict, **kwargs) -> ToolResult:
        try:
            # Your geospatial operation here
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.SUCCESS,
                output_files=["output.tif"],
                metrics={"area_km2": 1234.5}
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.FAILED,
                output_files=[],
                error_message=str(e)
            )
    
    def supported_operations(self) -> List[str]:
        return ["operation1", "operation2"]
```

2. Register in `executor/executor.py`:
```python
registry.register("mytool", MyGeoTool())
```

3. Test:
```python
registry = ToolRegistry()
tool = registry.get("mytool")
result = tool.execute("operation1", {"param": "value"})
```

### Add Data Sources

1. Extend `DatasetManager` in `data/ingestion.py`:
```python
def ingest_mydatasource(self, aoi_bounds, output_dir="./data"):
    dataset = {
        "id": "my-dataset",
        "name": "My Data Source",
        "source": "https://example.com",
        "status": "fetching"
    }
    # Implement fetching logic
    return dataset
```

2. Test:
```bash
python scripts/demo_data_ingestion.py
```

### Expand RAG Documents

1. Add to `rag/sample_docs.py`:
```python
{
    "id": "new_doc_id",
    "title": "New Geospatial Topic",
    "content": "Detailed documentation...",
    "tags": ["tag1", "tag2"]
}
```

2. Rebuild index:
```bash
python scripts/init_rag_index.py
```

### Add Example Workflows

1. Create JSON in `workflows/`:
```json
{
  "id": "my_workflow",
  "description": "Workflow description",
  "inputs": {...},
  "steps": [...],
  "outputs": [...],
  "cot": [...]
}
```

2. Validate:
```bash
python scripts/validate_workflows.py
```

### Improve Benchmarking

1. Add metrics to `evaluation/metrics.py`
2. Extend `BenchmarkRunner` in `evaluation/benchmark.py`
3. Generate new evaluation reports

---

## 🧪 Testing Checklist

Before submitting PR:

- ✅ All tests pass: `pytest tests/ -v`
- ✅ Code formatted: `black cortexgis/`
- ✅ No lint errors: `flake8 cortexgis/`
- ✅ Type hints OK: `mypy cortexgis/`
- ✅ Coverage ≥80%: `pytest --cov`
- ✅ Docstrings complete
- ✅ No secrets/credentials in code
- ✅ Updated README if needed
- ✅ Commits are logical & well-messaged

---

## 📋 PR Review Process

1. Automated checks run (linting, tests)
2. Maintainers review code & documentation
3. Feedback provided; iterate as needed
4. Upon approval, PR is merged to `main`

---

## ⚖️ Code of Conduct

Be respectful, inclusive, and professional. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) (if applicable).

---

## 📚 Additional Resources

- [Setting up Git fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
- [Creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

**Thank you for contributing to CortexGIS!** 🙏
