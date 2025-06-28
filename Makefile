# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

.PHONY: help up down status logs shell data train deploy demo web-demo test lint clean setup demo-help

help: ## Show this help message
	@echo "$(BLUE)🤖 Customer Support AI Agent - MLOps Demo$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-15s$(NC) %s\n", $$1, $$2}'

# Docker Management
up: ## Start all services
	@echo "$(BLUE)🚀 Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Services started$(NC)"

down: ## Stop all services
	@echo "$(BLUE)🛑 Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Services stopped$(NC)"

status: ## Check service status
	@echo "$(BLUE)📊 Service Status:$(NC)"
	@docker-compose ps

logs: ## View logs
	@echo "$(BLUE)📜 Viewing logs...$(NC)"
	docker-compose logs -f

shell: ## Access development container
	@echo "$(BLUE)🐚 Opening shell in development container...$(NC)"
	docker exec -it ml-dev bash

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

# Demo Commands
demo: deploy ## Run interactive CLI demo
	@echo "$(BLUE)💬 Running interactive CLI demo...$(NC)"
	docker exec -it ray-head python scripts/demo.py || echo "$(RED)❌ Demo failed$(NC)"

web-demo: deploy ## Start web interface demo with CORS support
	@echo "$(BLUE)🌐 Starting web demo server...$(NC)"
	@echo "$(BLUE)🌍 Starting CORS proxy...$(NC)"
	@docker exec ray-head pkill -f cors_proxy || echo "$(YELLOW)⚠️  CORS proxy not running$(NC)"
	@docker exec -d ray-head python scripts/cors_proxy.py
	@sleep 2
	@docker exec -d ray-head python -m http.server 8080 --directory /workspace/scripts
	@sleep 2
	@echo "$(GREEN)✅ Web demo server started with CORS support$(NC)"
	@echo "$(GREEN)🔗 Open: http://localhost:8080/web_demo.html$(NC)"
	@echo "$(YELLOW)⚠️  Make sure ports 8080 and 8001 are available$(NC)"
	@echo "$(BLUE)📖 To stop: make stop-web-demo$(NC)"

demo-help: ## Show demo usage examples
	@echo "$(BLUE)📖 Demo Commands:$(NC)"
	@echo "  $(GREEN)make demo$(NC)      - Interactive CLI demo with test scenarios"
	@echo "  $(GREEN)make web-demo$(NC)   - Beautiful web interface demo"
	@echo "  $(GREEN)make deploy$(NC)     - Deploy AI agent (runs automatically with demos)"
	@echo ""
	@echo "$(BLUE)🎯 Demo Features:$(NC)"
	@echo "  • Real-time customer satisfaction predictions"
	@echo "  • Multiple issue type scenarios"
	@echo "  • Interactive message testing"
	@echo "  • Response time metrics"
	@echo "  • Confidence scoring"

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

# Pipeline Commands
pipeline: ## Run complete ML pipeline (data -> train -> deploy -> demo)
	@echo "$(BLUE)🔄 Running complete ML pipeline...$(NC)"
	@make data
	@make train  
	@make deploy
	@echo "$(GREEN)🎉 Pipeline complete! Try 'make demo' or 'make web-demo'$(NC)"

quick-demo: ## Quick demo without full pipeline (uses existing models)
	@echo "$(BLUE)⚡ Quick demo with existing models...$(NC)"
	@make deploy
	@make demo

# Advanced Commands
stop-web-demo: ## Stop web demo server and CORS proxy
	@echo "$(BLUE)🛑 Stopping web demo server...$(NC)"
	@docker exec ray-head pkill -f 'http.server 8080' || echo "$(YELLOW)⚠️  Web server not running$(NC)"
	@docker exec ray-head pkill -f cors_proxy || echo "$(YELLOW)⚠️  CORS proxy not running$(NC)"
	@echo "$(GREEN)✅ Web demo and CORS proxy stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)🔄 Restarting services...$(NC)"
	@make down
	@make up
	@echo "$(GREEN)✅ Services restarted$(NC)"

