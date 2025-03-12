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
	if err != nil || len(entries) == 0 {
		log.Fatal("Directory /code is empty or not mounted correctly")
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

	var args []string
	if os.IsNotExist(err) {
		log.Println("No go.mod file found, scanning all Go files in /code.")
		args = []string{"-fmt=json", "-out", outputPath, "-stdout", "./..."} // Scansiona tutto il codice in modo ricorsivo
	} else {
		log.Println("go.mod file found, scanning as Go module.")
		args = []string{"-fmt=json", "-out", outputPath, "-stdout", "./..."} // Scansiona come modulo Go
	}

	// Log the exact gosec command being executed
	log.Printf("Executing gosec command: gosec %s", strings.Join(args, " "))

	// Run gosec inside /code directory
	cmd = exec.Command("gosec", args...)
	cmd.Dir = codePath // Set working directory to the code path

	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Gosec completed with issues: %v", err)
	}

	// Log gosec output
	log.Printf("Gosec output: %s", string(output))
	log.Printf("Gosec report saved to %s", outputPath)

	// Always exit with 0 regardless of gosec findings
	os.Exit(0)
}
