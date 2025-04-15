package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/resource-deployment/rds-sdk-go"
)

func main() {
	// Initialize the client with API key authentication
	client, err := rds.NewClient(rds.ClientOptions{
		BaseURL: "https://api.resourcedeployment.service/v1",
		APIKey:  "your-api-key-here",
	})
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}

	// Create a context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// List all resources
	resources, pagination, err := client.Resources.List(ctx, &rds.ResourceListOptions{
		Region: "us-west-1",
		Type:   "postgres",
		Limit:  10,
	})
	if err != nil {
		log.Fatalf("Failed to list resources: %v", err)
	}

	fmt.Printf("Found %d resources (page %d of %d)\n", 
		len(resources), 
		pagination.CurrentPage, 
		pagination.TotalPages)

	// Create a new PostgreSQL database
	pgConfig := &rds.PostgreSQLConfig{
		Version:     "13",
		StorageGB:   20,
		MemoryMB:    1024,
		CPUCores:    1,
		Replicas:    1,
		AdminUser:   "admin",
		DatabaseName: "myapp",
		Extensions:  []string{"pgcrypto", "uuid-ossp"},
	}

	createReq := &rds.ResourceCreateRequest{
		Name:   "sample-postgres",
		Type:   "postgres",
		Region: "us-west-1",
		Config: pgConfig,
	}

	newResource, err := client.Resources.Create(ctx, createReq)
	if err != nil {
		log.Fatalf("Failed to create resource: %v", err)
	}

	fmt.Printf("Created resource with ID: %s (status: %s)\n", 
		newResource.ID, 
		newResource.Status)

	// Deploy the resource
	deployJob, err := client.Resources.Deploy(ctx, newResource.ID)
	if err != nil {
		log.Fatalf("Failed to deploy resource: %v", err)
	}

	fmt.Printf("Deployment job started with ID: %s\n", deployJob.ID)

	// Poll for resource status
	for i := 0; i < 10; i++ {
		resource, err := client.Resources.Get(ctx, newResource.ID)
		if err != nil {
			log.Fatalf("Failed to get resource: %v", err)
		}

		fmt.Printf("Resource status: %s\n", resource.Status)
		if resource.Status == "running" {
			fmt.Println("Resource is now running!")
			break
		}

		if resource.Status == "failed" {
			fmt.Println("Resource deployment failed")
			break
		}

		// Wait before polling again
		time.Sleep(5 * time.Second)
	}

	// Get connection information
	connInfo, err := client.Resources.GetConnectionInfo(ctx, newResource.ID)
	if err != nil {
		log.Fatalf("Failed to get connection info: %v", err)
	}

	fmt.Printf("Host: %s\n", connInfo.Host)
	fmt.Printf("Port: %d\n", connInfo.Port)
	fmt.Printf("User: %s\n", connInfo.User)
	fmt.Printf("Database: %s\n", connInfo.Database)
	fmt.Printf("Use SSL: %t\n", connInfo.SSL)

	// Upload and obfuscate an environment file
	envFile := []byte(`
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=my-secure-password
DB_NAME=myapp
`)

	obfuscatedFile, err := client.EnvFiles.Obfuscate(ctx, &rds.EnvFileObfuscateRequest{
		Name:       "myapp.env",
		Content:    envFile,
		ResourceID: newResource.ID,
	})
	if err != nil {
		log.Fatalf("Failed to obfuscate environment file: %v", err)
	}

	fmt.Printf("Environment file obfuscated with ID: %s\n", obfuscatedFile.ID)

	// Download the obfuscated file
	fileContent, err := client.EnvFiles.Download(ctx, obfuscatedFile.ID)
	if err != nil {
		log.Fatalf("Failed to download obfuscated file: %v", err)
	}

	fmt.Printf("Downloaded obfuscated file (%d bytes)\n", len(fileContent))

	// Scale the resource
	scaleReq := &rds.ResourceScaleRequest{
		MemoryMB: 2048,
		CPUCores: 2,
	}

	scaleJob, err := client.Resources.Scale(ctx, newResource.ID, scaleReq)
	if err != nil {
		log.Fatalf("Failed to scale resource: %v", err)
	}

	fmt.Printf("Scale operation started with job ID: %s\n", scaleJob.ID)

	// Add an IP allowlist rule
	ipRule, err := client.Access.CreateIPRule(ctx, &rds.IPRuleCreateRequest{
		CIDR:        "192.168.1.0/24",
		Description: "Office network",
		ResourceIDs: []string{newResource.ID},
	})
	if err != nil {
		log.Fatalf("Failed to create IP rule: %v", err)
	}

	fmt.Printf("Created IP allowlist rule with ID: %s\n", ipRule.ID)

	// Get monitoring metrics
	metrics, err := client.Monitoring.GetResourceMetrics(ctx, newResource.ID, &rds.MetricsOptions{
		Metric:    "cpu",
		Timeframe: "1h",
	})
	if err != nil {
		log.Fatalf("Failed to get metrics: %v", err)
	}

	fmt.Printf("Retrieved %d metric data points\n", len(metrics.Datapoints))

	// Cleanup: delete the resource
	err = client.Resources.Delete(ctx, newResource.ID)
	if err != nil {
		log.Fatalf("Failed to delete resource: %v", err)
	}

	fmt.Println("Resource deleted successfully")
}