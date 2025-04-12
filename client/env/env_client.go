package env_client

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	// "github.com/your-org/rest_client" // Adjust import path as needed
)

// | `GET`       | `/envs/{env_id}`                          | Get environment details                     | `EnvironmentService`          |
// | `DELETE`    | `/envs/{env_id}`                          | Delete environment                          | `EnvironmentService`          |
// | `POST`      | `/envs/{env_id}/variables/`               | Set or update a variable                    | `EnvVariableService`          |
// | `GET`       | `/envs/{env_id}/variables/`               | List variables (optionally masked)          | `EnvVariableService`          |
// | `GET`       | `/envs/{env_id}/variables/{key}`          | Get a single variable                       | `EnvVariableService`          |
// | `DELETE`    | `/envs/{env_id}/variables/{key}`          | Delete a variable                           | `EnvVariableService`          |
// | `POST`      | `/envs/{env_id}/import/`                  | Import `.env` text                          | `EnvVariableService`          |
// | `GET`       | `/envs/{env_id}/export/`                  | Export `.env` text                          | `EnvVariableService`          |
// | `POST`      | `/envs/{env_id}/share/`                   | Generate one-time download link 
// EnvClient is a specialized client for interacting with the Environment Management API.
// It wraps the underlying REST client and provides domain-specific methods.
type EnvClient struct {
	client *rest_client.Client // Underlying REST client for HTTP operations
}

// Environment represents an environment in the system
type Environment struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// EnvVariable represents a variable stored in an environment
type EnvVariable struct {
	Key       string    `json:"key"`
	Value     string    `json:"value,omitempty"` // Will be empty if masked
	IsMasked  bool      `json:"is_masked"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// EnvVariableRequest represents a request to create or update a variable
type EnvVariableRequest struct {
	Key      string `json:"key"`
	Value    string `json:"value"`
	IsMasked bool   `json:"is_masked,omitempty"`
}

// ListVariablesOptions provides options for listing variables
type ListVariablesOptions struct {
	IncludeMaskedValues bool `json:"include_masked_values,omitempty"`
}

// ImportEnvRequest represents a request to import variables from .env format
type ImportEnvRequest struct {
	Content          string `json:"content"`
	OverwriteExisting bool   `json:"overwrite_existing,omitempty"`
}

// ShareLinkResponse represents the response when generating a share link
type ShareLinkResponse struct {
	URL       string    `json:"url"`
	ExpiresAt time.Time `json:"expires_at"`
	Token     string    `json:"token"`
}

// DownloadLinkResponse holds information about a download link
type DownloadLinkResponse struct {
	URL string `json:"url"`
}

// NewEnvClient creates a new Environment API client.
//
// This function initializes a new API client for interacting with the environment
// management service. It's a wrapper around the underlying REST client, providing
// domain-specific methods.
//
// Usage example:
//
//	// Basic client with just API key
//	client := env_api.NewEnvClient(
//	    "https://api.envmanagement.com/v1",
//	    "your-api-key",
//	    nil, // Use default options
//	)
//
//	// Client with custom options
//	client := env_api.NewEnvClient(
//	    "https://api.envmanagement.com/v1",
//	    "your-api-key",
//	    &env_api.Options{
//	        Timeout: 15 * time.Second,
//	        APIKeyHeaderName: "X-API-Key",
//	    },
//	)
//
// Parameters:
//   - baseURL: The base URL of the API (e.g., "https://api.envmanagement.com/v1")
//   - apiKey: Your API key for authentication
//   - options: Optional configuration settings (can be nil for defaults)
//
// Returns:
//   - *EnvClient: A configured API client ready to use
func NewEnvClient(baseURL, apiKey string, options *Options) *EnvClient {
	// Default options if none provided
	if options == nil {
		options = &Options{}
	}

	// Set defaults for unspecified options
	apiKeyHeader := options.APIKeyHeaderName
	if apiKeyHeader == "" {
		apiKeyHeader = "Authorization"
	}

	timeout := options.Timeout
	if timeout == 0 {
		timeout = 30 * time.Second
	}

	// Configure the REST client with our options
	restClient := rest_client.NewClient(
		rest_client.WithBaseURL(baseURL),
		rest_client.WithAPIKey(apiKey),
		rest_client.WithAPIKeyHeaderName(apiKeyHeader),
		rest_client.WithTimeout(timeout),
		rest_client.WithHeader("User-Agent", "EnvClient-Go-Client/1.0"),
	)

	// Add additional headers if specified
	for k, v := range options.Headers {
		restClient = rest_client.NewClient(rest_client.WithHeader(k, v))
	}

	return &EnvClient{
		client: restClient,
	}
}

// Options contains configuration options for the EnvClient client
type Options struct {
	APIKeyHeaderName string            // Header name for API key (default: "Authorization")
	Timeout          time.Duration     // Request timeout (default: 30s)
	Headers          map[string]string // Additional headers to include in all requests
}

// ----- Environment Operations -----

// GetEnvironment retrieves details for a specific environment.
//
// Usage example:
//
//	env, err := client.GetEnvironment(context.Background(), "env_123abc")
//	if err != nil {
//	    log.Fatalf("Failed to get environment: %v", err)
//	}
//	fmt.Printf("Environment: %s (Created: %s)\n", env.Name, env.CreatedAt)
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Unique identifier of the environment to retrieve
//
// Returns:
//   - *Environment: Details of the requested environment
//   - error: Any error encountered during the request
func (api *EnvClient) GetEnvironment(ctx context.Context, envID string) (*Environment, error) {
	path := fmt.Sprintf("/envs/%s", envID)
	
	resp, err := api.client.Get(ctx, path, nil, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get environment: %w", err)
	}
	
	if !resp.IsSuccess() {
		return nil, fmt.Errorf("API error: %d - %s", resp.StatusCode, string(resp.Body))
	}
	
	var env Environment
	if err := resp.Decode(&env); err != nil {
		return nil, fmt.Errorf("failed to decode environment: %w", err)
	}
	
	return &env, nil
}

// DeleteEnvironment permanently removes an environment and all its variables.
//
// Usage example:
//
//	err := client.DeleteEnvironment(context.Background(), "env_123abc")
//	if err != nil {
//	    log.Fatalf("Failed to delete environment: %v", err)
//	}
//	fmt.Println("Environment successfully deleted")
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Unique identifier of the environment to delete
//
// Returns:
//   - error: Any error encountered during the deletion
func (api *EnvClient) DeleteEnvironment(ctx context.Context, envID string) error {
	path := fmt.Sprintf("/envs/%s", envID)
	
	resp, err := api.client.Delete(ctx, path, nil)
	if err != nil {
		return fmt.Errorf("failed to delete environment: %w", err)
	}
	
	if !resp.IsSuccess() {
		return fmt.Errorf("API error: %d - %s", resp.StatusCode, string(resp.Body))
	}
	
	return nil
}

// ----- Environment Variables Operations -----

// SetVariable creates or updates an environment variable.
//
// Usage example:
//
//	// Create a regular variable
//	err := client.SetVariable(context.Background(), "env_123abc", &env_api.EnvVariableRequest{
//	    Key: "DATABASE_URL",
//	    Value: "postgres://username:password@localhost:5432/my_db",
//	    IsMasked: false,
//	})
//
//	// Create a masked variable (sensitive data)
//	err := client.SetVariable(context.Background(), "env_123abc", &env_api.EnvVariableRequest{
//	    Key: "API_SECRET",
//	    Value: "very-secret-value",
//	    IsMasked: true,
//	})
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Environment identifier
//   - variable: Variable details including key, value, and masking preference
//
// Returns:
//   - *EnvVariable: The created or updated variable
//   - error: Any error encountered during the operation
func (api *EnvClient) SetVariable(ctx context.Context, envID string, variable *EnvVariableRequest) (*EnvVariable, error) {
	path := fmt.Sprintf("/envs/%s/variables/", envID)
	
	resp, err := api.client.Post(ctx, path, variable, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to set variable: %w", err)
	}
	
	if !resp.IsSuccess() {
		return nil, fmt.Errorf("API error: %d - %s", resp.StatusCode, string(resp.Body))
	}
	
	var result EnvVariable
	if err := resp.Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}
	
	return &result, nil
}

// ListVariables retrieves all variables in an environment.
//
// By default, masked variable values are hidden. Set includeMaskedValues to true
// to retrieve the actual values of masked variables.
//
// Usage example:
//
//	// List variables without showing masked values
//	variables, err := client.ListVariables(context.Background(), "env_123abc", false)
//
//	// List variables with all values visible
//	variables, err := client.ListVariables(context.Background(), "env_123abc", true)
//	if err != nil {
//	    log.Fatalf("Failed to list variables: %v", err)
//	}
//
//	for _, v := range variables {
//	    fmt.Printf("%s=%s (masked: %v)\n", v.Key, v.Value, v.IsMasked)
//	}
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Environment identifier
//   - includeMaskedValues: Whether to include actual values for masked variables
//
// Returns:
//   - []EnvVariable: List of environment variables
//   - error: Any error encountered during the request
func (api *EnvClient) ListVariables(ctx context.Context, envID string, includeMaskedValues bool) ([]EnvVariable, error) {
	path := fmt.Sprintf("/envs/%s/variables/", envID)
	
	queryParams := map[string]string{
		"include_masked_values": fmt.Sprintf("%t", includeMaskedValues),
	}
	
	resp, err := api.client.Get(ctx, path, queryParams, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to list variables: %w", err)
	}
	
	if !resp.IsSuccess() {
		return nil, fmt.Errorf("API error: %d - %s", resp.StatusCode, string(resp.Body))
	}
	
	var variables []EnvVariable
	if err := resp.Decode(&variables); err != nil {
		return nil, fmt.Errorf("failed to decode variables: %w", err)
	}
	
	return variables, nil
}

// GetVariable retrieves a specific variable by key.
//
// Usage example:
//
//	variable, err := client.GetVariable(context.Background(), "env_123abc", "DATABASE_URL")
//	if err != nil {
//	    log.Fatalf("Failed to get variable: %v", err)
//	}
//	fmt.Printf("Variable: %s=%s\n", variable.Key, variable.Value)
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Environment identifier
//   - key: Variable key to retrieve
//
// Returns:
//   - *EnvVariable: The requested variable
//   - error: Any error encountered during the request
func (api *EnvClient) GetVariable(ctx context.Context, envID, key string) (*EnvVariable, error) {
	path := fmt.Sprintf("/envs/%s/variables/%s", envID, key)
	
	resp, err := api.client.Get(ctx, path, nil, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get variable: %w", err)
	}
	
	if !resp.IsSuccess() {
		return nil, fmt.Errorf("API error: %d - %s", resp.StatusCode, string(resp.Body))
	}
	
	var variable EnvVariable
	if err := resp.Decode(&variable); err != nil {
		return nil, fmt.Errorf("failed to decode variable: %w", err)
	}
	
	return &variable, nil
}

// DeleteVariable removes a variable from an environment.
//
// Usage example:
//
//	err := client.DeleteVariable(context.Background(), "env_123abc", "OLD_API_KEY")
//	if err != nil {
//	    log.Fatalf("Failed to delete variable: %v", err)
//	}
//	fmt.Println("Variable successfully deleted")
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Environment identifier
//   - key: Variable key to delete
//
// Returns:
//   - error: Any error encountered during the deletion
func (api *EnvClient) DeleteVariable(ctx context.Context, envID, key string) error {
	path := fmt.Sprintf("/envs/%s/variables/%s", envID, key)
	
	resp, err := api.client.Delete(ctx, path, nil)
	if err != nil {
		return fmt.Errorf("failed to delete variable: %w", err)
	}
	
	if !resp.IsSuccess() {
		return fmt.Errorf("API error: %d - %s", resp.StatusCode, string(resp.Body))
	}
	
	return nil
}

// ImportEnvFile imports variables from a .env file format.
//
// This method accepts a string in standard .env file format and creates 
// or updates variables in the specified environment.
//
// Usage example:
//
//	envContent := `
//	DATABASE_URL=postgres://user:pass@localhost/db
//	API_KEY=secret-key
//	DEBUG=true
//	`
//	
//	err := client.ImportEnvFile(context.Background(), "env_123abc", envContent, true)
//	if err != nil {
//	    log.Fatalf("Failed to import variables: %v", err)
//	}
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Environment identifier
//   - content: String containing .env formatted variables
//   - overwrite: Whether to overwrite existing variables with the same keys
//
// Returns:
//   - error: Any error encountered during the import
func (api *EnvClient) ImportEnvFile(ctx context.Context, envID, content string, overwrite bool) error {
	path := fmt.Sprintf("/envs/%s/import/", envID)
	
	req := ImportEnvRequest{
		Content:           content,
		OverwriteExisting: overwrite,
	}
	
	resp, err := api.client.Post(ctx, path, req, nil)
	if err != nil {
		return fmt.Errorf("failed to import .env: %w", err)
	}
	
	if !resp.IsSuccess() {
		return fmt.Errorf("API error: %d - %s", resp.StatusCode, string(resp.Body))
	}
	
	return nil
}

// ExportEnvFile exports environment variables in .env file format.
//
// Usage example:
//
//	content, err := client.ExportEnvFile(context.Background(), "env_123abc")
//	if err != nil {
//	    log.Fatalf("Failed to export variables: %v", err)
//	}
//	
//	fmt.Println("Exported .env file:")
//	fmt.Println(content)
//	
//	// Save to file
//	err = os.WriteFile(".env", []byte(content), 0644)
//	if err != nil {
//	    log.Fatalf("Failed to write .env file: %v", err)
//	}
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Environment identifier
//
// Returns:
//   - string: .env file format content
//   - error: Any error encountered during the export
func (api *EnvClient) ExportEnvFile(ctx context.Context, envID string) (string, error) {
	path := fmt.Sprintf("/envs/%s/export/", envID)
	
	resp, err := api.client.Get(ctx, path, nil, nil)
	if err != nil {
		return "", fmt.Errorf("failed to export .env: %w", err)
	}
	
	if !resp.IsSuccess() {
		return "", fmt.Errorf("API error: %d - %s", resp.StatusCode, string(resp.Body))
	}
	
	// The response body contains the .env file content as plain text
	return string(resp.Body), nil
}

// GenerateShareLink creates a one-time download link for an environment.
//
// The generated link can be shared with others to grant temporary access
// to the environment variables.
//
// Usage example:
//
//	shareLink, err := client.GenerateShareLink(context.Background(), "env_123abc")
//	if err != nil {
//	    log.Fatalf("Failed to generate share link: %v", err)
//	}
//	
//	fmt.Printf("Share this link: %s\n", shareLink.URL)
//	fmt.Printf("Link expires at: %s\n", shareLink.ExpiresAt)
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Environment identifier
//
// Returns:
//   - *ShareLinkResponse: Details about the generated share link
//   - error: Any error encountered during link generation
func (api *EnvClient) GenerateShareLink(ctx context.Context, envID string) (*ShareLinkResponse, error) {
	path := fmt.Sprintf("/envs/%s/share/", envID)
	
	resp, err := api.client.Post(ctx, path, nil, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to generate share link: %w", err)
	}
	
	if !resp.IsSuccess() {
		return nil, fmt.Errorf("API error: %d - %s", resp.StatusCode, string(resp.Body))
	}
	
	var result ShareLinkResponse
	if err := resp.Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode share link response: %w", err)
	}
	
	return &result, nil
}

// ----- Extended API Methods -----

// UploadObfuscatedEnvFile uploads an obfuscated .env file and returns a download link.
//
// This is a higher-level method that combines multiple API operations to:
// 1. Read an obfuscated .env file
// 2. Upload it to a specific environment
// 3. Generate and return a one-time download link
//
// Usage example:
//
//	// Read an obfuscated .env file
//	fileContent, err := os.ReadFile("./obfuscated.env")
//	if err != nil {
//	    log.Fatalf("Failed to read file: %v", err)
//	}
//	
//	// Upload the file and get a download link
//	downloadLink, err := client.UploadObfuscatedEnvFile(
//	    context.Background(),
//	    "env_123abc",
//	    string(fileContent),
//	)
//	if err != nil {
//	    log.Fatalf("Failed to upload file: %v", err)
//	}
//	
//	fmt.Printf("Download link: %s\n", downloadLink)
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Environment identifier
//   - fileContent: Content of the obfuscated .env file
//
// Returns:
//   - string: URL where the file can be downloaded
//   - error: Any error encountered during the process
func (api *EnvClient) UploadObfuscatedEnvFile(ctx context.Context, envID, fileContent string) (string, error) {
	// Step 1: Import the .env file
	err := api.ImportEnvFile(ctx, envID, fileContent, true)
	if err != nil {
		return "", fmt.Errorf("failed to import obfuscated env file: %w", err)
	}
	
	// Step 2: Generate a download link
	shareLink, err := api.GenerateShareLink(ctx, envID)
	if err != nil {
		return "", fmt.Errorf("failed to generate download link: %w", err)
	}
	
	return shareLink.URL, nil
}

// DownloadFromLink downloads content from a generated share link.
//
// This method retrieves the content from a URL previously generated by
// GenerateShareLink or UploadObfuscatedEnvFile.
//
// Usage example:
//
//	// Download from a link
//	content, err := client.DownloadFromLink(context.Background(), "https://api.example.com/download/abc123")
//	if err != nil {
//	    log.Fatalf("Failed to download content: %v", err)
//	}
//	
//	// Save the downloaded content to a file
//	err = os.WriteFile("downloaded.env", []byte(content), 0644)
//	if err != nil {
//	    log.Fatalf("Failed to save downloaded content: %v", err)
//	}
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - url: Download URL to retrieve content from
//
// Returns:
//   - string: Content retrieved from the URL
//   - error: Any error encountered during download
func (api *EnvClient) DownloadFromLink(ctx context.Context, url string) (string, error) {
	// Create a new request directly to the URL
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}
	
	// Use the HTTP client from the underlying REST client
	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("download request failed: %w", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("download failed with status %d: %s", resp.StatusCode, string(body))
	}
	
	// Read the content
	content, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read download content: %w", err)
	}
	
	return string(content), nil
}

// ----- Convenience Helper Methods -----

// SaveEnvToFile downloads environment variables and saves them to a file.
//
// This is a convenience method that exports environment variables and
// saves them directly to a local file.
//
// Usage example:
//
//	err := client.SaveEnvToFile(context.Background(), "env_123abc", "./.env")
//	if err != nil {
//	    log.Fatalf("Failed to save .env file: %v", err)
//	}
//	fmt.Println("Environment variables saved to .env file")
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Environment identifier
//   - filePath: Path where the .env file should be saved
//
// Returns:
//   - error: Any error encountered during the process
func (api *EnvClient) SaveEnvToFile(ctx context.Context, envID, filePath string) error {
	// Export the environment variables
	content, err := api.ExportEnvFile(ctx, envID)
	if err != nil {
		return fmt.Errorf("failed to export environment: %w", err)
	}
	
	// Save to file
	err = os.WriteFile(filePath, []byte(content), 0644)
	if err != nil {
		return fmt.Errorf("failed to write file: %w", err)
	}
	
	return nil
}

// LoadEnvFromFile reads a .env file and imports it to an environment.
//
// This is a convenience method that reads a local .env file and
// imports its variables to a specified environment.
//
// Usage example:
//
//	err := client.LoadEnvFromFile(context.Background(), "env_123abc", "./.env", true)
//	if err != nil {
//	    log.Fatalf("Failed to load .env file: %v", err)
//	}
//	fmt.Println("Environment variables imported from .env file")
//
// Parameters:
//   - ctx: Context for request cancellation/timeouts
//   - envID: Environment identifier
//   - filePath: Path to the .env file to be imported
//   - overwrite: Whether to overwrite existing variables
//
// Returns:
//   - error: Any error encountered during the process
func (api *EnvClient) LoadEnvFromFile(ctx context.Context, envID, filePath string, overwrite bool) error {
	// Read the file
	content, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("failed to read file: %w", err)
	}
	
	// Import the variables
	err = api.ImportEnvFile(ctx, envID, string(content), overwrite)
	if err != nil {
		return fmt.Errorf("failed to import variables: %w", err)
	}
	
	return nil
}