package main_test

import (
	"os"
	"os/exec"
	"strings"
	"testing"
	"time"

	"github.com/andrewloux/toolbox/chronos/testutil"
)

// ============================================================================
// Basic Flow Tests
// ============================================================================

func TestBasicExecCommand(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec().Cmd("echo", "hello world"),
	)

	result.MustSucceed()
	result.MustContain("echo hello world") // Task name is the command
}

func TestNamedExecCommand(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec("My Task").Cmd("echo", "test output"),
	)

	result.MustSucceed()
	result.MustHaveTask("My Task")
	result.Task("My Task").MustSucceed()
}

func TestStartEndFlow(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Start("Build"),
		h.Exec().Cmd("echo", "building..."),
		h.End("Build"),
	)

	result.MustSucceed()
	result.MustHaveTask("Build")
	result.Task("Build").MustSucceed()
}

func TestMultipleExecCommands(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec("Task1").Cmd("echo", "one"),
		h.Exec("Task2").Cmd("echo", "two"),
		h.Exec("Task3").Cmd("echo", "three"),
	)

	result.MustSucceed()
	result.MustHaveTask("Task1")
	result.MustHaveTask("Task2")
	result.MustHaveTask("Task3")
}

// ============================================================================
// Nesting Tests
// ============================================================================

func TestNestedTasks(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Start("Outer"),
		h.Start("Inner"),
		h.Exec("DeepTask").Cmd("echo", "nested"),
		h.End("Inner"),
		h.End("Outer"),
	)

	result.MustSucceed()
	result.MustHaveTask("Outer")
}

func TestMultipleSiblingTasks(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Start("Phase1"),
		h.Exec().Cmd("echo", "phase 1"),
		h.End("Phase1"),

		h.Start("Phase2"),
		h.Exec().Cmd("echo", "phase 2"),
		h.End("Phase2"),

		h.Start("Phase3"),
		h.Exec().Cmd("echo", "phase 3"),
		h.End("Phase3"),
	)

	result.MustSucceed()
	result.MustHaveTask("Phase1")
	result.MustHaveTask("Phase2")
	result.MustHaveTask("Phase3")
}

func TestDeeplyNestedTasks(t *testing.T) {
	h := testutil.New(t)

	// Successful subtrees are collapsed in artifact
	result := h.Run(
		h.Start("Level1"),
		h.Start("Level2"),
		h.Start("Level3"),
		h.Exec().Cmd("echo", "deep"),
		h.End("Level3"),
		h.End("Level2"),
		h.End("Level1"),
	)

	result.MustSucceed()
	result.MustHaveTask("Level1")
}

func TestDeeplyNestedTasksWithFailure(t *testing.T) {
	h := testutil.New(t)

	// When there's a failure, nested structure IS shown
	result := h.Run(
		h.Start("Level1"),
		h.Start("Level2"),
		h.Start("Level3"),
		h.Exec("Failing").CmdString("exit 1"),
		h.End("Level3"),
		h.End("Level2"),
		h.End("Level1"),
	)

	result.MustFail()
	result.MustHaveTask("Level1")
	result.MustHaveTask("Level2")
	result.MustHaveTask("Level3")
	result.MustHaveTask("Failing")
	result.Task("Failing").MustFail()
}

// ============================================================================
// Failure Tests
// ============================================================================

func TestExecFailure(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec("Failing Task").CmdString("exit 1"),
	)

	result.MustFail()
	result.Task("Failing Task").MustFail().MustHaveExitCode(1)
}

func TestFailedTaskShowsOutput(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec("Error Task").CmdString("echo 'error message here'; exit 1"),
	)

	result.MustFail()
	result.Task("Error Task").MustFail().MustShowOutput("error message here")
}

func TestFailedChildShowsInSuccessfulParent(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Start("Parent"),
		h.Exec("Good Task").Cmd("echo", "works"),
		h.Exec("Bad Task").CmdString("echo 'failure output'; exit 1"),
		h.End("Parent"),
	)

	result.MustFail()
	result.MustHaveTask("Parent")
	result.MustHaveTask("Good Task")
	result.MustHaveTask("Bad Task")
	result.Task("Bad Task").MustFail().MustShowOutput("failure output")
}

func TestExplicitFailCommand(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Start("Manual Fail"),
		h.Exec().Cmd("echo", "some work"),
		h.Fail("Manual Fail"),
	)

	result.MustFail()
	result.Task("Manual Fail").MustFail()
}

func TestMultipleFailures(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec("Fail1").CmdString("exit 1"),
		h.Exec("Fail2").CmdString("exit 2"),
		h.Exec("Success").Cmd("echo", "ok"),
	)

	result.MustFail()
	result.Task("Fail1").MustFail()
	result.Task("Fail2").MustFail()
	result.Task("Success").MustSucceed()
}

// ============================================================================
// Artifact Format Tests
// ============================================================================

func TestArtifactContainsDurations(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec("Timed Task").CmdString("sleep 0.1"),
	)

	result.MustSucceed()
	result.Task("Timed Task").MustHaveDuration()
}

func TestArtifactShowsTaskCount(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec("T1").Cmd("echo", "1"),
		h.Exec("T2").Cmd("echo", "2"),
		h.Exec("T3").Cmd("echo", "3"),
	)

	result.MustSucceed()
}

func TestArtifactFailureCount(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec("Pass").Cmd("echo", "ok"),
		h.Exec("Fail").CmdString("exit 1"),
	)

	result.MustFail()
	// Should show FAILED (1/N) in output
	result.MustContain("FAILED")
}

func TestArtifactBorders(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec().Cmd("echo", "test"),
	)

	result.MustSucceed()
	// Should have box drawing characters
	if !strings.Contains(result.Raw(), "─") && !strings.Contains(result.Raw(), "-") {
		t.Errorf("expected border characters in output")
	}
}

// ============================================================================
// Log Command Tests
// ============================================================================

func TestLogCommand(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Start("Task With Logs"),
		h.Log("First log message"),
		h.Log("Second log message"),
		h.End("Task With Logs"),
	)

	result.MustSucceed()
	result.Task("Task With Logs").MustSucceed()
}

// ============================================================================
// Scope Isolation Tests
// ============================================================================

func TestScopeStackIsolation(t *testing.T) {
	h := testutil.New(t)

	// Test scope stack properly tracks nesting
	result := h.Run(
		h.Start("A"),
		h.Start("B"),
		h.Exec().Cmd("echo", "in B"),
		h.End(), // Should end B (current scope)
		h.Exec().Cmd("echo", "in A"),
		h.End(), // Should end A
	)

	result.MustSucceed()
}

func TestEndWithoutNameUsesCurrentScope(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Start("First"),
		h.End(),
		h.Start("Second"),
		h.End(),
	)

	result.MustSucceed()
	result.MustHaveTask("First")
	result.MustHaveTask("Second")
}

func TestInterleavedScopes(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Start("Outer"),
		h.Exec("Outer-Task1").Cmd("echo", "1"),
		h.Start("Inner"),
		h.Exec("Inner-Task").Cmd("echo", "2"),
		h.End("Inner"),
		h.Exec("Outer-Task2").Cmd("echo", "3"),
		h.End("Outer"),
	)

	result.MustSucceed()
}

// ============================================================================
// Edge Cases
// ============================================================================

func TestEmptyScript(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Shell("echo 'just output'"),
	)

	result.MustSucceed()
}

func TestLongTaskName(t *testing.T) {
	h := testutil.New(t)
	longName := strings.Repeat("A", 100)

	result := h.Run(
		h.Exec(longName).Cmd("echo", "test"),
	)

	result.MustSucceed()
}

func TestSpecialCharactersInTaskName(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec("Task with 'quotes' and spaces").Cmd("echo", "test"),
	)

	result.MustSucceed()
}

func TestCommandWithComplexArgs(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Exec("Complex").CmdString("echo 'arg1 arg2 arg3'"),
	)

	result.MustSucceed()
}

func TestRapidTaskCreation(t *testing.T) {
	h := testutil.New(t).WithTimeout(60 * time.Second)

	var ops []testutil.Op
	for i := 0; i < 20; i++ {
		ops = append(ops, h.Exec().Cmd("echo", "task"))
	}

	result := h.Run(ops...)
	result.MustSucceed()
}

// ============================================================================
// Error Handling Tests
// ============================================================================

func TestEndNonexistentTask(t *testing.T) {
	h := testutil.New(t)

	// Script should complete even if end fails
	result := h.Run(
		h.Shell(`./chronos end "NonexistentTask" 2>&1 || true`),
	)

	// The script itself succeeds (error is caught by || true)
	result.MustSucceed()
}

func TestStartOutsideSession(t *testing.T) {
	// Find or build the binary
	h := testutil.New(t)
	_ = h // Just to ensure binary is built

	// Run start command directly (not through chronos run)
	cmd := exec.Command("go", "run", "./cmd/chronos", "start", "SomeTask")
	cmd.Dir = findProjectRoot()
	out, err := cmd.CombinedOutput()

	if err == nil {
		t.Error("expected error when running start outside session")
	}

	if !strings.Contains(strings.ToLower(string(out)), "no active session") {
		t.Errorf("expected 'no active session' error, got: %s", out)
	}
}

func TestExecOutsideSession(t *testing.T) {
	h := testutil.New(t)
	_ = h

	cmd := exec.Command("go", "run", "./cmd/chronos", "exec", "--", "echo", "test")
	cmd.Dir = findProjectRoot()
	out, err := cmd.CombinedOutput()

	if err == nil {
		t.Error("expected error when running exec outside session")
	}

	if !strings.Contains(strings.ToLower(string(out)), "no active session") {
		t.Errorf("expected 'no active session' error, got: %s", out)
	}
}

func TestLogOutsideSession(t *testing.T) {
	h := testutil.New(t)
	_ = h

	cmd := exec.Command("go", "run", "./cmd/chronos", "log", "some message")
	cmd.Dir = findProjectRoot()
	out, err := cmd.CombinedOutput()

	if err == nil {
		t.Error("expected error when running log outside session")
	}

	if !strings.Contains(strings.ToLower(string(out)), "no active session") {
		t.Errorf("expected 'no active session' error, got: %s", out)
	}
}

// ============================================================================
// Complex Scenarios
// ============================================================================

func TestBuildDeployPipeline(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Start("Build"),
		h.Exec("Install Deps").Cmd("echo", "installing..."),
		h.Exec("Compile").Cmd("echo", "compiling..."),
		h.End("Build"),

		h.Start("Test"),
		h.Exec("Unit Tests").Cmd("echo", "testing..."),
		h.End("Test"),

		h.Start("Deploy"),
		h.Log("Starting deployment..."),
		h.Exec("Push").Cmd("echo", "pushing..."),
		h.Log("Deployment complete"),
		h.End("Deploy"),
	)

	result.MustSucceed()
	result.MustHaveTask("Build")
	result.MustHaveTask("Test")
	result.MustHaveTask("Deploy")
}

func TestPartialFailure(t *testing.T) {
	h := testutil.New(t)

	result := h.Run(
		h.Start("Pipeline"),

		h.Start("Stage1"),
		h.Exec("S1-Task").Cmd("echo", "ok"),
		h.End("Stage1"),

		h.Start("Stage2"),
		h.Exec("S2-Task").CmdString("exit 1"), // Fails
		h.End("Stage2"),

		h.Start("Stage3"), // Still runs
		h.Exec("S3-Task").Cmd("echo", "ok"),
		h.End("Stage3"),

		h.End("Pipeline"),
	)

	result.MustFail()
	result.Task("Stage1").MustSucceed()
	result.Task("S2-Task").MustFail()
	result.Task("Stage3").MustSucceed()
}

// ============================================================================
// Helpers
// ============================================================================

func findProjectRoot() string {
	dir, _ := os.Getwd()
	for {
		if _, err := os.Stat(dir + "/go.mod"); err == nil {
			return dir
		}
		parent := dir[:strings.LastIndex(dir, "/")]
		if parent == dir {
			return "."
		}
		dir = parent
	}
}
