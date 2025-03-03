package main

import (
	"encoding/json"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func main() {
	// Configure logging
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	// Define paths
	codePath := "/code"
	outputPath := "/output/govulncheck-report.json"

	// Check if /code directory exists and contains a Go file
	entries, err := os.ReadDir(codePath)
	if err != nil || len(entries) == 0 {
		log.Fatal("Directory /code is empty or not mounted correctly")
	}

	// Find the first Go file in the directory
	var goFile string
	for _, entry := range entries {
		if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".go") {
			goFile = entry.Name()
			break
		}
	}
	if goFile == "" {
		log.Fatal("No Go files found in the directory")
	}
	log.Printf("Go file to scan: %s", goFile)

	// Check if the directory is already a Go module
	goModPath := filepath.Join(codePath, "go.mod")
	_, err = os.Stat(goModPath)
	isModule := !os.IsNotExist(err)

	var analysisDir string
	if isModule {
		// Use the existing module
		log.Println("Using existing Go module for analysis.")
		analysisDir = codePath
	} else {
		// Create a temporary Go module
		log.Println("Creating temporary Go module...")
		tempModulePath := filepath.Join(codePath, "temp-module")
		err = os.Mkdir(tempModulePath, 0755)
		if err != nil {
			log.Fatalf("Failed to create temporary module directory: %v", err)
		}
		defer os.RemoveAll(tempModulePath) // Clean up the temporary directory

		// Copy the Go file to the temporary module directory
		tempGoFile := filepath.Join(tempModulePath, goFile)
		err = os.Rename(filepath.Join(codePath, goFile), tempGoFile)
		if err != nil {
			log.Fatalf("Failed to move Go file to temporary directory: %v", err)
		}

		// Initialize a temporary Go module
		cmd := exec.Command("go", "mod", "init", "temp-module")
		cmd.Dir = tempModulePath
		_, err = cmd.CombinedOutput()
		if err != nil {
			log.Fatalf("Failed to initialize temporary Go module: %v", err)
		}

		analysisDir = tempModulePath
	}

	// Run govulncheck
	log.Println("Running govulncheck...")
	cmd := exec.Command("govulncheck", "-json", "./...")
	cmd.Dir = analysisDir

	output, err := cmd.CombinedOutput()
	if err != nil {
		// Don't exit on vulnerabilities found, just log them
		log.Printf("govulncheck completed with issues: %v", err)
	}

	// Log the raw output for debugging
	log.Printf("Raw govulncheck output: %s", string(output))

	// Handle streaming JSON objects and convert to an array
	var jsonObjects []interface{}
	decoder := json.NewDecoder(strings.NewReader(string(output)))
	for decoder.More() {
		var obj interface{}
		if err := decoder.Decode(&obj); err != nil {
			log.Printf("Failed to decode JSON object: %v", err)
			continue
		}
		jsonObjects = append(jsonObjects, obj)
	}

	// Ensure output directory exists
	err = os.MkdirAll(filepath.Dir(outputPath), 0755)
	if err != nil {
		log.Fatalf("Failed to create output directory: %v", err)
	}

	// Marshal the JSON output
	compactOutput, err := json.Marshal(jsonObjects)
	if err != nil {
		log.Fatalf("Failed to marshal final JSON output: %v", err)
	}


	// Log the compact JSON output
	log.Println("Compact JSON output:")
	log.Println(string(compactOutput))

	// Save the output to a file
	err = os.WriteFile(outputPath, compactOutput, 0644)
	if err != nil {
		log.Fatalf("Failed to write output file: %v", err)
	}
	log.Printf("govulncheck output saved to %s", outputPath)

	// Always exit with 0 regardless of findings
	os.Exit(0)
}
