# =============================================================================
# Makefile for YAML Environment Variable Extractor
# =============================================================================
# This Makefile provides convenient targets for working with the YAML 
# Environment Variable Extractor script.
# =============================================================================

# Default configuration
SCRIPT_NAME = scripts/db_yaml_gen.sh
CONFIG_FILE = app/db.yml
ENV_FILE = .env.gen
BACKUP_DIR = backups

# ANSI color codes for prettier output
YELLOW = \033[1;33m
GREEN = \033[1;32m
RED = \033[1;31m
BLUE = \033[1;34m
RESET = \033[0m

# Default target
.PHONY: help
help:
	@echo "${BLUE}========== YAML Environment Variable Extractor ===========${RESET}"
	@echo ""
	@echo "Available targets:"
	@echo ""
	@echo "${GREEN}make extract${RESET}              Extract environment variables using default settings"
	@echo "${GREEN}make extract-custom${RESET}       Extract with custom config and env files (prompted)"
	@echo "${GREEN}make extract-all${RESET}          Extract from all YAML files in current directory"
	@echo ""
	@echo "${GREEN}make install${RESET}              Make the script executable"
	@echo "${GREEN}make backup${RESET}               Backup existing .env file before extraction"
	@echo "${GREEN}make clean${RESET}                Remove generated .env files"
	@echo "${GREEN}make verify${RESET}               Check if all env variables have been set"
	@echo "${GREEN}make help${RESET}                 Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  ${YELLOW}make CONFIG_FILE=config.yaml ENV_FILE=.env.dev extract${RESET}"
	@echo "  ${YELLOW}make backup extract${RESET}"
	@echo ""

# Make the script executable
.PHONY: install
install:
	@echo "${BLUE}Making script executable...${RESET}"
	@chmod +x $(SCRIPT_NAME)
	@echo "${GREEN}Script is ready to use!${RESET}"

# Backup existing .env file
.PHONY: backup
backup:
	@echo "${BLUE}Backing up existing .env file...${RESET}"
	@if [ -f "$(ENV_FILE)" ]; then \
		mkdir -p $(BACKUP_DIR); \
		cp $(ENV_FILE) $(BACKUP_DIR)/$(ENV_FILE).$(shell date +%Y%m%d%H%M%S).bak; \
		echo "${GREEN}Backup created: $(BACKUP_DIR)/$(ENV_FILE).$(shell date +%Y%m%d%H%M%S).bak${RESET}"; \
	else \
		echo "${YELLOW}No existing $(ENV_FILE) file to backup.${RESET}"; \
	fi

# Extract environment variables using specified config
.PHONY: extract
extract:
	@echo "${BLUE}Extracting environment variables...${RESET}"
	@./$(SCRIPT_NAME) -c $(CONFIG_FILE) -e $(ENV_FILE)

# Interactive extract with custom inputs
.PHONY: extract-custom
extract-custom:
	@echo "${BLUE}Custom extraction:${RESET}"
	@read -p "Enter config file path [$(CONFIG_FILE)]: " config_input; \
	read -p "Enter output .env file path [$(ENV_FILE)]: " env_input; \
	config_file=$${config_input:-$(CONFIG_FILE)}; \
	env_file=$${env_input:-$(ENV_FILE)}; \
	echo "${BLUE}Extracting from $${config_file} to $${env_file}...${RESET}"; \
	./$(SCRIPT_NAME) -c "$${config_file}" -e "$${env_file}"

# Extract from all YAML files in the current directory
.PHONY: extract-all
extract-all:
	@echo "${BLUE}Extracting from all YAML files in current directory...${RESET}"
	@for file in *.yaml *.yml; do \
		if [ -f "$$file" ]; then \
			echo "${YELLOW}Processing $$file...${RESET}"; \
			./$(SCRIPT_NAME) -c "$$file" -e ".$${file%.*}.env"; \
		fi \
	done
	@echo "${GREEN}All YAML files processed!${RESET}"

# Clean generated files
.PHONY: clean
clean:
	@echo "${BLUE}Cleaning up generated .env files...${RESET}"
	@if [ -f "$(ENV_FILE)" ]; then \
		rm -i $(ENV_FILE); \
		echo "${GREEN}Removed $(ENV_FILE)${RESET}"; \
	else \
		echo "${YELLOW}No $(ENV_FILE) file to remove.${RESET}"; \
	fi
	@find . -name "*.env" -not -name "$(ENV_FILE)" -type f -exec echo "Found: {}" \; -exec rm -i {} \;
	@echo "${GREEN}Cleanup complete!${RESET}"

# Verify that all env variables have been set (no REPLACE_ME left)
.PHONY: verify
verify:
	@echo "${BLUE}Verifying environment variables...${RESET}"
	@if [ -f "$(ENV_FILE)" ]; then \
		placeholder_count=$$(grep -c "REPLACE_ME" $(ENV_FILE) || true); \
		if [ "$$placeholder_count" -gt 0 ]; then \
			echo "${RED}Found $$placeholder_count unset variables in $(ENV_FILE)!${RESET}"; \
			grep "REPLACE_ME" $(ENV_FILE); \
			exit 1; \
		else \
			echo "${GREEN}All variables in $(ENV_FILE) have been properly set!${RESET}"; \
		fi \
	else \
		echo "${RED}Error: $(ENV_FILE) file not found!${RESET}"; \
		exit 1; \
	fi

# Combined target: backup + extract
.PHONY: safe-extract
safe-extract: backup extract
	@echo "${GREEN}Safe extraction completed!${RESET}"