# Contributing to ohada-financial-extractor

Thank you for your interest in contributing!  
We welcome improvements, bug fixes, documentation updates, and new ideas that help strengthen the OHADA financial ecosystem.

This document explains how to contribute effectively and responsibly.

---

## 🧱 How to Contribute

### 1. Fork the repository
Click **Fork** on GitHub and clone your fork locally:

```bash
git clone https://github.com/<your-username>/ohada-extractor.git
cd ohada-extractor
````
### 2. Create a feature branch
```bash
git checkout -b feature/my-improvement
```
### 3. Install dependencies
We recommend using a virtual environment:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```
### 4. Make your changes
Follow the existing code style and structure.
If you add new modules, include docstrings and minimal examples.

### 5. Run tests (if applicable)
```bash
pytest
```
### 6. Commit your changes
Use clear, descriptive commit messages:

```bash
git commit -m "Add metadata extraction for new OHADA field"
```
### 7. Push and open a Pull Request
```bash
git push origin feature/my-improvement
```
Then open a PR on GitHub with:

- a clear description of the change
- motivation and context
- screenshots or examples if relevant

---
📚 **Code Style**
- Follow PEP 8 for Python code.

- Use type hints where possible.

- Keep functions small and focused.

- Prefer clarity over cleverness.

🧪 **Tests**

If you add new functionality, please include tests under:

```Code
tests/
```
We use pytest.

---
📝 **Documentation**

If your contribution affects user-facing behavior, update:

- README.md

- any relevant files under docs/

---
🔐 **Security**

Do not report security issues publicly.
Follow the instructions in **SECURITY.md**.

🤝 **Thank You**

Your contributions help strengthen financial analysis tools across the OHADA region.
We appreciate your time, expertise, and collaboration.