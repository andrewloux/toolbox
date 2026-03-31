// Package testutil provides a fluent test harness for Chronos integration tests.
//
// Example usage:
//
//	func TestDeploy(t *testing.T) {
//	    h := testutil.New(t)
//
//	    result := h.Run(
//	        h.Start("Build"),
//	        h.Exec("Compile").Cmd("go", "build", "."),
//	        h.End("Build"),
//	    )
//
//	    result.MustSucceed()
//	    result.Task("Build").MustSucceed()
//	}
package testutil

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"testing"
	"time"
)

var (
	binaryOnce sync.Once
	binaryPath string
	buildErr   error
)

// Harness provides a fluent API for building and running Chronos integration tests.
type Harness struct {
	t       *testing.T
	timeout time.Duration
	env     []string
	noColor bool
}

// New creates a new test harness. It automatically builds the Chronos binary
// once per test run.
func New(t *testing.T) *Harness {
	t.Helper()

	binaryOnce.Do(func() {
		binaryPath, buildErr = buildBinary()
	})

	if buildErr != nil {
		t.Fatalf("failed to build chronos binary: %v", buildErr)
	}

	return &Harness{
		t:       t,
		timeout: 30 * time.Second,
		noColor: true, // Default to no-color for easier parsing
	}
}

func buildBinary() (string, error) {
	tmpDir, err := os.MkdirTemp("", "chronos-test-*")
	if err != nil {
		return "", err
	}

	binary := filepath.Join(tmpDir, "chronos")
	cmd := exec.Command("go", "build", "-o", binary, "./cmd/chronos")
	cmd.Dir = findProjectRoot()

	if out, err := cmd.CombinedOutput(); err != nil {
		return "", &BuildError{Output: string(out), Err: err}
	}

	return binary, nil
}

func findProjectRoot() string {
	dir, _ := os.Getwd()
	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "."
		}
		dir = parent
	}
}

// BuildError is returned when the Chronos binary fails to build.
type BuildError struct {
	Output string
	Err    error
}

func (e *BuildError) Error() string {
	return "build failed: " + e.Err.Error() + "\n" + e.Output
}

// WithTimeout sets the maximum duration for script execution.
func (h *Harness) WithTimeout(d time.Duration) *Harness {
	h.timeout = d
	return h
}

// WithEnv adds an environment variable for script execution.
func (h *Harness) WithEnv(key, value string) *Harness {
	h.env = append(h.env, key+"="+value)
	return h
}

// WithColor enables colored output (disabled by default for easier parsing).
func (h *Harness) WithColor() *Harness {
	h.noColor = false
	return h
}

// Run executes a script composed of the given operations and returns
// a parsed result for assertions.
func (h *Harness) Run(ops ...Op) *Result {
	h.t.Helper()

	// Build script
	var script strings.Builder
	script.WriteString("#!/bin/bash\n")
	script.WriteString("set +e\n") // Don't exit on error by default

	for _, op := range ops {
		script.WriteString(op.Render(binaryPath))
		script.WriteString("\n")
	}

	// Write script to temp file
	tmpDir := h.t.TempDir()
	scriptPath := filepath.Join(tmpDir, "test.sh")
	if err := os.WriteFile(scriptPath, []byte(script.String()), 0755); err != nil {
		h.t.Fatalf("failed to write script: %v", err)
	}

	// Build command
	args := []string{"run"}
	if h.noColor {
		args = append(args, "--no-color")
	}
	args = append(args, scriptPath)

	cmd := exec.Command(binaryPath, args...)
	cmd.Env = append(os.Environ(), h.env...)
	cmd.Env = append(cmd.Env, "TERM=dumb")

	// Run with timeout
	done := make(chan error, 1)
	var output []byte

	go func() {
		var err error
		output, err = cmd.CombinedOutput()
		done <- err
	}()

	var exitCode int
	var runErr error

	select {
	case err := <-done:
		runErr = err
		if exitErr, ok := err.(*exec.ExitError); ok {
			exitCode = exitErr.ExitCode()
		}
	case <-time.After(h.timeout):
		cmd.Process.Kill()
		h.t.Fatalf("script timed out after %v", h.timeout)
	}

	return parseResult(h.t, string(output), exitCode, runErr, script.String())
}

// Operation builders - these create Op instances for use with Run()

// Start creates a "chronos start <name>" operation.
func (h *Harness) Start(name string) Op {
	return &startOp{name: name}
}

// End creates a "chronos end [name]" operation.
func (h *Harness) End(name ...string) Op {
	op := &endOp{}
	if len(name) > 0 {
		op.name = name[0]
	}
	return op
}

// Fail creates a "chronos fail [name]" operation.
func (h *Harness) Fail(name ...string) Op {
	op := &failOp{}
	if len(name) > 0 {
		op.name = name[0]
	}
	return op
}

// Log creates a "chronos log <message>" operation.
func (h *Harness) Log(message string) Op {
	return &logOp{message: message}
}

// Exec creates a "chronos exec" operation. Use .Cmd() to set the command.
func (h *Harness) Exec(name ...string) *ExecOp {
	op := &ExecOp{}
	if len(name) > 0 {
		op.name = name[0]
	}
	return op
}

// Shell creates a raw shell command (not a chronos command).
func (h *Harness) Shell(command string) Op {
	return &shellOp{command: command}
}

// Sleep creates a sleep command.
func (h *Harness) Sleep(d time.Duration) Op {
	return &shellOp{command: fmt.Sprintf("sleep %.3f", d.Seconds())}
}

// Echo creates an echo command (for script output, not chronos log).
func (h *Harness) Echo(message string) Op {
	return &shellOp{command: "echo " + shellQuote(message)}
}
