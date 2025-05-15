package rest_client

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// ClientOption defines a function signature used to configure the Client.
// This follows the functional options pattern, allowing for flexible and extendable
// client configuration without breaking backward compatibility.
type ClientOption func(*Client)

// Client represents a reusable HTTP REST client.
// It encapsulates configuration and provides methods for making various HTTP requests.
// The client handles common operations like setting default headers, authentication,
// and timeout management.
type Client struct {
	httpClient       *http.Client       // Underlying HTTP client used to make requests
	baseURL          string             // Base URL for all requests (e.g., "https://api.example.com/v1")
	apiKey           string             // Optional API key for authentication
	apiKeyHeaderName string             // Header name used to pass the API key (e.g., "Authorization", "X-API-Key")
	headers          map[string]string  // Default headers applied to every request
	timeout          time.Duration      // Timeout duration for all requests
}

// NewClient creates a new REST client with provided configuration options.
//
// The client is configured using the functional options pattern, which allows
// for clear, flexible, and extensible configuration. Default values are set
// for timeout (30s) and API key header name ("Authorization").
//
// Usage example:
//
//	client := rest_client.NewClient(
//	    rest_client.WithBaseURL("https://api.example.com/v1"),
//	    rest_client.WithAPIKey("your-api-key"),
//	    rest_client.WithTimeout(10 * time.Second),
//	    rest_client.WithHeader("User-Agent", "MyApp/1.0"),
//	)
//
// Parameters:
//   - options: variadic list of ClientOption functions to configure the client.
//
// Returns:
//   - *Client: pointer to a newly created and configured Client instance.
func NewClient(options ...ClientOption) *Client {
	client := &Client{
		httpClient:       &http.Client{},
		headers:          make(map[string]string),
		apiKeyHeaderName: "Authorization",
		timeout:          30 * time.Second,
	}

	// Apply configuration options
	for _, option := range options {
		option(client)
	}

	// Set timeout for the HTTP client
	client.httpClient.Timeout = client.timeout

	return client
}

// WithBaseURL sets the base URL for the client.
// This URL will be used as a prefix for all request paths.
//
// Usage example:
//
//	client := rest_client.NewClient(
//	    rest_client.WithBaseURL("https://api.example.com/v1"),
//	)
//
// Parameters:
//   - baseURL: the root URL for all requests, e.g., "https://api.example.com/v1".
//
// Returns:
//   - ClientOption: a function to set the baseURL on the client.
func WithBaseURL(baseURL string) ClientOption {
	return func(c *Client) {
		c.baseURL = baseURL
	}
}

// WithAPIKey sets the API key for authentication.
// This key will be included in every request in the header specified by apiKeyHeaderName.
//
// Usage example:
//
//	client := rest_client.NewClient(
//	    rest_client.WithAPIKey("sk_1234567890abcdef"),
//	)
//
// Parameters:
//   - apiKey: the secret token or API key to be used for authentication.
//
// Returns:
//   - ClientOption: a function to set the API key on the client.
func WithAPIKey(apiKey string) ClientOption {
	return func(c *Client) {
		c.apiKey = apiKey
	}
}

// WithAPIKeyHeaderName sets the header name to use for the API key.
// By default, "Authorization" is used.
//
// Usage example:
//
//	client := rest_client.NewClient(
//	    rest_client.WithAPIKeyHeaderName("X-API-Key"),
//	)
//
// Parameters:
//   - headerName: the name of the HTTP header (e.g., "Authorization", "X-API-Key").
//
// Returns:
//   - ClientOption: a function to set the API key header name on the client.
func WithAPIKeyHeaderName(headerName string) ClientOption {
	return func(c *Client) {
		c.apiKeyHeaderName = headerName
	}
}

// WithTimeout sets the timeout for all HTTP requests.
// The default timeout is 30 seconds.
//
// Usage example:
//
//	client := rest_client.NewClient(
//	    rest_client.WithTimeout(5 * time.Second),
//	)
//
// Parameters:
//   - timeout: duration before request times out (e.g., 10 * time.Second).
//
// Returns:
//   - ClientOption: a function to set the request timeout on the client.
func WithTimeout(timeout time.Duration) ClientOption {
	return func(c *Client) {
		c.timeout = timeout
	}
}

// WithHeader adds a default header to every request made by the client.
// This is useful for headers like "User-Agent" or "Accept-Language" that
// should be included in all requests.
//
// Usage example:
//
//	client := rest_client.NewClient(
//	    rest_client.WithHeader("User-Agent", "MyApp/1.0"),
//	    rest_client.WithHeader("Accept-Language", "en-US"),
//	)
//
// Parameters:
//   - key: HTTP header key (e.g., "User-Agent", "Accept-Language").
//   - value: HTTP header value (e.g., "MyApp/1.0", "en-US").
//
// Returns:
//   - ClientOption: a function to add the default header to the client.
func WithHeader(key, value string) ClientOption {
	return func(c *Client) {
		c.headers[key] = value
	}
}

// Request represents a generic API request.
// It encapsulates all the information needed to make an HTTP request.
type Request struct {
	Method      string            // HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)
	Path        string            // API endpoint path (appended to baseURL, e.g., "/users")
	QueryParams map[string]string // Optional URL query parameters (e.g., {"page": "1", "limit": "10"})
	Body        interface{}       // Optional request body (usually a struct or map to be JSON-encoded)
	Headers     map[string]string // Optional request-specific headers that override default ones
}

// Response represents a generic API response.
// It provides access to status, headers, and body data returned from an API request.
type Response struct {
	StatusCode int         // HTTP status code (e.g., 200, 404, 500)
	Headers    http.Header // Response headers map
	Body       []byte      // Raw response body as a byte array
}

// Do sends an HTTP request and returns a structured response.
// This is the core method that handles request preparation, execution, and response processing.
// Other methods like Get, Post, etc. are convenience wrappers around this method.
//
// Usage example:
//
//	resp, err := client.Do(ctx, rest_client.Request{
//	    Method: http.MethodPost,
//	    Path: "/users",
//	    Body: map[string]interface{}{
//	        "name": "John Doe",
//	        "email": "john@example.com",
//	    },
//	    Headers: map[string]string{
//	        "X-Request-ID": "req-123",
//	    },
//	})
//
//	if err != nil {
//	    log.Fatalf("Request failed: %v", err)
//	}
//
//	if !resp.IsSuccess() {
//	    log.Fatalf("API returned error: %s", string(resp.Body))
//	}
//
//	var user User
//	if err := resp.Decode(&user); err != nil {
//	    log.Fatalf("Failed to decode response: %v", err)
//	}
//
// Parameters:
//   - ctx: context used for cancellation and timeouts (can be context.Background() or a context with deadline).
//   - request: a Request object containing method, path, headers, and other request details.
//
// Returns:
//   - *Response: structured API response on success, containing status code, headers, and body.
//   - error: wrapped error if the request fails or body cannot be parsed.
//
// Possible Errors:
//   - JSON marshal errors when encoding body.
//   - HTTP request creation errors.
//   - Network or timeout errors on request execution.
//   - Errors while reading response body.
func (c *Client) Do(ctx context.Context, request Request) (*Response, error) {
	url := c.baseURL
	if request.Path != "" {
		url = fmt.Sprintf("%s%s", c.baseURL, request.Path)
	}

	// Append query parameters
	if len(request.QueryParams) > 0 {
		url += "?"
		for key, value := range request.QueryParams {
			url = fmt.Sprintf("%s%s=%s&", url, key, value)
		}
		url = url[:len(url)-1] // remove trailing '&'
	}

	// Prepare request body
	var reqBody io.Reader
	if request.Body != nil {
		jsonBody, err := json.Marshal(request.Body)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal request body: %w", err)
		}
		reqBody = bytes.NewBuffer(jsonBody)
	}

	// Construct HTTP request
	req, err := http.NewRequestWithContext(ctx, request.Method, url, reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	// Apply API key if provided
	if c.apiKey != "" {
		req.Header.Set(c.apiKeyHeaderName, c.apiKey)
	}

	// Apply default headers
	for key, value := range c.headers {
		req.Header.Set(key, value)
	}

	// Apply request-specific headers (override defaults)
	for key, value := range request.Headers {
		req.Header.Set(key, value)
	}

	// Perform HTTP request
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	// Read response
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	return &Response{
		StatusCode: resp.StatusCode,
		Headers:    resp.Header,
		Body:       respBody,
	}, nil
}

// Get sends a GET request to the specified path.
// This is a convenience wrapper around the Do method for GET requests.
//
// Usage example:
//
//	// Get user by ID
//	resp, err := client.Get(
//	    context.Background(),
//	    "/users/123",
//	    nil,  // No query params
//	    nil,  // No special headers
//	)
//
//	// Get users with pagination
//	resp, err := client.Get(
//	    context.Background(),
//	    "/users",
//	    map[string]string{
//	        "page": "2",
//	        "limit": "20",
//	    },
//	    nil,
//	)
//
// Parameters:
//   - ctx: context for request lifecycle (cancellation/timeouts).
//   - path: endpoint path (e.g., "/users/123").
//   - queryParams: optional query parameters as key-value pairs.
//   - headers: optional custom headers for this specific request.
//
// Returns:
//   - *Response: the response object containing status, headers, and body.
//   - error: if the request fails for any reason.
func (c *Client) Get(ctx context.Context, path string, queryParams map[string]string, headers map[string]string) (*Response, error) {
	return c.Do(ctx, Request{
		Method:      http.MethodGet,
		Path:        path,
		QueryParams: queryParams,
		Headers:     headers,
	})
}

// Post sends a POST request.
// This is typically used for creating resources or submitting data.
//
// Usage example:
//
//	// Create a new user
//	resp, err := client.Post(
//	    context.Background(),
//	    "/users",
//	    map[string]interface{}{
//	        "name": "Jane Smith",
//	        "email": "jane@example.com",
//	        "role": "admin",
//	    },
//	    nil,  // No special headers
//	)
//
//	// Authenticate a user
//	resp, err := client.Post(
//	    context.Background(),
//	    "/auth/login",
//	    map[string]string{
//	        "username": "user1",
//	        "password": "secret",
//	    },
//	    nil,
//	)
//
// Parameters:
//   - ctx: context for cancellation/timeouts.
//   - path: endpoint path (e.g., "/users").
//   - body: request payload to be JSON-encoded (struct or map).
//   - headers: optional headers for this specific request.
//
// Returns:
//   - *Response: the response object containing status, headers, and body.
//   - error: if the request fails or body is invalid JSON.
func (c *Client) Post(ctx context.Context, path string, body interface{}, headers map[string]string) (*Response, error) {
	return c.Do(ctx, Request{
		Method:  http.MethodPost,
		Path:    path,
		Body:    body,
		Headers: headers,
	})
}

// Put sends a PUT request.
// This is typically used for updating resources with a complete replacement.
//
// Usage example:
//
//	// Update a user (complete replacement)
//	resp, err := client.Put(
//	    context.Background(),
//	    "/users/123",
//	    map[string]interface{}{
//	        "name": "Jane Doe",
//	        "email": "jane.doe@example.com",
//	        "role": "admin",
//	        "active": true,
//	    },
//	    nil,
//	)
//
// Parameters:
//   - ctx: context for cancellation/timeouts.
//   - path: endpoint path (e.g., "/users/123").
//   - body: request payload to be JSON-encoded (struct or map).
//   - headers: optional headers for this specific request.
//
// Returns:
//   - *Response: the response object containing status, headers, and body.
//   - error: if the request fails or body is invalid JSON.
func (c *Client) Put(ctx context.Context, path string, body interface{}, headers map[string]string) (*Response, error) {
	return c.Do(ctx, Request{
		Method:  http.MethodPut,
		Path:    path,
		Body:    body,
		Headers: headers,
	})
}

// Delete sends a DELETE request.
// This is typically used for removing resources.
//
// Usage example:
//
//	// Delete a user
//	resp, err := client.Delete(
//	    context.Background(),
//	    "/users/123",
//	    nil,  // No special headers
//	)
//
//	// Delete with confirmation header
//	resp, err := client.Delete(
//	    context.Background(),
//	    "/critical-resource/456",
//	    map[string]string{
//	        "X-Confirm-Delete": "true",
//	    },
//	)
//
// Parameters:
//   - ctx: context for request lifecycle (cancellation/timeouts).
//   - path: endpoint path (e.g., "/users/123").
//   - headers: optional custom headers for this specific request.
//
// Returns:
//   - *Response: the response object containing status, headers, and body.
//   - error: if the request fails for any reason.
func (c *Client) Delete(ctx context.Context, path string, headers map[string]string) (*Response, error) {
	return c.Do(ctx, Request{
		Method:  http.MethodDelete,
		Path:    path,
		Headers: headers,
	})
}

// Patch sends a PATCH request.
// This is typically used for partial updates to resources.
//
// Usage example:
//
//	// Update only specific fields of a user
//	resp, err := client.Patch(
//	    context.Background(),
//	    "/users/123",
//	    map[string]interface{}{
//	        "email": "new.email@example.com",
//	        // Only updating email, other fields remain unchanged
//	    },
//	    nil,
//	)
//
// Parameters:
//   - ctx: context for cancellation/timeouts.
//   - path: endpoint path (e.g., "/users/123").
//   - body: request payload to be JSON-encoded, typically containing only changed fields.
//   - headers: optional headers for this specific request.
//
// Returns:
//   - *Response: the response object containing status, headers, and body.
//   - error: if the request fails or body is invalid JSON.
func (c *Client) Patch(ctx context.Context, path string, body interface{}, headers map[string]string) (*Response, error) {
	return c.Do(ctx, Request{
		Method:  http.MethodPatch,
		Path:    path,
		Body:    body,
		Headers: headers,
	})
}

// Decode un marshals the JSON response body into the given interface.
// This provides convenient access to structured response data.
//
// Usage example:
//
//	var user struct {
//	    ID    string `json:"id"`
//	    Name  string `json:"name"`
//	    Email string `json:"email"`
//	}
//
//	resp, err := client.Get(context.Background(), "/users/123", nil, nil)
//	if err != nil {
//	    return err
//	}
//
//	if err := resp.Decode(&user); err != nil {
//	    return fmt.Errorf("failed to decode user: %w", err)
//	}
//
//	fmt.Printf("User: %s (%s)\n", user.Name, user.Email)
//
// Parameters:
//   - v: pointer to the target struct or map to decode into (e.g., &myStruct or &map[string]interface{}).
//
// Returns:
//   - error: if the body cannot be unmarshaled (invalid JSON or type mismatch).
func (r *Response) Decode(v interface{}) error {
	return json.Unmarshal(r.Body, v)
}

// IsSuccess returns true if the HTTP status code is in the 2xx range (successful).
// This is a convenient way to check if a request was successful.
//
// Usage example:
//
//	resp, err := client.Get(context.Background(), "/users/123", nil, nil)
//	if err != nil {
//	    return err
//	}
//
//	if !resp.IsSuccess() {
//	    return fmt.Errorf("API error: %d - %s", resp.StatusCode, string(resp.Body))
//	}
//
// Returns:
//   - bool: true if status is between 200 and 299 (inclusive).
func (r *Response) IsSuccess() bool {
	return r.StatusCode >= 200 && r.StatusCode < 300
}

// UploadFile uploads a file to the specified path.
// This method supports binary uploads with specified content type.
//
// Usage example:
//
//	file, err := os.Open("document.pdf")
//	if err != nil {
//	    return err
//	}
//	defer file.Close()
//
//	err = client.UploadFile("/documents/upload", file, "application/pdf")
//	if err != nil {
//	    return fmt.Errorf("upload failed: %w", err)
//	}
//
// Parameters:
//   - path: endpoint path for the upload (e.g., "/documents/upload").
//   - file: io.Reader containing the file data to upload.
//   - contentType: MIME type of the file being uploaded (e.g., "application/pdf", "image/jpeg").
//
// Returns:
//   - error: if the upload fails for any reason.
func (c *Client) UploadFile(path string, file io.Reader, contentType string) error {
	reqURL, _ := c.BaseURL.Parse(path)
	req, err := http.NewRequest("PUT", reqURL.String(), file)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", contentType)
	req.Header.Set("Authorization", "Bearer "+c.APIKey)
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("upload failed: %s", string(body))
	}
	return nil
}

// DownloadFile downloads a file from the specified path.
// The file is returned as a byte array, which can be written to disk or processed in memory.
//
// Usage example:
//
//	data, err := client.DownloadFile("/documents/123/download")
//	if err != nil {
//	    return err
//	}
//
//	// Write to file
//	err = os.WriteFile("downloaded-document.pdf", data, 0644)
//	if err != nil {
//	    return fmt.Errorf("failed to save file: %w", err)
//	}
//
// Parameters:
//   - path: endpoint path for the download (e.g., "/documents/123/download").
//
// Returns:
//   - []byte: byte array containing the downloaded file data.
//   - error: if the download fails for any reason.
func (c *Client) DownloadFile(path string) ([]byte, error) {
	reqURL, _ := c.BaseURL.Parse(path)
	req, err := http.NewRequest("GET", reqURL.String(), nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+c.APIKey)
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}