# AI Agent MLOps Demo

A complete MLOps pipeline for an AI customer support agent using Ray, MLflow, and Docker.

## 🎯 Project Goal

Demonstrate a production-ready AI agent with:
- Multi-model orchestration (intent classification, sentiment analysis, response generation)
- Distributed training with Ray
- Experiment tracking with MLflow
- Complete CI/CD pipeline
- Local development environment

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
