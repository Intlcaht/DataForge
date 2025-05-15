// main.go
// This is the entry point of the Icaht Sidecar application.
// It initializes the necessary components, loads the configuration,
// and starts the main processes, including the API server for
// service registration and the core proxy management.

package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/intlcaht/icaht-sidecar/configuration" // Import configuration package
	"github.com/intlcaht/icaht-sidecar/core"          // Import core logic package
)

func main() {
	// Load the application configuration.
	// This reads settings from environment variables or configuration files.
	cfg, err := configuration.Load()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}
	log.Printf("Configuration loaded successfully: %+v", cfg)

	// Initialize the service registry.
	// This component will store information about registered microservices.
	registry := core.NewRegistry()
	log.Println("Service registry initialized.")

	// Initialize the proxy manager.
	// This component is responsible for creating and managing the lifecycle
	// of the individual service proxies. It needs a reference to the registry
	// to know which services to proxy.
	proxyManager := core.NewProxyManager(registry, cfg.ProxyPortRangeStart)
	log.Println("Proxy manager initialized.")

	// Start the API server for service registration.
	// This server listens for incoming HTTP requests from microservices
	// that want to register themselves with the sidecar.
	registrationServer := &http.Server{
		Addr:    fmt.Sprintf(":%d", cfg.RegistrationPort),
		Handler: core.NewRegistrationHandler(registry, proxyManager), // Handler for registration requests
	}

	// Start the registration server in a goroutine so it doesn't block
	// the main thread. This allows other processes to run concurrently.
	go func() {
		log.Printf("Starting service registration API server on port %d", cfg.RegistrationPort)
		if err := registrationServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start registration server: %v", err)
		}
	}()

	// Set up signal handling for graceful shutdown.
	// This listens for OS signals like SIGINT (Ctrl+C) and SIGTERM (Docker stop).
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	// Block until a signal is received.
	<-quit
	log.Println("Received shutdown signal. Shutting down...")

	// Perform graceful shutdown of the registration server.
	// This gives the server a chance to finish any in-flight requests
	// before exiting.
	if err := registrationServer.Shutdown(nil); err != nil {
		log.Fatalf("Registration server shutdown failed: %v", err)
	}
	log.Println("Service registration API server stopped.")

	// Perform any other cleanup operations here, like stopping the
	// proxy manager and any other background processes.
	if err := proxyManager.ShutdownAll(); err != nil {
		log.Printf("Proxy manager shutdown encountered errors: %v", err)
	}
	log.Println("Proxy manager stopped.")

	log.Println("Icaht Sidecar stopped gracefully.")
}