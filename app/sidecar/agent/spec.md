## Icaht Sidecar Agent Specification (Final)

**🌟 Overview**

The **Icaht Sidecar Agent** is a lightweight, per-microservice component designed to enhance the integration between individual microservices and the Icaht Sidecar, as well as broader centralized infrastructure. It provides utility services that simplify common cross-cutting concerns, promoting consistency, security, and observability across the microservice ecosystem.

**🎯 Key Responsibilities**

1.  **Metrics Reporting:** Standardized and efficient pushing of application-level metrics to the Icaht Sidecar or a dedicated metrics aggregation system.
2.  **Structured Audit Logging:** Utility for submitting structured audit records related to user actions and system events to a centralized audit logging service, potentially routed via the sidecar.
3.  **Secure Request User Information Access:** Facilitates secure and easy retrieval of authenticated user information associated with the incoming request processed by the sidecar.
4.  **Distributed Configuration Retrieval:** Enables microservices to dynamically fetch service-specific configuration from a centralized configuration management system.
5.  **Feature Flag Evaluation:** Provides a local mechanism for evaluating feature flags, potentially fetching flag configurations from a central service.
6.  **Outbound Request Interception (Optional):** Allows the agent to intercept outbound HTTP(s) requests made by the microservice to inject necessary headers (e.g., request IDs, tracing spans) or enforce basic policies.

**🧱 Agent Specification Details**

### 1. Metrics Reporting Utility

* **Mechanism:** Local API (gRPC or HTTP) for microservices to report metrics.
* **Data Format:** Standard format (JSON or Protocol Buffers) including:
    * `Metric Name` (string, required)
    * `Value` (numeric, required)
    * `Timestamp` (ISO 8601 string or Unix timestamp, required)
    * `Tags` (map\<string, string\>, optional)
* **Transport to Sidecar/Central System:**
    * Periodically batching and sending via HTTP/gRPC to a sidecar endpoint.
    * Directly publishing to a metrics broker (e.g., Kafka, Prometheus Push gateway). Configuration determines the target.
* **Configuration:** Target endpoint(s), reporting interval, batch size.
* **Best Practices:** Asynchronous, buffering with retries (exponential backoff), minimal overhead, configurable reporting frequency.

### 2. Structured Audit Logging Utility

* **Mechanism:** Local API for submitting audit records.
* **Data Format:** Standard format (JSON or Protocol Buffers) including:
    * `Timestamp` (ISO 8601 string or Unix timestamp, required)
    * `UserID` (string, optional)
    * `Action` (string, required)
    * `Resource` (string, optional)
    * `Details` (map\<string, interface{}\>, optional)
    * `Severity` (string, e.g., "INFO", "WARNING", "ERROR", required)
* **Transport to Central System:**
    * Sending via HTTP/gRPC to a sidecar endpoint for forwarding.
    * Directly publishing to a logging platform (e.g., Elasticsearch, cloud logging). Configuration determines the target.
* **Configuration:** Target endpoint(s), batching settings, logging level.
* **Best Practices:** Reliable delivery (queueing, retries), structured format, correlation with request IDs, secure handling of sensitive data.

### 3. Secure Request User Information Access Utility

* **Mechanism:** Local API call within the microservice's request context.
* **Information Source:** Retrieves information propagated by the Icaht Sidecar (e.g., via headers or a local shared context).
* **Data Format:** Structured object containing:
    * `UserID` (string, required)
    * `Username` (string, optional)
    * `Roles` (array\<string\>, optional)
    * `Permissions` (array\<string\>, optional)
    * `Claims` (map\<string, interface{}\>, optional) - other attributes from the authentication token.
* **Security:** Access restricted to the processing thread/context of the incoming request.
* **Best Practices:** Local caching within request lifecycle, abstraction of retrieval mechanism, read-only access, clear API for accessing specific attributes.

### 4. Distributed Configuration Retrieval Utility

* **Mechanism:** Local API for fetching configuration parameters by key.
* **Source:** Interacts with a centralized configuration management system (e.g., HashiCorp Consul KV, Spring Cloud Config Server), potentially via the sidecar acting as a proxy or directly.
* **Data Format:** Returns the configuration value as a string or a structured object (based on content type).
* **Caching:** The agent can implement local caching of configuration values with a configurable TTL to reduce load on the central system.
* **Updates:** Supports mechanisms for detecting and applying configuration updates (e.g., long-polling, webhooks).
* **Configuration:** Endpoint of the configuration server, polling interval (if applicable), caching TTL.
* **Best Practices:** Asynchronous fetching, local caching, graceful handling of configuration server unavailability, versioning of configuration.

### 5. Feature Flag Evaluation Utility

* **Mechanism:** Local API for evaluating the status (on/off, variant) of a feature flag by name.
* **Source:** Fetches feature flag configurations from a centralized feature flag management service (e.g., LaunchDarkly, Split). This fetch can be direct or via the sidecar.
* **Evaluation:** Provides a local evaluation engine that can determine the flag's status based on context (e.g., user ID, service version).
* **Caching:** The agent should cache flag configurations for efficient evaluation.
* **Updates:** Supports mechanisms for receiving real-time updates to flag configurations.
* **Configuration:** Endpoint of the feature flag service, polling/streaming settings, default flag values.
* **Best Practices:** Local evaluation for performance, real-time updates, targeting rules based on context, default values in case of service unavailability.

### 6. Outbound Request Interception (Optional)

* **Mechanism:** Provides interceptors or wrappers for the microservice's HTTP client.
* **Functionality:**
    * **Header Injection:** Automatically injects standard headers like request IDs, tracing spans, or authentication tokens for inter-service communication.
    * **Basic Policy Enforcement:** Can enforce basic policies like retries or timeouts for outbound requests.
    * **Metrics Collection (Outbound):** Can automatically collect basic metrics about outbound request latency and status codes.
* **Configuration:** Rules for header injection, retry policies, timeout settings.
* **Best Practices:** Minimal performance overhead, configurable interception, support for common HTTP client libraries, clear separation of concerns from the core application logic.

**⚙️ Agent Communication with Sidecar and Central Infrastructure**

The agent will require flexible communication mechanisms:

* **Local HTTP/gRPC API (to Sidecar):** For pushing metrics, audit logs, and potentially querying for immediate request context.
* **Direct HTTP/gRPC to Central Services:** For configuration and feature flag retrieval, and potentially direct metrics/audit log pushing.
* **Message Queues (Publishing):** For asynchronous metrics and audit log delivery.

**🌱 Best Practices for Building Agents (Expanded)**

* **Keep it Lightweight:** Minimal dependencies, small footprint, efficient resource usage.
* **Simplicity:** Easy-to-use API for microservice developers, clear and concise functionality.
* **Resilience:** Graceful handling of network issues and unavailability of dependent services (sidecar, central systems). Circuit breaker patterns can be considered.
* **Observability:** Self-monitoring via metrics and logs.
* **Configuration Management:** Externalized configuration via environment variables or configuration files. Dynamic configuration updates.
* **Security First:** Secure communication channels (TLS), proper handling of sensitive data, and potentially mutual TLS with the sidecar or central services.
* **Language Agnostic Design:** Architectural principles should be adaptable across different programming languages. Consider providing SDKs or client libraries in common languages.
* **Extensibility:** Design the agent to be extensible with new utilities or customizations through plugins or middleware.
* **Idempotency (for Data Pushing):** Ensure that retries for metrics and audit logs don't lead to duplicate data.
* **Contextual Awareness:** Ensure utilities operate within the context of the current request where applicable (e.g., accessing user info).
