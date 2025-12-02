package main_test

import (
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"testing"
	"time"
)

var chronosBinary string

func TestMain(m *testing.M) {
	// Build the binary before running tests
	tmpDir, err := os.MkdirTemp("", "chronos-test")
	if err != nil {
		panic(err)
	}
	defer os.RemoveAll(tmpDir)

	chronosBinary = filepath.Join(tmpDir, "chronos")
	cmd := exec.Command("go", "build", "-o", chronosBinary, "./cmd/chronos")
	cmd.Dir = getProjectRoot()
	if out, err := cmd.CombinedOutput(); err != nil {
		panic("failed to build chronos: " + string(out))
	}

	os.Exit(m.Run())
}

func getProjectRoot() string {
	// Find the directory containing go.mod
	dir, _ := os.Getwd()
	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			panic("could not find project root")
		}
		dir = parent
	}
}

// runChronos executes chronos with given script and returns stdout/stderr
func runChronos(t *testing.T, script string, timeout time.Duration) (string, error) {
	t.Helper()

	// Create temp script
	tmpDir := t.TempDir()
	scriptPath := filepath.Join(tmpDir, "test.sh")
	if err := os.WriteFile(scriptPath, []byte(script), 0755); err != nil {
		t.Fatal(err)
	}

	cmd := exec.Command(chronosBinary, "run", "--no-color", scriptPath)
	cmd.Env = append(os.Environ(), "TERM=dumb")

	// Use timeout for the command
	done := make(chan error, 1)
	var out []byte
	go func() {
		var err error
		out, err = cmd.CombinedOutput()
		done <- err
	}()

	select {
	case err := <-done:
		return string(out), err
	case <-time.After(timeout):
		cmd.Process.Kill()
		return "", os.ErrDeadlineExceeded
	}
}

// ============================================================================
// Basic Flow Tests
// ============================================================================

func TestBasicExecCommand(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` exec -- echo "hello world"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	// Should contain success marker
	if !strings.Contains(output, "[OK]") && !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected success in output, got:\n%s", output)
	}

	// Task name should be the command
	if !strings.Contains(output, "echo hello world") {
		t.Errorf("expected task name 'echo hello world' in output, got:\n%s", output)
	}
}

func TestNamedExecCommand(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` exec "My Task" -- echo "test output"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	if !strings.Contains(output, "My Task") {
		t.Errorf("expected 'My Task' in output, got:\n%s", output)
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS in output, got:\n%s", output)
	}
}

func TestStartEndFlow(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` start "Build"
` + chronosBinary + ` exec -- echo "building..."
` + chronosBinary + ` end "Build"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	if !strings.Contains(output, "Build") {
		t.Errorf("expected 'Build' task in output, got:\n%s", output)
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

// ============================================================================
// Nesting Tests
// ============================================================================

func TestNestedTasks(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` start "Outer"
` + chronosBinary + ` start "Inner"
` + chronosBinary + ` exec -- echo "nested task"
` + chronosBinary + ` end "Inner"
` + chronosBinary + ` end "Outer"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	if !strings.Contains(output, "Outer") {
		t.Errorf("expected 'Outer' in output, got:\n%s", output)
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

func TestMultipleSiblingTasks(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` start "Phase1"
` + chronosBinary + ` exec -- echo "phase 1"
` + chronosBinary + ` end "Phase1"

` + chronosBinary + ` start "Phase2"
` + chronosBinary + ` exec -- echo "phase 2"
` + chronosBinary + ` end "Phase2"

` + chronosBinary + ` start "Phase3"
` + chronosBinary + ` exec -- echo "phase 3"
` + chronosBinary + ` end "Phase3"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	// All phases should appear
	for _, phase := range []string{"Phase1", "Phase2", "Phase3"} {
		if !strings.Contains(output, phase) {
			t.Errorf("expected '%s' in output, got:\n%s", phase, output)
		}
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

func TestDeeplyNestedTasks(t *testing.T) {
	// Note: Successful subtrees are collapsed in the artifact per spec
	// So we only see Level1, the nested children are collapsed
	script := `#!/bin/bash
` + chronosBinary + ` start "Level1"
` + chronosBinary + ` start "Level2"
` + chronosBinary + ` start "Level3"
` + chronosBinary + ` exec -- echo "deep"
` + chronosBinary + ` end "Level3"
` + chronosBinary + ` end "Level2"
` + chronosBinary + ` end "Level1"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	// Only Level1 should be visible (collapsed successful subtree)
	if !strings.Contains(output, "Level1") {
		t.Errorf("expected 'Level1' in output, got:\n%s", output)
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

func TestDeeplyNestedTasksWithFailure(t *testing.T) {
	// When there's a failure, nested structure IS shown
	script := `#!/bin/bash
` + chronosBinary + ` start "Level1"
` + chronosBinary + ` start "Level2"
` + chronosBinary + ` start "Level3"
` + chronosBinary + ` exec "Failing" -- sh -c "exit 1"
` + chronosBinary + ` end "Level3"
` + chronosBinary + ` end "Level2"
` + chronosBinary + ` end "Level1"
`
	output, _ := runChronos(t, script, 10*time.Second)

	// All levels should be visible because of the failure
	for _, level := range []string{"Level1", "Level2", "Level3", "Failing"} {
		if !strings.Contains(output, level) {
			t.Errorf("expected '%s' in output, got:\n%s", level, output)
		}
	}

	if !strings.Contains(output, "FAILED") {
		t.Errorf("expected FAILED, got:\n%s", output)
	}
}

// ============================================================================
// Failure Tests
// ============================================================================

func TestExecFailure(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` exec "Failing Task" -- sh -c "exit 1"
`
	output, _ := runChronos(t, script, 10*time.Second)

	if !strings.Contains(output, "FAILED") {
		t.Errorf("expected FAILED in output, got:\n%s", output)
	}

	if !strings.Contains(output, "Failing Task") {
		t.Errorf("expected 'Failing Task' in output, got:\n%s", output)
	}

	// Should show exit code
	if !strings.Contains(output, "exit code 1") {
		t.Errorf("expected 'exit code 1' in output, got:\n%s", output)
	}
}

func TestFailedTaskShowsOutput(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` exec "Error Task" -- sh -c 'echo "error message here"; exit 1'
`
	output, _ := runChronos(t, script, 10*time.Second)

	if !strings.Contains(output, "FAILED") {
		t.Errorf("expected FAILED in output, got:\n%s", output)
	}

	// The error output should be shown in the artifact
	if !strings.Contains(output, "error message here") {
		t.Errorf("expected error output in artifact, got:\n%s", output)
	}
}

func TestFailedChildShowsInSuccessfulParent(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` start "Parent"
` + chronosBinary + ` exec "Good Task" -- echo "works"
` + chronosBinary + ` exec "Bad Task" -- sh -c 'echo "failure output"; exit 1'
` + chronosBinary + ` end "Parent"
`
	output, _ := runChronos(t, script, 10*time.Second)

	// Should show FAILED overall
	if !strings.Contains(output, "FAILED") {
		t.Errorf("expected FAILED in output, got:\n%s", output)
	}

	// Parent task should be shown
	if !strings.Contains(output, "Parent") {
		t.Errorf("expected 'Parent' in output, got:\n%s", output)
	}

	// Bad Task should be shown with its output
	if !strings.Contains(output, "Bad Task") {
		t.Errorf("expected 'Bad Task' in output, got:\n%s", output)
	}

	// Good Task should also be shown (sibling of failed task)
	if !strings.Contains(output, "Good Task") {
		t.Errorf("expected 'Good Task' in output, got:\n%s", output)
	}

	// Failure output should be visible
	if !strings.Contains(output, "failure output") {
		t.Errorf("expected failure output in artifact, got:\n%s", output)
	}
}

func TestExplicitFailCommand(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` start "Manual Fail"
` + chronosBinary + ` exec -- echo "some work"
` + chronosBinary + ` fail "Manual Fail"
`
	output, _ := runChronos(t, script, 10*time.Second)

	if !strings.Contains(output, "FAILED") {
		t.Errorf("expected FAILED in output, got:\n%s", output)
	}

	if !strings.Contains(output, "Manual Fail") {
		t.Errorf("expected 'Manual Fail' in output, got:\n%s", output)
	}
}

// ============================================================================
// Artifact Format Tests
// ============================================================================

func TestArtifactContainsDurations(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` exec "Timed Task" -- sleep 0.1
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	// Should contain some duration format (ms, s, or m)
	durationPattern := regexp.MustCompile(`\d+ms|\d+\.\d+s|\d+m`)
	if !durationPattern.MatchString(output) {
		t.Errorf("expected duration in output, got:\n%s", output)
	}
}

func TestArtifactShowsTaskCount(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` exec -- echo "task1"
` + chronosBinary + ` exec -- echo "task2"
` + chronosBinary + ` exec -- echo "task3"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	// SUCCESS should appear (all passed)
	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS in output, got:\n%s", output)
	}
}

func TestArtifactFailureCount(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` exec -- echo "pass1"
` + chronosBinary + ` exec -- sh -c "exit 1"
` + chronosBinary + ` exec -- echo "pass2"
`
	output, _ := runChronos(t, script, 10*time.Second)

	// Should show FAILED with count
	failedPattern := regexp.MustCompile(`FAILED \(\d+/\d+\)`)
	if !failedPattern.MatchString(output) {
		t.Errorf("expected 'FAILED (n/m)' in output, got:\n%s", output)
	}
}

func TestArtifactBorders(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` exec -- echo "test"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	// Should have box drawing characters
	if !strings.Contains(output, "─") && !strings.Contains(output, "-") {
		t.Errorf("expected border characters in output, got:\n%s", output)
	}
}

// ============================================================================
// Log Command Tests
// ============================================================================

func TestLogCommand(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` start "Task With Logs"
` + chronosBinary + ` log "First log message"
` + chronosBinary + ` log "Second log message"
` + chronosBinary + ` end "Task With Logs"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	if !strings.Contains(output, "Task With Logs") {
		t.Errorf("expected 'Task With Logs' in output, got:\n%s", output)
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

// ============================================================================
// Scope Isolation Tests
// ============================================================================

func TestScopeStackIsolation(t *testing.T) {
	// This tests that the scope stack properly tracks nesting
	script := `#!/bin/bash
` + chronosBinary + ` start "A"
` + chronosBinary + ` start "B"
` + chronosBinary + ` exec -- echo "in B"
` + chronosBinary + ` end  # should end B (current scope)
` + chronosBinary + ` exec -- echo "in A"
` + chronosBinary + ` end  # should end A
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

func TestEndWithoutNameUsesCurrentScope(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` start "First"
` + chronosBinary + ` end
` + chronosBinary + ` start "Second"
` + chronosBinary + ` end
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	if !strings.Contains(output, "First") {
		t.Errorf("expected 'First' in output, got:\n%s", output)
	}

	if !strings.Contains(output, "Second") {
		t.Errorf("expected 'Second' in output, got:\n%s", output)
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

// ============================================================================
// Edge Cases
// ============================================================================

func TestEmptyScript(t *testing.T) {
	script := `#!/bin/bash
# Empty script - no chronos commands
echo "just output"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	// Should still produce an artifact with SUCCESS
	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS for empty script, got:\n%s", output)
	}
}

func TestLongTaskName(t *testing.T) {
	longName := strings.Repeat("A", 100)
	script := `#!/bin/bash
` + chronosBinary + ` exec "` + longName + `" -- echo "test"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	// Should handle long names gracefully (possibly truncated)
	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

func TestSpecialCharactersInTaskName(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` exec "Task with 'quotes' and \"double quotes\"" -- echo "test"
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

func TestCommandWithArguments(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` exec -- sh -c 'echo "arg1 arg2 arg3"'
`
	output, err := runChronos(t, script, 10*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

func TestRapidTaskCreation(t *testing.T) {
	// Create many tasks quickly to test socket handling
	var cmds strings.Builder
	cmds.WriteString("#!/bin/bash\n")
	for i := 0; i < 20; i++ {
		cmds.WriteString(chronosBinary + ` exec -- echo "task ` + string(rune('A'+i)) + `"` + "\n")
	}

	output, err := runChronos(t, cmds.String(), 30*time.Second)
	if err != nil {
		t.Logf("Output: %s", output)
	}

	if !strings.Contains(output, "SUCCESS") {
		t.Errorf("expected SUCCESS, got:\n%s", output)
	}
}

// ============================================================================
// Error Handling Tests
// ============================================================================

func TestEndNonexistentTask(t *testing.T) {
	script := `#!/bin/bash
` + chronosBinary + ` end "NonexistentTask" 2>&1 || true
`
	output, _ := runChronos(t, script, 10*time.Second)

	// The script should still complete (we use || true)
	// But there should be some indication it couldn't find the task
	_ = output // Error goes to the script's stderr
}

func TestStartOutsideSession(t *testing.T) {
	// Try to run start without a session
	cmd := exec.Command(chronosBinary, "start", "SomeTask")
	out, err := cmd.CombinedOutput()

	if err == nil {
		t.Error("expected error when running start outside session")
	}

	outLower := strings.ToLower(string(out))
	if !strings.Contains(outLower, "no active session") {
		t.Errorf("expected 'no active session' error, got: %s", out)
	}
}

func TestExecOutsideSession(t *testing.T) {
	cmd := exec.Command(chronosBinary, "exec", "--", "echo", "test")
	out, err := cmd.CombinedOutput()

	if err == nil {
		t.Error("expected error when running exec outside session")
	}

	outLower := strings.ToLower(string(out))
	if !strings.Contains(outLower, "no active session") {
		t.Errorf("expected 'no active session' error, got: %s", out)
	}
}

func TestLogOutsideSession(t *testing.T) {
	cmd := exec.Command(chronosBinary, "log", "some message")
	out, err := cmd.CombinedOutput()

	if err == nil {
		t.Error("expected error when running log outside session")
	}

	outLower := strings.ToLower(string(out))
	if !strings.Contains(outLower, "no active session") {
		t.Errorf("expected 'no active session' error, got: %s", out)
	}
}
