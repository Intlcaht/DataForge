// core/registration_handler.go
// This file defines the HTTP handler for the service registration API.
// It receives registration requests from microservices, validates them,
// and registers the services with the core registry.

package core

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

// RegistrationRequest represents the expected JSON payload for service registration.
type RegistrationRequest struct {
	Name     string            `json:"name"`
	Version  string            `json:"version"`
	Endpoint string            `json:"endpoint"`
	Metadata map[string]string `json:"metadata"`
}

// RegistrationResponse represents the JSON payload returned after registration.
type RegistrationResponse struct {
	Message   string `json:"message"`
	ProxyPort int    `json:"proxy_port"`
}

// RegistrationHandler handles incoming service registration requests.
type RegistrationHandler struct {
	registry     *Registry
	proxyManager *ProxyManager
}

// NewRegistrationHandler creates a new RegistrationHandler.
func NewRegistrationHandler(registry *Registry, proxyManager *ProxyManager) *RegistrationHandler {
	return &RegistrationHandler{
		registry:     registry,
		proxyManager: proxyManager,
	}
}

// ServeHTTP implements the http.Handler interface for the registration endpoint.
func (h *RegistrationHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Only POST method is allowed", http.StatusMethodNotAllowed)
		return
	}

	var req RegistrationRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, fmt.Sprintf("Failed to decode request body: %v", err), http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	if req.Name == "" || req.Version == "" || req.Endpoint == "" {
		http.Error(w, "Missing required fields (name, version, endpoint)", http.StatusBadRequest)
		return
	}

	log.Printf("Received registration request for service '%s' (%s) with endpoint '%s'", req.Name, req.Version, req.Endpoint)

	serviceInfo, err := h.registry.RegisterService(req.Name, req.Version, req.Endpoint, req.Metadata)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to register service: %v",err), http.StatusInternalServerError)
		return
	}

	// Once the service is registered, start its proxy.
	if err := h.proxyManager.StartProxy(serviceInfo); err != nil {
		// If proxy start fails, consider de registering the service to avoid inconsistencies.
		h.registry.DeregisterService(req.Name, req.Version)
		http.Error(w, fmt.Sprintf("Failed to start proxy for service '%s': %v", req.Name, err), http.StatusInternalServerError)
		return
	}

	resp := RegistrationResponse{
		Message:   fmt.Sprintf("Service '%s' (%s) registered successfully.", req.Name, req.Version),
		ProxyPort: serviceInfo.ProxyPort,
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		log.Printf("Failed to encode registration response: %v", err)
		// We've already sent a 200 OK status, so just log the error.
	}

	log.Printf("Service '%s' (%s) registered and proxy started on port %d.", req.Name, req.Version, serviceInfo.ProxyPort)
}