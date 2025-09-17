## 📦 Publishing to PyPI

```bash
python3 -m pip install --upgrade build twine
python3 -m build
python3 -m twine upload --repository testpypi dist/*
# or: python3 -m twine upload dist/*
```

Verify on PyPI, then install via `pip install copycat`.