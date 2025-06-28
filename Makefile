# Makefile for AI Agent MLOps Demo
.PHONY: help up down logs status shell data train deploy demo test lint clean

# Colors for pretty output
BLUE=\033[36m
GREEN=\033[32m
YELLOW=\033[33m
RED=\033[31m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)AI Agent MLOps Demo - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

# Docker Environment Management
up: ## Start all services
	@echo "$(BLUE)🚀 Starting AI Agent MLOps environment...$(NC)"
	docker-compose up -d
	@echo "$(YELLOW)⏳ Waiting for services to start...$(NC)"
	@sleep 30
	@make status

down: ## Stop all services
	@echo "$(BLUE)🛑 Stopping all services...$(NC)"
	docker-compose down

restart: down up ## Restart all services

logs: ## Show logs from all services
	docker-compose logs -f

status: ## Check status of all services
	@echo "$(BLUE)📊 Service Status:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)🌐 Available URLs:$(NC)"
	@echo "$(GREEN)Ray Dashboard:$(NC)    http://localhost:8265"
	@echo "$(GREEN)MLflow UI:$(NC)        http://localhost:5001"
	@echo "$(GREEN)Grafana:$(NC)          http://localhost:3000"
	@echo "$(GREEN)Prometheus:$(NC)       http://localhost:9090"

# Development
shell: ## Enter development container
	@echo "$(BLUE)🐚 Entering development container...$(NC)"
	docker exec -it ml-dev bash || echo "$(RED)❌ Development container not running. Run 'make up' first.$(NC)"

ray-shell: ## Enter Ray head container
	@echo "$(BLUE)⚡ Entering Ray head container...$(NC)"
	docker exec -it ray-head bash || echo "$(RED)❌ Ray container not running. Run 'make up' first.$(NC)"

# Data and Training
data: ## Generate training data
	@echo "$(BLUE)📊 Generating training data...$(NC)"
	docker exec ml-dev python scripts/setup_data.py || echo "$(RED)❌ Failed to generate data$(NC)"

train: ## Run training pipeline
	@echo "$(BLUE)🎯 Starting model training...$(NC)"
	docker exec ray-head python src/training/training_pipeline.py || echo "$(RED)❌ Training failed$(NC)"

# Deployment
deploy: ## Deploy AI agent
	@echo "$(BLUE)🚀 Deploying AI agent...$(NC)"
	docker exec ray-head python scripts/deploy_local.py || echo "$(RED)❌ Deployment failed$(NC)"

demo: ## Run demo conversation
	@echo "$(BLUE)💬 Running demo conversations...$(NC)"
	docker exec ml-dev python scripts/run_demo.py || echo "$(RED)❌ Demo failed$(NC)"

# Testing and Quality
test: ## Run tests
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@echo "$(YELLOW)⚠️  Tests not implemented yet$(NC)"

lint: ## Check code quality
	@echo "$(BLUE)🔍 Checking code quality...$(NC)"
	@echo "$(YELLOW)⚠️  Linting not implemented yet$(NC)"

# Utilities
clean: ## Clean up containers and volumes
	@echo "$(BLUE)🧹 Cleaning up...$(NC)"
	docker-compose down -v
	docker system prune -f
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

setup: ## First-time setup
	@echo "$(BLUE)⚙️  Running first-time setup...$(NC)"
	@make up
	@sleep 10
	@make data
	@echo "$(GREEN)✅ Setup complete! Run 'make status' to see available services$(NC)"
