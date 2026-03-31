package testutil

import (
	"fmt"
	"regexp"
	"strings"
	"testing"
)

// Result represents the parsed output of a Chronos run.
type Result struct {
	t        *testing.T
	raw      string
	script   string
	exitCode int
	err      error

	// Parsed fields
	status   string  // "SUCCESS", "FAILED (n/m)", "ABORTED"
	tasks    []*Task // Top-level tasks (children of root)
	allTasks []*Task // Flattened list of all tasks
}

// Task represents a parsed task from the artifact output.
type Task struct {
	Name     string
	State    TaskState
	Duration string
	Output   []string // Log lines shown for failed tasks
	ExitCode int
	Children []*Task
	parent   *Task
}

// TaskState represents the state of a task.
type TaskState string

const (
	TaskSuccess TaskState = "success"
	TaskFailure TaskState = "failure"
	TaskAborted TaskState = "aborted"
	TaskUnknown TaskState = "unknown"
)

// Regex patterns for parsing artifact output
var (
	// Match task lines with box borders:
	// │  [OK] Name .......................................... 5ms  │
	// │     [FAIL] Name                                      5ms  │
	taskLinePattern = regexp.MustCompile(`(\[OK\]|\[FAIL\]|\[ABORT\]|✓|✗|⚠)\s+(.+?)\s+(?:\.+\s+)?(\d+(?:ms|m\s*\d*s?|s))`)

	// Match failure output lines: └─ message
	failOutputPattern = regexp.MustCompile(`└─\s+(.+?)(?:\s*│)?$`)

	// Match exit code: exit code N
	exitCodePattern = regexp.MustCompile(`exit code (\d+)`)

	// Match status line: SUCCESS or FAILED (n/m) or ABORTED
	statusPattern = regexp.MustCompile(`(SUCCESS|FAILED\s*\(\d+/\d+\)|ABORTED)`)
)

func parseResult(t *testing.T, output string, exitCode int, err error, script string) *Result {
	t.Helper()

	r := &Result{
		t:        t,
		raw:      output,
		script:   script,
		exitCode: exitCode,
		err:      err,
	}

	// Parse status from footer
	if matches := statusPattern.FindStringSubmatch(output); len(matches) > 1 {
		r.status = strings.TrimSpace(matches[1])
	}

	// Parse tasks
	r.tasks, r.allTasks = parseTasks(output)

	return r
}

func parseTasks(output string) ([]*Task, []*Task) {
	var allTasks []*Task

	lines := strings.Split(output, "\n")

	for i := 0; i < len(lines); i++ {
		line := lines[i]

		// Try to match a task line
		if matches := taskLinePattern.FindStringSubmatch(line); len(matches) >= 4 {
			task := &Task{
				Name:     strings.TrimSpace(matches[2]),
				Duration: matches[3],
				State:    parseState(matches[1]),
			}

			// Collect failure output lines following this task
			if task.State == TaskFailure {
				for j := i + 1; j < len(lines); j++ {
					if failMatches := failOutputPattern.FindStringSubmatch(lines[j]); len(failMatches) >= 2 {
						outputLine := strings.TrimSpace(failMatches[1])

						// Check for exit code
						if codeMatches := exitCodePattern.FindStringSubmatch(outputLine); len(codeMatches) >= 2 {
							var code int
							fmt.Sscanf(codeMatches[1], "%d", &code)
							task.ExitCode = code
						}

						task.Output = append(task.Output, outputLine)
						i = j // Skip these lines in main loop
					} else {
						break
					}
				}
			}

			allTasks = append(allTasks, task)
		}
	}

	// For now, treat all tasks as top-level (hierarchy is complex to parse)
	// The important thing is that FindTask can find any task by name
	return allTasks, allTasks
}

func parseState(marker string) TaskState {
	switch marker {
	case "[OK]", "✓":
		return TaskSuccess
	case "[FAIL]", "✗":
		return TaskFailure
	case "[ABORT]", "⚠":
		return TaskAborted
	default:
		return TaskUnknown
	}
}

// Raw returns the raw output string.
func (r *Result) Raw() string {
	return r.raw
}

// Script returns the generated script that was executed.
func (r *Result) Script() string {
	return r.script
}

// ExitCode returns the exit code of the script.
func (r *Result) ExitCode() int {
	return r.exitCode
}

// Status returns the parsed status string (SUCCESS, FAILED (n/m), ABORTED).
func (r *Result) Status() string {
	return r.status
}

// Tasks returns all top-level tasks.
func (r *Result) Tasks() []*Task {
	return r.tasks
}

// AllTasks returns a flattened list of all tasks.
func (r *Result) AllTasks() []*Task {
	return r.allTasks
}

// IsSuccess returns true if the run succeeded.
func (r *Result) IsSuccess() bool {
	return strings.HasPrefix(r.status, "SUCCESS")
}

// IsFailed returns true if the run failed.
func (r *Result) IsFailed() bool {
	return strings.HasPrefix(r.status, "FAILED")
}

// IsAborted returns true if the run was aborted.
func (r *Result) IsAborted() bool {
	return strings.HasPrefix(r.status, "ABORTED")
}

// FindTask finds a task by name (searches all tasks recursively).
func (r *Result) FindTask(name string) *Task {
	for _, task := range r.allTasks {
		if task.Name == name {
			return task
		}
	}
	return nil
}

// HasTask returns true if a task with the given name exists.
func (r *Result) HasTask(name string) bool {
	return r.FindTask(name) != nil
}
