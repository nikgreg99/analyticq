package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func main() {
	// Configure logging
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	// Check staticcheck version
	cmd := exec.Command("staticcheck", "-version")
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Error checking staticcheck version: %v", err)
	}
	log.Printf("Staticcheck version: %s", string(output))

	// Define paths
	codePath := "/code"
	outputPath := "/output/staticcheck-report.json"

	// Check if /code directory exists and is not empty
	entries, err := os.ReadDir(codePath)
	if err != nil || len(entries) == 0 {
		log.Fatal("Directory /code is empty or not mounted correctly")
	}

	// Find all Go files
	var filesToScan []string
	err = filepath.Walk(codePath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && strings.HasSuffix(path, ".go") {
			filesToScan = append(filesToScan, path)
		}
		return nil
	})
	if err != nil {
		log.Fatalf("Error walking directory: %v", err)
	}

	// Check if it's a Go module
	if len(filesToScan) == 0 {
		log.Fatal("No valid Go files found in the directory")
	}

	log.Printf("Files to scan: %v", filesToScan)

	// Run staticcheck
	log.Println("Running staticcheck...")
	cmd = exec.Command("staticcheck", "-f", "json", codePath+"/...")
	cmd.Dir = codePath // Set working directory to the code path

	output, err = cmd.CombinedOutput()
	if err != nil {
		// Don't exit on linting errors, just log them
		log.Printf("Staticcheck completed with issues: %v", err)
	}

	// Ensure output directory exists
	err = os.MkdirAll(filepath.Dir(outputPath), 0755)
	if err != nil {
		log.Fatalf("Failed to create output directory: %v", err)
	}

	// Validate JSON output
	var jsonOutput interface{}
	if err := json.Unmarshal(output, &jsonOutput); err != nil {
		// If output is not JSON, create a JSON array with the raw output
		output = []byte(fmt.Sprintf("[{\"error\": %q}]", string(output)))
	}

	// Save output to file
	err = os.WriteFile(outputPath, output, 0644)
	if err != nil {
		log.Fatalf("Failed to write output file: %v", err)
	}
	log.Printf("Staticcheck output saved to %s", outputPath)

	// Always exit with 0 regardless of staticcheck findings
	os.Exit(0)
}
