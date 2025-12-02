.PHONY: help build install clean test dev

BINARY_NAME=chronos
BUILD_DIR=./cmd/chronos
INSTALL_DIR=$(HOME)/.local/bin

help:
	@echo "Chronos - Task Runner with Live TUI"
	@echo ""
	@echo "Usage:"
	@echo "  make build     Build the chronos binary"
	@echo "  make install   Build and install to ~/.local/bin"
	@echo "  make clean     Remove build artifacts"
	@echo "  make test      Run tests"
	@echo "  make dev       Build with race detector"
	@echo ""

build:
	@echo "Building $(BINARY_NAME)..."
	go build -o $(BINARY_NAME) $(BUILD_DIR)
	@echo "Done! Binary: ./$(BINARY_NAME)"

install: build
	@echo "Installing to $(INSTALL_DIR)..."
	@mkdir -p $(INSTALL_DIR)
	cp $(BINARY_NAME) $(INSTALL_DIR)/
	@echo "Done! Installed to $(INSTALL_DIR)/$(BINARY_NAME)"
	@echo ""
	@echo "Make sure $(INSTALL_DIR) is in your PATH:"
	@echo "  export PATH=\"$(INSTALL_DIR):\$$PATH\""

clean:
	@echo "Cleaning..."
	rm -f $(BINARY_NAME)
	rm -f /tmp/chronos-*.sock
	rm -f /tmp/chronos-tasks-*.map
	rm -f /tmp/chronos-scope-*.stack
	@echo "Done!"

test:
	@echo "Running tests..."
	go test -v ./...

dev:
	@echo "Building with race detector..."
	go build -race -o $(BINARY_NAME) $(BUILD_DIR)
	@echo "Done! Binary: ./$(BINARY_NAME)"
