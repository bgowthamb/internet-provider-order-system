# Contributing to Internet Provider Order Entry System

Thank you for your interest in contributing to the Internet Provider Order Entry System! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- pip

### Setup Development Environment
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/internet-provider-order-system.git
   cd internet-provider-order-system
   ```
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up the database:
   ```bash
   python init_db.py
   ```

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused

### Testing
- Write tests for new features
- Ensure all tests pass before submitting
- Run tests with: `python -m pytest tests/`

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Keep the first line under 50 characters
- Add more details in the body if needed

## 🔧 Making Changes

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Write your code following the guidelines above
- Add tests for new functionality
- Update documentation if needed

### 3. Test Your Changes
```bash
# Run the application
python run.py

# Run tests
python -m pytest tests/

# Check code style
flake8 app/
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "Add new feature: description"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Screenshots if UI changes
- Test results
- Any breaking changes

## 🐛 Reporting Bugs

### Before Reporting
1. Check existing issues
2. Try to reproduce the bug
3. Check if it's a known issue

### Bug Report Template
```
**Bug Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: [e.g., macOS, Windows, Linux]
- Python Version: [e.g., 3.8, 3.9]
- Browser: [if applicable]

**Additional Information:**
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template
```
**Feature Description:**
Brief description of the feature

**Use Case:**
Why this feature is needed

**Proposed Solution:**
How you think it should work

**Additional Information:**
Any other relevant information
```

## 📚 Documentation

### Updating Documentation
- Keep README.md up to date
- Update API documentation for new endpoints
- Add inline comments for complex code
- Update setup instructions if needed

## 🔒 Security

### Reporting Security Issues
- **DO NOT** create a public issue for security vulnerabilities
- Email security issues to: [your-email@example.com]
- Include detailed information about the vulnerability
- Allow time for response before public disclosure

## 🏷️ Release Process

### Versioning
We use [Semantic Versioning](https://semver.org/):
- MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number updated
- [ ] Changelog updated
- [ ] Release notes prepared

## 🤝 Code of Conduct

### Our Standards
- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative and constructive
- Focus on what is best for the community

### Enforcement
- Unacceptable behavior will not be tolerated
- Violations may result in temporary or permanent ban
- Report violations to maintainers

## �� Getting Help

### Questions and Support
- Check existing issues and discussions
- Create a new issue for questions
- Join our community chat (if available)

### Contact Maintainers
- GitHub Issues: For bugs and feature requests
- Email: [your-email@example.com] for private matters

## 🙏 Acknowledgments

Thank you to all contributors who have helped make this project better!

---

**Note:** This is a living document. Feel free to suggest improvements or clarifications through issues or pull requests.
