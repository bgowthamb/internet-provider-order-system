# AI & Automation Portfolio

Two independent Python projects showcasing applied machine learning, business automation, document retrieval and automated testing.

| Project | Focus | Run guide |
| --- | --- | --- |
| ISP Order System | Flask, SQLAlchemy, customer analytics, pricing and ML | [Application guide](internet-provider-order-system/README.md) |
| Local Knowledge Assistant | Local document retrieval, optional offline LLM, citations, desktop UI | [Windows setup](local-document-assistant/README.md) |

## Engineering practices

- Application factory and isolated in-memory database tests
- Read-only local document search and source excerpts
- GitHub Actions test checks on pushes and pull requests
- Private data, environment files and generated databases excluded from Git

## Roadmap

1. Complete secondary ISP screens and expand end-to-end tests.
2. Add offline OCR and semantic retrieval to the knowledge assistant.
3. Evaluate retrieval quality with synthetic examples and add reproducible release packaging.

These are demonstration applications, not production-ready or validated regulated systems. Never commit real customer records, personal identity documents, credentials or employer materials.
