# AI Agent MLOps Demo

A complete MLOps pipeline for an AI customer support agent using Ray, MLflow, and Docker.

## 🎯 Project Goal

Demonstrate a production-ready AI agent with:
- Multi-model orchestration (intent classification, sentiment analysis, response generation)
- Distributed training with Ray
- Experiment tracking with MLflow
- Complete CI/CD pipeline
- Local development environment

## 🔬 About This Demo

**This project focuses on demonstrating MLOps pipeline architecture and infrastructure rather than cutting-edge ML algorithms.**

### Pipeline Focus
- 🏗️ **MLOps Infrastructure** - Complete production pipeline setup
- 🔄 **CI/CD Integration** - Automated training, testing, and deployment
- 📊 **Experiment Tracking** - MLflow integration for model versioning
- 🚀 **Scalable Deployment** - Ray-based distributed processing
- 🐳 **Containerization** - Docker-based development and production environments

### Model Implementation
- 📝 **Simplified Models** - Uses basic classification and sentiment analysis for demonstration
- 🎯 **Production Patterns** - Shows real-world ML deployment patterns
- 🔧 **Extensible Design** - Easy to replace with your own sophisticated models
- 📈 **Monitoring Ready** - Built-in health checks and performance tracking

> **Note**: For production use, replace the demo models with your own trained algorithms. The pipeline infrastructure supports any scikit-learn compatible models or custom implementations.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/fanzi19/ai-agent-mlops-demo.git
cd ai-agent-mlops-demo

# Start local environment
make up

# Generate training data
make data

# Train models
make train

# Deploy AI agent
make deploy

# Run demo
make demo

# Run Web-demo
make web-demo

# Stop Web-demo
make stop-web-demo

# Run Pipeline (data -> train -> deploy)
make pipeline

## 🌐 Access URLs

Web Demo: http://localhost:8080/web_demo.html
Ray Dashboard: http://localhost:8265
Health Check: http://localhost:8000/health
