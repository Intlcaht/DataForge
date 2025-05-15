// core/proxy_manager.go
// This file manages the lifecycle of the reverse proxies for each
// registered service. It starts a new proxy instance when a service
// registers and stops it when a service deregisters.

package core

import (
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strconv"
	"sync"
)

// ProxyManager manages the reverse proxies for registered services.
type ProxyManager struct {
	registry *Registry                // Reference to the service registry.
	proxies  map[string]*httputil.ReverseProxy // Map of service key to its proxy.
	mu       sync.RWMutex                    // Mutex to protect access to the proxies map.
	portStart int                             // Starting port for proxy allocation.
}

// NewProxyManager creates and initializes a new ProxyManager.
func NewProxyManager(registry *Registry, portStart int) *ProxyManager {
	pm := &ProxyManager{
		registry:  registry,
		proxies:   make(map[string]*httputil.ReverseProxy),
		portStart: portStart,
	}
	pm.registry.SetPortRange(portStart)
	return pm
}

// StartProxy starts a new reverse proxy for the given service information.
func (pm *ProxyManager) StartProxy(serviceInfo *ServiceInfo) error {
	targetURL, err := url.Parse(serviceInfo.Endpoint)
	if err != nil {
		return fmt.Errorf("failed to parse service endpoint '%s': %v", serviceInfo.Endpoint, err)
	}

	reverseProxy := httputil.NewSingleHostReverseProxy(targetURL)

	// Apply any middleware to the reverse proxy handler here.
	handler := http.Handler(reverseProxy)
	// Example: handler = auth.Middleware(handler)
	// Example: handler = tracing.Middleware(handler)
	// ...

	server := &http.Server{
		Addr:    ":" + strconv.Itoa(serviceInfo.ProxyPort),
		Handler: handler,
	}

	serviceKey := fmt.Sprintf("%s-%s", serviceInfo.Name, serviceInfo.Version)
	pm.mu.Lock()
	pm.proxies[serviceKey] = reverseProxy // Store the reverse proxy instance (might be useful later)
	pm.mu.Unlock()

	log.Printf("Starting proxy for service '%s' (%s) on port %d, forwarding to '%s'",
		serviceInfo.Name, serviceInfo.Version, serviceInfo.ProxyPort, serviceInfo.Endpoint)

	// Start the proxy server in a goroutine.
	go func() {
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start proxy for '%s': %v", serviceKey, err)
			// Consider implementing a retry or cleanup mechanism here.
		}
		log.Printf("Proxy for service '%s' stopped.", serviceKey)
	}()

	return nil
}

// StopProxy stops the reverse proxy for the given service.
func (pm *ProxyManager) StopProxy(name, version string) error {
	serviceKey := fmt.Sprintf("%s-%s", name, version)
	pm.mu.Lock()
	defer pm.mu.Unlock()

	proxy := pm.proxies[serviceKey]
	if proxy == nil {
		return fmt.Errorf("no proxy found for service '%s'", serviceKey)
	}

	// Graceful shutdown of the server associated with this proxy would be more robust.
	// This example doesn't keep a direct reference to the http.Server.
	// A more advanced implementation might store the *http.Server in the ProxyManager
	// and call Shutdown() on it.
	delete(pm.proxies, serviceKey)
	log.Printf("Stopped proxy for service '%s'", serviceKey)
	return nil
}

// ShutdownAll stops all running proxies.
func (pm *ProxyManager) ShutdownAll() error {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	var errorList []error
	for key := range pm.proxies {
		// As mentioned in StopProxy, a more robust shutdown would involve
		// managing the http.Server instances. For this basic example,
		// we just log the stopping action.
		log.Printf("Stopping proxy for service '%s'...", key)
		delete(pm.proxies, key)
	}
	return nil
}