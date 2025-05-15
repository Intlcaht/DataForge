// core/registry.go
// This file defines the service registry, which is responsible for
// storing and managing information about the registered microservices.
// It provides mechanisms to add, retrieve, and remove service details.

package core

import (
	"fmt"
	"sync"
)

// ServiceInfo holds the metadata of a registered microservice.
type ServiceInfo struct {
	Name     string            // Name of the service.
	Version  string            // Version of the service.
	Endpoint string            // The actual address of the microservice.
	Metadata map[string]string // Additional metadata provided during registration.
	ProxyPort int               // The port assigned to the proxy for this service.
}

// Registry is a thread-safe store for registered services.
type Registry struct {
	services map[string]*ServiceInfo // Map of service name to its information.
	mu       sync.RWMutex          // Mutex to protect access to the services map.
	portInUse map[int]bool          // Keep track of ports that are currently in use.
	portStart int                   // Starting port for dynamic allocation.
	nextPort  int                   // The next available port to assign.
}

// NewRegistry creates and initializes a new service registry.
func NewRegistry() *Registry {
	return &Registry{
		services:  make(map[string]*ServiceInfo),
		portInUse: make(map[int]bool),
	}
}

// SetPortRange sets the starting port for dynamic port allocation.
func (r *Registry) SetPortRange(startPort int) {
	r.portStart = startPort
	r.nextPort = startPort
}

// RegisterService adds a new service to the registry and assigns it a proxy port.
func (r *Registry) RegisterService(name, version, endpoint string, metadata map[string]string) (*ServiceInfo, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	serviceKey := fmt.Sprintf("%s-%s", name, version)
	if _, exists := r.services[serviceKey]; exists {
		return nil, fmt.Errorf("service with name '%s' and version '%s' already registered", name, version)
	}

	proxyPort, err := r.allocatePort()
	if err != nil {
		return nil, fmt.Errorf("failed to allocate port for service '%s': %v", name, err)
	}

	serviceInfo := &ServiceInfo{
		Name:     name,
		Version:  version,
		Endpoint: endpoint,
		Metadata: metadata,
		ProxyPort: proxyPort,
	}
	r.services[serviceKey] = serviceInfo
	return serviceInfo, nil
}

// DeregisterService removes a service from the registry and marks its port as available.
func (r *Registry) DeregisterService(name, version string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	serviceKey := fmt.Sprintf("%s-%s", name, version)
	serviceInfo, exists := r.services[serviceKey]
	if !exists {
		return fmt.Errorf("service with name '%s' and version '%s' not found", name, version)
	}

	delete(r.services, serviceKey)
	r.releasePort(serviceInfo.ProxyPort)
	return nil
}

// GetService retrieves the information for a specific service.
func (r *Registry) GetService(name, version string) (*ServiceInfo, bool) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	serviceKey := fmt.Sprintf("%s-%s", name, version)
	serviceInfo, exists := r.services[serviceKey]
	return serviceInfo, exists
}

// GetAllServices returns a snapshot of all registered services.
func (r *Registry) GetAllServices() map[string]*ServiceInfo {
	r.mu.RLock()
	defer r.mu.RUnlock()

	services := make(map[string]*ServiceInfo)
	for key, service := range r.services {
		services[key] = service
	}
	return services
}

// allocatePort finds and reserves a unique port for a service proxy.
func (r *Registry) allocatePort() (int, error) {
	if r.portStart == 0 {
		return 0, fmt.Errorf("port range not initialized")
	}

	for {
		port := r.nextPort
		r.nextPort++
		if r.nextPort > 65535 {
			r.nextPort = r.portStart // Wrap around if the range is exhausted (can be problematic in long run)
		}
		if !r.portInUse[port] {
			r.portInUse[port] = true
			return port, nil
		}
		if port == r.nextPort { // Avoid infinite loop if all ports in range are used
			return 0, fmt.Errorf("no available ports in the configured range")
		}
	}
}

// releasePort marks a port as no longer in use.
func (r *Registry) releasePort(port int) {
	delete(r.portInUse, port)
}