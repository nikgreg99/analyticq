package main

import (
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
	outputPath := "/output/gosec-report.json"

	// Check if /code directory exists and is not empty
	entries, err := os.ReadDir(codePath)
	if err != nil {
		log.Fatalf("Error accessing /code directory: %v", err)
	}
	if len(entries) == 0 {
		log.Fatal("Directory /code is empty")
	}

	// Check gosec version
	cmd := exec.Command("gosec", "-version")
	versionOutput, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Error checking gosec version: %v", err)
	} else {
		log.Printf("Gosec version: %s", strings.TrimSpace(string(versionOutput)))
	}

	// Determine if it's a Go module
	goModPath := filepath.Join(codePath, "go.mod")
	_, err = os.Stat(goModPath)

	// Prepare command arguments
	args := []string{"-fmt=json", "-out", outputPath}

	// Add stdout flag only if needed
	if os.Getenv("PRINT_STDOUT") == "true" {
		args = append(args, "-stdout")
	}

	// Scan based on module presence
	if os.IsNotExist(err) {
		log.Println("No go.mod file found, scanning all Go files in /code")
		// For non-module mode, specific file patterns may work better
		args = append(args, "./...")
	} else {
		log.Println("go.mod file found, scanning as Go module")
		// For module mode, let's make sure we're in the right context
		os.Setenv("GO111MODULE", "on")
		args = append(args, "./...")
	}

	// Log the exact gosec command being executed
	log.Printf("Executing gosec command: gosec %s", strings.Join(args, " "))

	// Run gosec inside /code directory
	cmd = exec.Command("gosec", args...)
	cmd.Dir = codePath
	cmd.Stdout = os.Stdout // Show stdout directly
	cmd.Stderr = os.Stderr // Show stderr directly

	err = cmd.Run()
	if err != nil {
		log.Printf("Gosec completed with issues: %v", err)
	}

	// Verify output file exists
	if _, err := os.Stat(outputPath); os.IsNotExist(err) {
		log.Printf("Warning: Output file %s was not created", outputPath)
	} else {
		log.Printf("Gosec report saved to %s", outputPath)
	}

	// Always exit with 0 regardless of gosec findings
	os.Exit(0)
}
