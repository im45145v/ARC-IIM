# Contributing to Alumni Management System

Thank you for your interest in contributing to the Alumni Management System! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Documentation](#documentation)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ARC-IIM.git
   cd ARC-IIM
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/im45145v/ARC-IIM.git
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for local database)
- Git

### Installation

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Install development dependencies**:
   ```bash
   pip install pytest pytest-asyncio hypothesis pandas openpyxl
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your test credentials
   ```

5. **Start local database**:
   ```bash
   docker-compose up -d
   ```

6. **Initialize database**:
   ```bash
   python -c "from alumni_system.database.init_db import init_database; init_database()"
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_account_rotation.py

# Run with coverage
pytest --cov=alumni_system

# Run property-based tests with more iterations
pytest tests/test_*_properties.py -v
```

## Project Architecture

The project follows a modular architecture:

```
alumni_system/
├── chatbot/          # NLP query processing
├── database/         # Database models and operations
├── frontend/         # Streamlit web interface
├── scraper/          # LinkedIn scraping with multi-account support
├── storage/          # Cloud storage (B2) integration
└── utils/            # Shared utilities
```

### Key Design Principles

1. **Modularity**: Each component is independently testable
2. **Resilience**: Failures in one component don't cascade
3. **Scalability**: Multi-account rotation supports large-scale operations
4. **Security**: All credentials externalized to environment variables

## Making Changes

### Types of Contributions

- **Bug fixes**: Fix issues in existing functionality
- **Features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code
- **Refactoring**: Improve code structure without changing behavior

### Before You Start

1. **Check existing issues**: Look for related issues or discussions
2. **Create an issue**: Describe what you plan to work on
3. **Get feedback**: Wait for maintainer feedback before starting large changes
4. **Keep it focused**: One feature/fix per pull request

### Development Workflow

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**:
   - Write code following coding standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**:
   ```bash
   pytest
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Testing

### Test Requirements

- All new features must include tests
- Bug fixes should include regression tests
- Aim for high test coverage (>80%)
- Tests should be fast and reliable

### Test Types

1. **Unit Tests**: Test individual functions/classes
   ```python
   def test_account_rotation():
       manager = AccountRotationManager(accounts, limit=80)
       account = manager.get_next_account()
       assert account is not None
   ```

2. **Property-Based Tests**: Test properties across many inputs
   ```python
   @given(st.integers(min_value=1, max_value=100))
   def test_pagination_math(total_records):
       # Test pagination calculation for any number of records
       ...
   ```

3. **Integration Tests**: Test component interactions
   ```python
   def test_import_and_queue_workflow(db_session):
       # Test complete import → queue → scrape workflow
       ...
   ```

### Running Specific Tests

```bash
# Run unit tests only
pytest tests/test_account_rotation.py

# Run property-based tests
pytest tests/test_*_properties.py

# Run integration tests
pytest tests/test_*_integration.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=alumni_system --cov-report=html
```

## Submitting Changes

### Pull Request Process

1. **Update documentation**: Ensure README and docstrings are updated
2. **Add tests**: Include tests for new functionality
3. **Run tests**: Ensure all tests pass
4. **Update CHANGELOG**: Add entry describing your changes
5. **Create pull request**: Use descriptive title and description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] All tests pass
- [ ] Added new tests for changes
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages follow convention
```

### Commit Message Convention

Use conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples**:
```
feat(scraper): add multi-account rotation support
fix(database): resolve cascade deletion issue
docs(readme): update installation instructions
test(import): add property tests for bulk import
```

## Coding Standards

### Python Style Guide

Follow PEP 8 with these specifics:

- **Line length**: 100 characters max
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Group stdlib, third-party, local (separated by blank lines)
- **Docstrings**: Use Google style docstrings
- **Type hints**: Use type hints for function signatures

### Code Quality

```bash
# Format code with black
black alumni_system/

# Check style with flake8
flake8 alumni_system/

# Type checking with mypy
mypy alumni_system/
```

### Example Code Style

```python
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from alumni_system.database.models import Alumni


def get_alumni_by_batch(
    db: Session,
    batch: str,
    limit: int = 100
) -> List[Alumni]:
    """
    Retrieve alumni records for a specific batch.
    
    Args:
        db: Database session
        batch: Graduation batch/year
        limit: Maximum number of records to return
    
    Returns:
        List of Alumni objects matching the batch
    
    Example:
        >>> alumni = get_alumni_by_batch(db, "2020", limit=50)
        >>> len(alumni)
        50
    """
    return db.query(Alumni).filter(
        Alumni.batch == batch
    ).limit(limit).all()
```

### Naming Conventions

- **Functions/methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`
- **Module names**: `lowercase` or `snake_case`

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed, explaining behavior,
    edge cases, and important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is negative
    
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

### README Updates

When adding features:
1. Update feature list
2. Add usage examples
3. Update configuration section if needed
4. Add troubleshooting entries if applicable

### Code Comments

- Use comments to explain **why**, not **what**
- Keep comments up-to-date with code changes
- Avoid obvious comments
- Use TODO comments for future improvements

```python
# Good: Explains why
# Use exponential backoff to avoid overwhelming LinkedIn servers
await asyncio.sleep(delay * (2 ** attempt))

# Bad: States the obvious
# Increment counter by 1
counter += 1
```

## Areas for Contribution

### High Priority

- [ ] Improve error handling and recovery
- [ ] Add more comprehensive logging
- [ ] Optimize database queries
- [ ] Enhance security features
- [ ] Improve test coverage

### Feature Ideas

- [ ] Export to additional formats (JSON, PDF reports)
- [ ] Advanced analytics and visualizations
- [ ] Email notifications for scraping completion
- [ ] Webhook support for integrations
- [ ] API endpoints for external access
- [ ] Mobile-responsive web interface
- [ ] Advanced search with filters
- [ ] Batch operations in admin panel

### Documentation Needs

- [ ] Video tutorials
- [ ] Architecture diagrams
- [ ] API reference documentation
- [ ] Deployment guides (AWS, Azure, GCP)
- [ ] Performance tuning guide
- [ ] Security best practices guide

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Create an issue with reproduction steps
- **Features**: Open an issue to discuss before implementing
- **Security**: Email maintainers directly (don't open public issue)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! 🎉
