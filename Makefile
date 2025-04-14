# Root Makefile for starting frontend and backend

.PHONY: start start-frontend start-backend build-frontend install-frontend install-backend clean

# === Install Dependencies ===

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

# === Start Frontend and Backend ===

start: start-backend start-frontend

start-backend:
	cd backend && python main.py

start-frontend:
	cd frontend && npm start

# === Build Frontend for Production ===

build-frontend:
	cd frontend && npm run build

# === Clean up ===

clean:
	rm -rf backend/__pycache__ frontend/node_modules frontend/build
