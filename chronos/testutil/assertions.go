package testutil

import (
	"fmt"
	"strings"
	"testing"
)

// ============================================================================
// Result Assertions
// ============================================================================

// MustSucceed asserts that the run succeeded.
func (r *Result) MustSucceed() *Result {
	r.t.Helper()
	if !r.IsSuccess() {
		r.t.Fatalf("expected SUCCESS, got %q\n\nOutput:\n%s\n\nScript:\n%s",
			r.status, r.raw, r.script)
	}
	return r
}

// MustFail asserts that the run failed.
func (r *Result) MustFail() *Result {
	r.t.Helper()
	if !r.IsFailed() {
		r.t.Fatalf("expected FAILED, got %q\n\nOutput:\n%s", r.status, r.raw)
	}
	return r
}

// MustFailWith asserts the run failed with specific counts.
func (r *Result) MustFailWith(failed, total int) *Result {
	r.t.Helper()
	expected := fmt.Sprintf("FAILED (%d/%d)", failed, total)
	// Normalize whitespace
	normalizedStatus := strings.ReplaceAll(r.status, " ", "")
	normalizedExpected := strings.ReplaceAll(expected, " ", "")

	if normalizedStatus != normalizedExpected {
		r.t.Fatalf("expected %q, got %q\n\nOutput:\n%s", expected, r.status, r.raw)
	}
	return r
}

// MustAbort asserts that the run was aborted.
func (r *Result) MustAbort() *Result {
	r.t.Helper()
	if !r.IsAborted() {
		r.t.Fatalf("expected ABORTED, got %q\n\nOutput:\n%s", r.status, r.raw)
	}
	return r
}

// MustContain asserts that the output contains the given string.
func (r *Result) MustContain(s string) *Result {
	r.t.Helper()
	if !strings.Contains(r.raw, s) {
		r.t.Fatalf("expected output to contain %q\n\nOutput:\n%s", s, r.raw)
	}
	return r
}

// MustNotContain asserts that the output does not contain the given string.
func (r *Result) MustNotContain(s string) *Result {
	r.t.Helper()
	if strings.Contains(r.raw, s) {
		r.t.Fatalf("expected output NOT to contain %q\n\nOutput:\n%s", s, r.raw)
	}
	return r
}

// MustHaveTask asserts that a task with the given name exists.
func (r *Result) MustHaveTask(name string) *Result {
	r.t.Helper()
	if !r.HasTask(name) {
		r.t.Fatalf("expected task %q to exist\n\nOutput:\n%s", name, r.raw)
	}
	return r
}

// MustNotHaveTask asserts that a task with the given name does not exist.
func (r *Result) MustNotHaveTask(name string) *Result {
	r.t.Helper()
	if r.HasTask(name) {
		r.t.Fatalf("expected task %q NOT to exist\n\nOutput:\n%s", name, r.raw)
	}
	return r
}

// MustHaveTaskCount asserts the total number of tasks.
func (r *Result) MustHaveTaskCount(count int) *Result {
	r.t.Helper()
	if len(r.allTasks) != count {
		r.t.Fatalf("expected %d tasks, got %d\n\nTasks: %v\n\nOutput:\n%s",
			count, len(r.allTasks), taskNames(r.allTasks), r.raw)
	}
	return r
}

// MustHaveExitCode asserts the script exit code.
func (r *Result) MustHaveExitCode(code int) *Result {
	r.t.Helper()
	if r.exitCode != code {
		r.t.Fatalf("expected exit code %d, got %d\n\nOutput:\n%s", code, r.exitCode, r.raw)
	}
	return r
}

// Task returns a TaskAssertion for the named task.
// If the task doesn't exist, assertions on it will fail with helpful messages.
func (r *Result) Task(name string) *TaskAssertion {
	r.t.Helper()
	return &TaskAssertion{
		t:      r.t,
		task:   r.FindTask(name),
		name:   name,
		result: r,
	}
}

// ============================================================================
// Task Assertions
// ============================================================================

// TaskAssertion provides fluent assertions on a task.
type TaskAssertion struct {
	t      *testing.T
	task   *Task
	name   string
	result *Result
}

// MustExist asserts that the task exists.
func (a *TaskAssertion) MustExist() *TaskAssertion {
	a.t.Helper()
	if a.task == nil {
		a.t.Fatalf("expected task %q to exist\n\nOutput:\n%s", a.name, a.result.raw)
	}
	return a
}

// MustSucceed asserts that the task succeeded.
func (a *TaskAssertion) MustSucceed() *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	if a.task.State != TaskSuccess {
		a.t.Fatalf("expected task %q to succeed, but state is %q\n\nOutput:\n%s",
			a.name, a.task.State, a.result.raw)
	}
	return a
}

// MustFail asserts that the task failed.
func (a *TaskAssertion) MustFail() *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	if a.task.State != TaskFailure {
		a.t.Fatalf("expected task %q to fail, but state is %q\n\nOutput:\n%s",
			a.name, a.task.State, a.result.raw)
	}
	return a
}

// MustAbort asserts that the task was aborted.
func (a *TaskAssertion) MustAbort() *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	if a.task.State != TaskAborted {
		a.t.Fatalf("expected task %q to be aborted, but state is %q\n\nOutput:\n%s",
			a.name, a.task.State, a.result.raw)
	}
	return a
}

// MustHaveState asserts the task's state.
func (a *TaskAssertion) MustHaveState(state TaskState) *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	if a.task.State != state {
		a.t.Fatalf("expected task %q to have state %q, got %q\n\nOutput:\n%s",
			a.name, state, a.task.State, a.result.raw)
	}
	return a
}

// MustHaveExitCode asserts the task's exit code.
func (a *TaskAssertion) MustHaveExitCode(code int) *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	if a.task.ExitCode != code {
		a.t.Fatalf("expected task %q to have exit code %d, got %d\n\nOutput:\n%s",
			a.name, code, a.task.ExitCode, a.result.raw)
	}
	return a
}

// MustShowOutput asserts that the task's output contains the given string.
func (a *TaskAssertion) MustShowOutput(s string) *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	found := false
	for _, line := range a.task.Output {
		if strings.Contains(line, s) {
			found = true
			break
		}
	}
	if !found {
		a.t.Fatalf("expected task %q output to contain %q\n\nOutput lines: %v\n\nFull output:\n%s",
			a.name, s, a.task.Output, a.result.raw)
	}
	return a
}

// MustHaveChild asserts that the task has a child with the given name.
func (a *TaskAssertion) MustHaveChild(name string) *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	for _, child := range a.task.Children {
		if child.Name == name {
			return a
		}
	}
	a.t.Fatalf("expected task %q to have child %q\n\nChildren: %v\n\nOutput:\n%s",
		a.name, name, taskNames(a.task.Children), a.result.raw)
	return a
}

// MustHaveChildren asserts that the task has children with the given names.
func (a *TaskAssertion) MustHaveChildren(names ...string) *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	for _, name := range names {
		found := false
		for _, child := range a.task.Children {
			if child.Name == name {
				found = true
				break
			}
		}
		if !found {
			a.t.Fatalf("expected task %q to have child %q\n\nChildren: %v\n\nOutput:\n%s",
				a.name, name, taskNames(a.task.Children), a.result.raw)
		}
	}
	return a
}

// MustHaveChildCount asserts the number of children.
func (a *TaskAssertion) MustHaveChildCount(count int) *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	if len(a.task.Children) != count {
		a.t.Fatalf("expected task %q to have %d children, got %d\n\nChildren: %v\n\nOutput:\n%s",
			a.name, count, len(a.task.Children), taskNames(a.task.Children), a.result.raw)
	}
	return a
}

// MustHaveDuration asserts the task has a non-empty duration.
func (a *TaskAssertion) MustHaveDuration() *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	if a.task.Duration == "" {
		a.t.Fatalf("expected task %q to have a duration\n\nOutput:\n%s",
			a.name, a.result.raw)
	}
	return a
}

// Child returns a TaskAssertion for a child task.
func (a *TaskAssertion) Child(name string) *TaskAssertion {
	a.t.Helper()
	a.MustExist()
	for _, child := range a.task.Children {
		if child.Name == name {
			return &TaskAssertion{
				t:      a.t,
				task:   child,
				name:   name,
				result: a.result,
			}
		}
	}
	// Return assertion with nil task - will fail on first assertion call
	return &TaskAssertion{
		t:      a.t,
		task:   nil,
		name:   name,
		result: a.result,
	}
}

// ============================================================================
// Helpers
// ============================================================================

func taskNames(tasks []*Task) []string {
	names := make([]string, len(tasks))
	for i, t := range tasks {
		names[i] = t.Name
	}
	return names
}

// ============================================================================
// Convenience Constructors for Common Patterns
// ============================================================================

// AssertSuccessfulExec is a convenience for testing a simple exec that succeeds.
func (r *Result) AssertSuccessfulExec(taskName string) *Result {
	r.t.Helper()
	r.MustSucceed()
	r.Task(taskName).MustSucceed()
	return r
}

// AssertFailedExec is a convenience for testing an exec that fails.
func (r *Result) AssertFailedExec(taskName string, exitCode int) *Result {
	r.t.Helper()
	r.MustFail()
	r.Task(taskName).MustFail().MustHaveExitCode(exitCode)
	return r
}

// Dump prints the result for debugging.
func (r *Result) Dump() *Result {
	fmt.Printf("=== Result Dump ===\n")
	fmt.Printf("Status: %s\n", r.status)
	fmt.Printf("Exit Code: %d\n", r.exitCode)
	fmt.Printf("Tasks: %v\n", taskNames(r.allTasks))
	fmt.Printf("\n--- Raw Output ---\n%s\n", r.raw)
	fmt.Printf("\n--- Script ---\n%s\n", r.script)
	fmt.Printf("==================\n")
	return r
}
