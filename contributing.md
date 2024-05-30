# Contributing to Sales Automation Tool

First off, thank you for considering contributing to the Sales Automation Tool! 🎉 Your help is appreciated, and every bit of contribution counts. Below are some guidelines to get you started.

## Table of Contents

1. [How Can I Contribute?](#how-can-i-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Suggesting Enhancements](#suggesting-enhancements)
   - [Submitting Pull Requests](#submitting-pull-requests)
2. [Code of Conduct](#code-of-conduct)
3. [Style Guides](#style-guides)
   - [Git Commit Messages](#git-commit-messages)
   - [Python Style Guide](#python-style-guide)
4. [Getting Started](#getting-started)
5. [Additional Resources](#additional-resources)

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please report it by opening an issue. Before doing so, please check if the issue already exists. When reporting a bug, please include:

- A clear and descriptive title.
- A detailed description of the problem.
- Steps to reproduce the issue.
- Any relevant logs or screenshots.

### Suggesting Enhancements

Enhancements and new features are always welcome! To suggest an enhancement, please open an issue and provide:

- A clear and descriptive title.
- A detailed description of the proposed enhancement.
- Any relevant examples or designs.

### Submitting Pull Requests

1. **Fork the repository**: Click the "Fork" button at the top right of the repository page.
2. **Clone your fork**:
   ```sh
   git clone https://github.com/KrishnaKumarSoni/bulk-cold-mailer.git
   ```
3. **Create a new branch**:
   ```sh
   git checkout -b feature-branch-name
   ```
4. **Make your changes**: Ensure your code follows the style guides below.
5. **Commit your changes**:
   ```sh
   git commit -m "Brief description of your changes"
   ```
6. **Push to your fork**:
   ```sh
   git push origin feature-branch-name
   ```
7. **Open a Pull Request**: Go to the original repository and open a pull request. Provide a detailed description of your changes and any related issue numbers.


## Style Guides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature").
- Use the imperative mood ("Move button left..." not "Moves button left...").
- Limit the first line to 72 characters or less.
- Reference issues and pull requests liberally.

### Python Style Guide

- Follow [PEP 8](https://pep8.org/), the Python style guide.
- Use meaningful variable and function names.
- Write docstrings for all public classes and functions.
- Use type hints for function signatures.

## Getting Started

### Setting Up Your Development Environment

1. **Clone the repository**:
   ```sh
   git clone https://github.com/KrishnaKumarSoni/bulk-cold-mailer.git
   cd sales-automation-tool
   ```
2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
3. **Set up Google Cloud credentials**:
   - Follow the instructions in the [README](README.md) to set up your `credentials.json` file.
4. **Run the application**:
   ```sh
   streamlit run app.py --server.port=8501
   ```

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [OpenAI API Documentation](https://beta.openai.com/docs/)

Thank you for contributing! 🙌
