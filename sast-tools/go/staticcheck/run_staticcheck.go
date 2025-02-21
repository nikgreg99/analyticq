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

	goModPath := filepath.Join(codePath, "go.mod")
	_, err = os.Stat(goModPath)

	var args []string
	if os.IsNotExist(err) {
		log.Println("No go.mod file found, scanning individual files.")
		args = append([]string{"-f", "json"}, filesToScan...)
	} else {
		log.Println("go.mod file found, scanning as Go module.")
		args = []string{"-f", "json", "./..."}
	}

	// Run staticcheck
	log.Println("Running staticcheck...")
	cmd = exec.Command("staticcheck", args...)
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

	finalOutput, err := json.MarshalIndent(jsonObjects, "", "  ")
	if err != nil {
		log.Fatalf("Failed to marshal final JSON output: %v", err)
	}

	err = os.WriteFile(outputPath, finalOutput, 0644)
	if err != nil {
		log.Fatalf("Failed to write output file: %v", err)
	}
	log.Printf("Staticcheck output saved to %s", outputPath)
	log.Printf("Print final %s", finalOutput)

	// Always exit with 0 regardless of staticcheck findings
	os.Exit(0)
}
