
# Smart Contract Audit Bot

A comprehensive, production-ready AI-powered smart contract security analysis and auditing system built with FastAPI, LangChain, Pinecone, and Next.js.

## 🚀 Features

### Core Capabilities
- **Smart Contract Ingestion**: Upload and process Solidity contracts with intelligent chunking
- **RAG-Powered Analysis**: Retrieval-Augmented Generation for context-aware security analysis
- **Comprehensive Security Auditing**: Detect vulnerabilities, gas optimization opportunities, and best practices
- **Interactive Chat Interface**: Natural language interaction with the audit bot
- **Vulnerability Explanations**: Detailed explanations of security vulnerabilities
- **Improvement Suggestions**: Specific recommendations for code enhancement

### Security Features
- **Input Validation**: Comprehensive validation of all inputs
- **Rate Limiting**: Protection against abuse
- **File Type Validation**: Only allow safe file types
- **Error Handling**: Robust error handling and logging
- **CORS Protection**: Secure cross-origin resource sharing

### Technical Features
- **Vector Database**: Pinecone for efficient similarity search
- **Modern Frontend**: Next.js with TypeScript and Tailwind CSS
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Async Processing**: Non-blocking operations for better performance
- **Modular Architecture**: Clean separation of concerns

## 🏗️ Architecture

```
smart-contract-audit-bot/
├── app/                    # Backend application
│   ├── config.py          # Configuration management
│   ├── ingestion_sol.py   # Contract ingestion and processing
│   ├── chatbot_sol.py     # RAG-powered chatbot logic
│   └── main.py            # FastAPI application
├── contracts/             # Sample contracts for testing
├── audit-bot-frontend/    # Next.js frontend
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- OpenAI API key
- Pinecone API key

### Backend Setup

1. **Clone and setup environment**:
```bash
cd smart-contract-audit-bot
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start the backend server**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```



### Frontend Setup

The UI is served via FastAPI using a Jinja2 template (`app/frontend/index.html`). No Node.js setup is required unless using the optional Next.js version.


2. **Start the development server**:
```bash
npm run dev
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /upload` - Upload smart contract files
- `POST /chat` - Chat with the audit bot
- `POST /analyze` - Comprehensive security analysis
- `POST /improvements` - Get improvement suggestions
- `POST /explain-vulnerability` - Explain specific vulnerabilities
- `GET /search` - Search contract database
- `GET /stats` - System statistics

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `PINECONE_INDEX_NAME` | Pinecone index name | smart-contract-audit |
| `OPENAI_MODEL` | OpenAI model to use | gpt-4 |
| `MAX_TOKENS` | Maximum tokens per response | 2000 |
| `CHUNK_SIZE` | Text chunk size for processing | 1000 |
| `TOP_K_RESULTS` | Number of search results | 5 |

### Security Settings

- **File Upload**: 10MB max size, .sol and .txt files only
- **Rate Limiting**: 100 requests per hour per IP
- **Input Validation**: All inputs validated and sanitized
- **CORS**: Configured for localhost development

## 🧪 Usage Examples

### Upload a Contract
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@contract.sol"
```
**LangSmith or RAGAS Integration**: For LLM tracing or response evaluation
- **Frontend Upload Progress Bar**
- **Chat History Persistence**
- **OAuth or Token-Based Access**
### Chat with the Bot
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main security vulnerabilities in smart contracts?"}'
```

### Analyze a Contract
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"contract_content": "pragma solidity ^0.8.0; contract Example { ... }"}'
```

## 🔍 Security Analysis Features

### Vulnerability Detection
- **Reentrancy**: Detection of reentrancy vulnerabilities
- **Access Control**: Analysis of permission systems
- **Integer Overflow/Underflow**: Arithmetic safety checks
- **External Calls**: Safe external interaction patterns
- **Gas Optimization**: Efficiency improvements
- **Best Practices**: Solidity coding standards

### Analysis Categories
- **CRITICAL**: Immediate security risks
- **HIGH**: Significant vulnerabilities
- **MEDIUM**: Important improvements
- **LOW**: Minor optimizations
- **INFORMATIONAL**: Best practice suggestions

## 🧪 Testing

### Run Backend Tests
```bash
pytest tests/ -v
```

### Test Contract Upload
```bash
# Upload the sample contract
curl -X POST "http://localhost:8000/upload" \
  -F "file=@contracts/AuditReportRegistry.sol"
```

## 🚀 Deployment
## 🌐 Demo
Screenshots: [See UI Preview](docs\screenshots.png)
### Production Considerations

1. **Environment Variables**: Set production API keys
2. **Database**: Configure production Pinecone index
3. **Security**: Enable HTTPS, update CORS origins
4. **Monitoring**: Add logging and monitoring
5. **Scaling**: Consider load balancing for high traffic

### Docker Deployment
```bash
# Build and run with Docker
docker build -t audit-bot .
docker run -p 8000:8000 --env-file .env audit-bot
```

## 📈 Performance

- **Vector Search**: Sub-second similarity search with Pinecone
- **Async Processing**: Non-blocking file uploads and analysis
- **Caching**: Intelligent caching of embeddings and results
- **Rate Limiting**: Protection against abuse

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint
- **Issues**: Report bugs via GitHub issues
- **API Help**: Use the interactive docs at `/docs`

## 🔮 Roadmap

- [ ] Advanced vulnerability detection
- [ ] Integration with popular audit tools
- [ ] Multi-language support
- [ ] Real-time collaboration features
- [ ] Automated report generation
- [ ] Blockchain integration for report storage
