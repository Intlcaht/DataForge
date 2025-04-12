package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/joho/godotenv" // For loading env vars to system environment
)

// # 📦 Env Client CLI
// A command-line tool for downloading and managing environment variable files from a remote API.
//
// This tool connects to a secure environment management API and retrieves or updates `.env` files for local use.
//
// ## 🔧 Command-line flags:
// - `--env-id <string>`           : (Required) The ID of the environment to access.
// - `--api-key <string>`          : (Optional) Your API key for authentication. Can also be set via ENV_API_KEY.
// - `--source <string>`           : (Optional) Path to the local obfuscated .env file to upload or compare.
// - `--dest <string>`             : (Optional) Path where the downloaded .env file will be saved. Default is `./.env`.
// - `--api-url <string>`          : (Optional) Custom base URL for the API. Default is `https://api.environment.example.com/v1`.
// - `--timeout <int>`             : (Optional) Request timeout in seconds. Default is 30.
//
// ## 🧪 Usage Examples:
//
// ### ▶️ Basic usage (download environment):
// ```bash
// ./env-client --env-id env_abc123 --api-key your-api-key
// ```
// This downloads the environment file for `env_abc123` and saves it to `./.env`.
//
// ---
//
// ### 📂 Specify custom file paths:
// ```bash
// ./env-client --env-id env_abc123 --api-key your-api-key --source ./configs/dev.env.obfuscated --dest ./configs/dev.env
// ```
// Downloads the environment and saves it as `./configs/dev.env`.
// If `--source` is provided, the client may use it to compare with or update remote variables (depending on implementation).
//
// ---
//
// ### 🔐 Use environment variable for API key (recommended for CI):
// ```bash
// export ENV_API_KEY=your-api-key
// ./env-client --env-id env_abc123
// ```
// This avoids hardcoding your API key in scripts or command history.
//
// ---
//
// ### 🌐 Set custom API URL and timeout:
// ```bash
// ./env-client --env-id env_abc123 --api-key your-api-key --api-url https://custom-api.example.com/v2 --timeout 60
// ```
// Useful when targeting staging or alternative backends with a longer request timeout.
//
// ---
//
// ## 🧼 Best Practices:
// - Never commit `.env` files to version control.
// - Store API keys securely (e.g., CI secrets, key vaults).
// - Use `--source` with obfuscated files to prevent leaking secrets.
//
// ## ✅ Exit Codes:
// - `0`: Success
// - `1`: Invalid usage or missing required flags
// - `2`: API request failed
// - `3`: File IO error
//
// ## 🛠️ Example Automation in CI:
// ```yaml
// steps:
//   - name: Download secrets
//     run: ./env-client --env-id env_abc123
//     env:
//       ENV_API_KEY: ${{ secrets.ENV_API_KEY }}
// ```
//
// ---

func main() {
	// Define command-line flags
	apiBaseURL := flag.String("api-url", "https://api.envmanagement.com/v1", "Base URL for the environment API")
	apiKey := flag.String("api-key", "", "API key for authentication")
	envID := flag.String("env-id", "", "Environment ID to work with")
	sourcePath := flag.String("source", "./.env.obfuscated", "Path to the obfuscated .env file")
	destPath := flag.String("dest", "./.env", "Path where the downloaded .env file will be saved")
	timeout := flag.Int("timeout", 30, "Timeout in seconds for API operations")
	flag.Parse()

	// Validate required flags
	if *apiKey == "" {
		// Try to get from environment if not provided as flag
		*apiKey = os.Getenv("ENV_API_KEY")
		if *apiKey == "" {
			log.Fatal("API key is required. Provide it with --api-key flag or ENV_API_KEY environment variable")
		}
	}

	if *envID == "" {
		log.Fatal("Environment ID is required. Provide it with --env-id flag")
	}

	// Create a client with the provided options
	client := env_client.NewEnvClient(
		*apiBaseURL,
		*apiKey,
		&env_client.Options{
			Timeout: time.Duration(*timeout) * time.Second,
		},
	)

	// Create a context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(*timeout+5)*time.Second)
	defer cancel()

	// Read the obfuscated .env file
	fmt.Printf("Reading obfuscated .env file from %s...\n", *sourcePath)
	fileContent, err := os.ReadFile(*sourcePath)
	if err != nil {
		log.Fatalf("Failed to read obfuscated file: %v", err)
	}

	// Upload the file and get a download link
	fmt.Printf("Uploading obfuscated .env file to environment %s...\n", *envID)
	downloadLink, err := client.UploadObfuscatedEnvFile(
		ctx,
		*envID,
		string(fileContent),
	)
	if err != nil {
		log.Fatalf("Failed to upload file: %v", err)
	}
	fmt.Printf("Obtained download link: %s\n", downloadLink)

	// Download the file content from the link
	fmt.Println("Downloading environment file from link...")
	downloadedContent, err := client.DownloadFromLink(ctx, downloadLink)
	if err != nil {
		log.Fatalf("Failed to download content: %v", err)
	}
	fmt.Printf("Downloaded %d bytes of environment data\n", len(downloadedContent))

	// Save the downloaded content to the destination file
	fmt.Printf("Saving downloaded content to %s...\n", *destPath)
	err = os.WriteFile(*destPath, []byte(downloadedContent), 0644)
	if err != nil {
		log.Fatalf("Failed to save downloaded content: %v", err)
	}

	// Load the environment variables into the current process
	fmt.Println("Loading environment variables to system environment...")
	err = godotenv.Load(*destPath)
	if err != nil {
		log.Fatalf("Failed to load environment variables: %v", err)
	}

	// Display the loaded environment variables (masked for sensitive values)
	fmt.Println("Successfully loaded environment variables:")
	// Parse the env file to know which variables were loaded
	loadedVars := parseEnvFile(downloadedContent)
	for key := range loadedVars {
		value := os.Getenv(key)
		// Mask the value if it looks like a secret
		if isSensitiveKey(key) {
			value = maskSensitiveValue(value)
		}
		fmt.Printf("  %s=%s\n", key, value)
	}

	fmt.Println("Environment setup complete!")
}

// parseEnvFile parses a .env file content into a map
func parseEnvFile(content string) map[string]string {
	result := make(map[string]string)
	lines := strings.Split(content, "\n")

	for _, line := range lines {
		line = strings.TrimSpace(line)
		// Skip empty lines and comments
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		// Split by first equals sign
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}

		key := strings.TrimSpace(parts[0])
		value := strings.TrimSpace(parts[1])

		// Remove quotes if present
		if len(value) > 1 && (strings.HasPrefix(value, "\"") && strings.HasSuffix(value, "\"")) ||
			(strings.HasPrefix(value, "'") && strings.HasSuffix(value, "'")) {
			value = value[1 : len(value)-1]
		}

		result[key] = value
	}

	return result
}

// isSensitiveKey checks if a key name suggests it contains sensitive information
func isSensitiveKey(key string) bool {
	key = strings.ToUpper(key)
	sensitivePatterns := []string{
		"KEY", "SECRET", "PASSWORD", "TOKEN", "CREDENTIAL",
		"AUTH", "PRIVATE", "CERT", "PWD", "PASS",
	}

	for _, pattern := range sensitivePatterns {
		if strings.Contains(key, pattern) {
			return true
		}
	}
	return false
}

// maskSensitiveValue masks a sensitive value for display
func maskSensitiveValue(value string) string {
	if len(value) <= 4 {
		return "****"
	}
	return value[:2] + "****" + value[len(value)-2:]
}