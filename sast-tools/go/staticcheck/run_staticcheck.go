package main

import (
	"encoding/json"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"bytes"
	"io"
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
	log.Printf("Staticcheck version: %s", strings.TrimSpace(string(output)))

	// Define paths
	codePath := "/code"
	outputPath := "/output/staticcheck-report.json"

	// Check if /code directory exists and is not empty
	entries, err := os.ReadDir(codePath)
	if err != nil {
		log.Fatalf("Error accessing code directory: %v", err)
	}
	if len(entries) == 0 {
		log.Fatal("Directory /code is empty")
	}

	// Find all Go files
	var filesToScan []string
	err = filepath.Walk(codePath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && strings.HasSuffix(path, ".go") {
			// Convert absolute path to relative path for better staticcheck output
			relPath, err := filepath.Rel(codePath, path)
			if err == nil {
				filesToScan = append(filesToScan, relPath)
			} else {
				filesToScan = append(filesToScan, path)
			}
		}
		return nil
	})
	if err != nil {
		log.Fatalf("Error walking directory: %v", err)
	}

	if len(filesToScan) == 0 {
		log.Fatal("No valid Go files found in the directory")
	}

	log.Printf("Found %d Go files to scan", len(filesToScan))

	// Check if it's a Go module
	goModPath := filepath.Join(codePath, "go.mod")
	_, err = os.Stat(goModPath)
	isModule := !os.IsNotExist(err)

	// Prepare command
	var args []string
	if isModule {
		log.Println("go.mod file found, scanning as Go module")
		args = []string{"-f", "json", "./..."}
		// Explicitly set GO111MODULE for consistent behavior
		os.Setenv("GO111MODULE", "on")
	} else {
		log.Println("No go.mod file found, scanning individual files")
		args = append([]string{"-f", "json"}, filesToScan...)
	}

	// Run staticcheck
	log.Printf("Running staticcheck with args: %v", args)
	cmd = exec.Command("staticcheck", args...)
	cmd.Dir = codePath

	// Capture stdout and stderr separately
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err = cmd.Run()
	if err != nil {
		log.Printf("Staticcheck command error: %v", err)
		log.Printf("Stderr: %s", stderr.String())
	}

	// Ensure output directory exists
	err = os.MkdirAll(filepath.Dir(outputPath), 0755)
	if err != nil {
		log.Fatalf("Failed to create output directory: %v", err)
	}

	// Check if we have any JSON output
	stdoutStr := stdout.String()
	if len(stdoutStr) == 0 {
		// No output - likely no issues found or command failed
		log.Println("No output from staticcheck, creating empty JSON array")
		err = os.WriteFile(outputPath, []byte("[]"), 0644)
		if err != nil {
			log.Fatalf("Failed to write empty output file: %v", err)
		}
		log.Printf("Empty staticcheck report saved to %s", outputPath)
		os.Exit(0)
	}

	// Process JSON output
	var jsonObjects []interface{}

	// Log sample of output for debugging
	if len(stdoutStr) > 100 {
		log.Printf("First 100 chars of stdout: %s...", stdoutStr[:100])
	} else {
		log.Printf("Complete stdout: %s", stdoutStr)
	}

	// Try to decode each line as separate JSON object
	decoder := json.NewDecoder(strings.NewReader(stdoutStr))
	for {
		var obj interface{}
		err := decoder.Decode(&obj)
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Printf("Failed to decode JSON object: %v", err)
			// Skip to next line to try to recover
			buffer := make([]byte, 1024)
			_, err = decoder.Buffered().Read(buffer)
			decoder = json.NewDecoder(strings.NewReader(stdoutStr[decoder.InputOffset():]))
			continue
		}
		jsonObjects = append(jsonObjects, obj)
	}

	// If parsing failed completely, write the raw output for investigation
	if len(jsonObjects) == 0 {
		log.Println("Failed to parse any JSON objects, saving raw output for debugging")
		debugPath := outputPath + ".debug"
		err = os.WriteFile(debugPath, stdout.Bytes(), 0644)
		if err != nil {
			log.Printf("Failed to write debug file: %v", err)
		} else {
			log.Printf("Raw output saved to %s for debugging", debugPath)
		}

		// Still write an empty JSON array as the official output
		err = os.WriteFile(outputPath, []byte("[]"), 0644)
		if err != nil {
			log.Fatalf("Failed to write empty output file: %v", err)
		}
	} else {
		// Successfully parsed some objects
		finalOutput, err := json.MarshalIndent(jsonObjects, "", "  ")
		if err != nil {
			log.Fatalf("Failed to marshal final JSON output: %v", err)
		}

		err = os.WriteFile(outputPath, finalOutput, 0644)
		if err != nil {
			log.Fatalf("Failed to write output file: %v", err)
		}
		log.Printf("Staticcheck output with %d issues saved to %s", len(jsonObjects), outputPath)
	}

	// Always exit with 0 regardless of staticcheck findings
	os.Exit(0)
}
