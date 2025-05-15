## Modified Icaht Sidecar Architecture

Given that Traefik will handle CORS, caching, rate limiting, and logging, and the services will manage their own logging, the Icaht Sidecar's enrichment features will primarily focus on authentication, authorization, metrics, tracing, request ID injection, and health checks. The authentication logic will also be tailored to Authentik for normal users and Zitadel for admins and employees.

```txt
+---------------------+     +---------------------+     +---------------------+
|       main.go       | --> |     core/           | --> |     auth/           |
+---------------------+     +---------------------+     +---------------------+
| Initializes and     |     | Manages service     |     | Handles             |
| starts the sidecar. |     | registration, proxy |     | authentication and  |
+---------------------+     | lifecycle, and port |     | authorization logic |
                          | allocation.         |     | based on user type. |
                          +---------------------+     +---------------------+
                                  ^
                                  |
+---------------------+     +---------------------+     +---------------------+
|   configuration/    | <-- |     proxy/          | --> |     metrics/        |
+---------------------+     +---------------------+     +---------------------+
| Loads and manages   |     | Configures and runs |     | Exposes metrics for |
| the sidecar's       |     | individual service  |     | Prometheus.         |
| configuration.      |     | proxies.            |     +---------------------+
+---------------------+     +---------------------+
                                  ^
                                  |
+---------------------+     +---------------------+     +---------------------+
|   service-discovery/| --> |   middleware/       | --> |     tracing/        |
+---------------------+     +---------------------+     +---------------------+
| Handles interaction |     | Defines and applies |     | Implements          |
| with service        |     | middleware chains   |     | distributed tracing.|
| discovery systems.  |     | for proxies.        |     +---------------------+
+---------------------+     +---------------------+
                                  ^
                                  |
+---------------------+     +---------------------+
|     health/         | --> |   requestid/        |
+---------------------+     +---------------------+
| Implements health   |     | Manages request ID  |
| check logic.        |     | generation and      |
+---------------------+     | injection.          |
                          +---------------------+
```

## Modified File Descriptions and Functions

Here's an updated breakdown of the purpose and functions of each file, reflecting the removal of certain features and the specific authentication requirements:

**1. `main.go` (Root Directory):**

  * **Purpose:** Remains the entry point, responsible for initializing core components and starting the sidecar.
  * **Functions:**
      * Parses configuration.
      * Initializes core service registration and proxy management.
      * Sets up the API server for service registration.
      * Potentially initializes integrations with service discovery or Traefik configuration management.
      * Handles graceful shutdown.

**2. `core/`:**

  * **Purpose:** Core logic for service registration, proxy lifecycle, and port allocation.
  * **Files and Functions:**
      * `core/registry.go`:
          * **Purpose:** Manages service registration and metadata.
          * **Functions:**
              * Handles registration requests.
              * Validates registration data.
              * Stores service information (name, version, endpoints, authentication type).
              * Assigns unique ports.
              * Manages service-to-port mapping.
              * Handles deregistration.
      * `core/proxy_manager.go`:
          * **Purpose:** Manages the creation, starting, and stopping of service proxies.
          * **Functions:**
              * Listens for registration events.
              * Configures and starts proxies.
              * Passes request handling to `proxy/`.
              * Monitors proxy health.
              * Handles proxy shutdown.

**3. `auth/`:**

  * **Purpose:** Handles authentication and authorization based on user type (normal users via Authentik, admins/employees via Zitadel).
  * **Files and Functions:**
      * `auth/middleware.go`:
          * **Purpose:** Implements the primary authentication and authorization middleware.
          * **Functions:**
              * Determines the authentication method based on configuration or request context.
              * Delegates authentication to either the Authentik or Zitadel handler.
              * Performs authorization checks after successful authentication.
              * Forwards authenticated and authorized requests.
              * Handles unauthorized access.
      * `auth/authentik.go`:
          * **Purpose:** Handles authentication and authorization specifically for normal users via Authentik.
          * **Functions:**
              * Interacts with the Authentik API to verify user credentials (e.g., JWT validation).
              * Extracts user roles or permissions from Authentik.
              * Performs authorization checks based on Authentik's response.
      * `auth/zitadel.go`:
          * **Purpose:** Handles authentication and authorization specifically for admins and employees via Zitadel.
          * **Functions:**
              * Interacts with the Zitadel API to verify user credentials (e.g., OIDC token validation).
              * Extracts user roles or groups from Zitadel.
              * Performs authorization checks based on Zitadel's response.
      * `auth/config.go`:
          * **Purpose:** Manages configuration for Authentik and Zitadel integration per service.
          * **Functions:**
              * Loads configuration for Authentik and Zitadel (e.g., API endpoints, client IDs).
              * Provides access to service-specific authentication requirements.

**4. `metrics/`:**

  * **Purpose:** Exposes metrics for Prometheus.
  * **Files and Functions:**
      * `metrics/exporter.go`:
          * **Purpose:** Collects and exposes proxy metrics.
          * **Functions:**
              * Defines metrics (request counts, latency, errors).
              * Registers metrics.
              * Updates metric values.
              * Exposes `/metrics` endpoint.

**5. `tracing/`:**

  * **Purpose:** Implements distributed tracing.
  * **Files and Functions:**
      * `tracing/tracer.go`:
          * **Purpose:** Initializes and configures the tracing provider.
          * **Functions:**
              * Sets up the tracing library.
              * Configures the exporter.
      * `tracing/middleware.go`:
          * **Purpose:** Handles tracing spans for requests.
          * **Functions:**
              * Starts and propagates trace spans.
              * Extracts and injects trace context.
              * Records span events and attributes.
              * Closes spans.

**6. `requestid/`:**

  * **Purpose:** Manages request ID generation and injection.
  * **Files and Functions:**
      * `requestid/middleware.go`:
          * **Purpose:** Generates and injects request IDs.
          * **Functions:**
              * Generates unique IDs.
              * Injects IDs into request headers.

**7. `health/`:**

  * **Purpose:** Implements health check logic.
  * **Files and Functions:**
      * `health/healthcheck.go`:
          * **Purpose:** Provides health check endpoints.
          * **Functions:**
              * Reports overall sidecar health.
              * Provides health checks for individual proxies.

**8. `service-discovery/`:**

  * **Purpose:** Handles interaction with service discovery systems.
  * **Files and Functions:**
      * `service-discovery/discovery.go`:
          * **Purpose:** Defines the service discovery interface.
          * **Functions:**
              * Defines methods for service registration/deregistration (if needed).
              * Defines methods for service discovery (if needed).
      * `service-discovery/consul.go`, `service-discovery/kubernetes.go`, etc.:
          * **Purpose:** Implementations for specific service discovery systems.
          * **Functions:**
              * Client logic for interacting with discovery platforms.

**9. `proxy/`:**

  * **Purpose:** Core reverse proxy implementation.
  * **Files and Functions:**
      * `proxy/reverse_proxy.go`:
          * **Purpose:** Forwards requests to microservices.
          * **Functions:**
              * Receives proxy requests.
              * Forwards requests to target services.
              * Handles and forwards responses.

**10. `middleware/`:**

  * **Purpose:** Defines the middleware chaining mechanism.
  * **Files and Functions:**
      * `middleware/middleware.go`:
          * **Purpose:** Defines the `Middleware` interface and chaining logic.
          * **Functions:**
              * Defines the middleware interface.
              * Provides a way to apply a chain of middleware.

**11. `configuration/`:**

  * **Purpose:** Loads and manages the sidecar's configuration.
  * **Files and Functions:**
      * `configuration/config.go`:
          * **Purpose:** Defines the configuration structure and loading logic.
          * **Functions:**
              * Defines the configuration structure.
              * Loads configuration from files/environment variables.
              * Provides access to configuration values.

## Structural Folder/File Format

```
icaht-sidecar/
├── main.go                 // Entry point of the application
├── go.mod                  // Go module definition
├── go.sum                  // Go module dependencies
├── core/
│   ├── registry.go         // Manages service registration
│   └── proxy_manager.go    // Manages proxy lifecycle
├── auth/
│   ├── middleware.go       // Main authentication/authorization middleware
│   ├── authentik.go        // Handles Authentik authentication
│   ├── zitadel.go          // Handles Zitadel authentication
│   └── config.go           // Authentication configuration
├── metrics/
│   └── exporter.go         // Exposes Prometheus metrics
├── tracing/
│   ├── tracer.go           // Initializes tracing
│   └── middleware.go       // Tracing middleware
├── requestid/
│   └── middleware.go       // Request ID generation/injection
├── health/
│   └── healthcheck.go      // Health check endpoints
├── service-discovery/
│   ├── discovery.go        // Service discovery interface
│   ├── consul.go           // Consul implementation (if used)
│   └── kubernetes.go       // Kubernetes implementation (if used)
├── proxy/
│   └── reverse_proxy.go    // Core reverse proxy logic
├── middleware/
│   └── middleware.go       // Middleware interface and chaining
├── configuration/
│   └── config.go           // Configuration loading and management
├── internal/               // For internal helper functions (optional)
│   └── ...
├── pkg/                    // For reusable packages (optional)
│   └── ...
├── cmd/                    // For different command-line tools (optional)
│   └── ...
├── config/                 // Example configuration files (optional)
│   └── config.yaml
├── deployments/            // Deployment manifests (e.g., Kubernetes) (optional)
│   └── ...
└── README.md
```
