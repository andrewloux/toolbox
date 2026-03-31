package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"

	"github.com/andrewloux/toolbox/chronos/internal/artifact"
	"github.com/andrewloux/toolbox/chronos/internal/protocol"
	"github.com/andrewloux/toolbox/chronos/internal/session"
	"github.com/andrewloux/toolbox/chronos/internal/tui"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/spf13/cobra"
)

var (
	noColor bool
	program *tea.Program
)

func main() {
	rootCmd := &cobra.Command{
		Use:   "chronos",
		Short: "Task runner with live TUI",
		Long:  "Chronos is a CLI tool for tracking hierarchical task execution with a live TUI.",
	}

	// Global flags
	rootCmd.PersistentFlags().BoolVar(&noColor, "no-color", false, "Disable colored output")

	// Add commands
	rootCmd.AddCommand(runCmd())
	rootCmd.AddCommand(startCmd())
	rootCmd.AddCommand(endCmd())
	rootCmd.AddCommand(failCmd())
	rootCmd.AddCommand(execCmd())
	rootCmd.AddCommand(logCmd())

	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

// runCmd implements "chronos run <script> [args...]"
func runCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "run <script> [args...]",
		Short: "Start a session and run a script",
		Args:  cobra.MinimumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			script := args[0]
			scriptArgs := args[1:]

			// Get script name for display
			scriptName := filepath.Base(script)

			// Create session
			sess := session.NewSession(scriptName)

			// Start protocol server
			handler := &sessionHandler{session: sess}
			server := protocol.NewServer(sess.SocketPath, handler)
			if err := server.Start(); err != nil {
				return fmt.Errorf("failed to start server: %w", err)
			}
			defer server.Stop()

			// Channel to signal script completion
			scriptDone := make(chan error, 1)

			// Start the script as subprocess
			scriptCmd := exec.Command(script, scriptArgs...)
			scriptCmd.Env = append(os.Environ(),
				"CHRONOS_SOCK="+sess.SocketPath,
				"CHRONOS_SESSION="+sess.ID,
				"CHRONOS_PARENT="+sess.Root.ID,
			)

			// Capture script output for root task logging
			stdout, _ := scriptCmd.StdoutPipe()
			stderr, _ := scriptCmd.StderrPipe()

			if err := scriptCmd.Start(); err != nil {
				return fmt.Errorf("failed to start script: %w", err)
			}

			// Pipe output to root task logs
			go pipeOutput(stdout, sess.Root, handler)
			go pipeOutput(stderr, sess.Root, handler)

			// Wait for script in background
			go func() {
				err := scriptCmd.Wait()
				scriptDone <- err
			}()

			// Handle signals
			sigChan := make(chan os.Signal, 1)
			signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

			// Start TUI
			quitCallback := func() {
				// Send SIGTERM to script
				if scriptCmd.Process != nil {
					scriptCmd.Process.Signal(syscall.SIGTERM)
				}
			}

			model := tui.NewModel(sess, quitCallback)
			program = tea.NewProgram(model, tea.WithAltScreen())
			handler.program = program

			// Run TUI in background
			tuiDone := make(chan struct{})
			go func() {
				program.Run()
				close(tuiDone)
			}()

			// Wait for script to finish or signal
			select {
			case err := <-scriptDone:
				// Script finished
				if err != nil {
					// Mark root as failed
					sess.Root.End(session.StateFailure, getExitCode(err))
				} else {
					sess.Root.End(session.StateSuccess, 0)
				}
				// Abort any still-running tasks
				sess.AbortAllRunning()

			case sig := <-sigChan:
				// Signal received
				if scriptCmd.Process != nil {
					scriptCmd.Process.Signal(sig)
				}
				sess.AbortAllRunning()
			}

			// Quit TUI
			program.Quit()
			<-tuiDone

			// Print artifact
			fmt.Println()
			fmt.Print(artifact.Generate(sess, noColor))

			// Exit with script's exit code
			if sess.Root.State == session.StateFailure {
				os.Exit(sess.Root.ExitCode)
			}

			return nil
		},
	}
}

func pipeOutput(r io.Reader, task *session.Task, handler *sessionHandler) {
	scanner := bufio.NewScanner(r)
	for scanner.Scan() {
		line := scanner.Text()
		task.AddLog(line)
		if handler.program != nil {
			tui.SendUpdate(handler.program)
		}
	}
}

func getExitCode(err error) int {
	if exitErr, ok := err.(*exec.ExitError); ok {
		return exitErr.ExitCode()
	}
	return 1
}

// sessionHandler handles protocol events
type sessionHandler struct {
	session *session.Session
	program *tea.Program
}

func (h *sessionHandler) HandleEvent(event *protocol.Event) *protocol.Response {
	switch event.Type {
	case protocol.EventStart:
		task := h.session.StartTask(event.Name, event.Parent)
		if h.program != nil {
			tui.SendUpdate(h.program)
		}
		return &protocol.Response{Success: true, TaskID: task.ID}

	case protocol.EventEnd:
		state := session.StateSuccess
		if event.Status == "failure" {
			state = session.StateFailure
		} else if event.Status == "aborted" {
			state = session.StateAborted
		}
		h.session.EndTask(event.ID, state, event.Code)
		if h.program != nil {
			tui.SendUpdate(h.program)
		}
		return &protocol.Response{Success: true}

	case protocol.EventLog:
		h.session.AddLog(event.ID, event.Line)
		if h.program != nil {
			tui.SendUpdate(h.program)
		}
		return &protocol.Response{Success: true}

	default:
		return &protocol.Response{Success: false, Error: "unknown event type"}
	}
}

// startCmd implements "chronos start <name>"
func startCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "start <name>",
		Short: "Begin a new task",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			name := args[0]

			client, err := protocol.NewClientFromEnv()
			if err != nil {
				return err
			}

			// Get current scope from stack (fallback to env root)
			parentID := getCurrentScope()
			if parentID == "" {
				parentID = os.Getenv("CHRONOS_PARENT")
			}

			resp, err := client.StartTask(name, parentID)
			if err != nil {
				return fmt.Errorf("failed to start task: %w", err)
			}

			if !resp.Success {
				return fmt.Errorf("failed to start task: %s", resp.Error)
			}

			// Push new task onto scope stack
			pushScope(resp.TaskID)

			// Store name -> ID mapping for end by name
			storeTaskMapping(name, resp.TaskID)

			return nil
		},
	}
}

// endCmd implements "chronos end [name]"
func endCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "end [name]",
		Short: "End a task as success",
		Args:  cobra.MaximumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return endTask(args, "success")
		},
	}
}

// failCmd implements "chronos fail [name]"
func failCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "fail [name]",
		Short: "End a task as failure",
		Args:  cobra.MaximumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			return endTask(args, "failure")
		},
	}
}

func endTask(args []string, status string) error {
	client, err := protocol.NewClientFromEnv()
	if err != nil {
		return err
	}

	var taskID string

	if len(args) > 0 {
		// End by name
		name := args[0]
		taskID = loadTaskMapping(name)
		if taskID == "" {
			return fmt.Errorf("no running task named '%s'", name)
		}
		// Remove this task from scope stack
		removeFromScope(taskID)
	} else {
		// End current scope (top of stack)
		taskID = getCurrentScope()
		if taskID == "" {
			return fmt.Errorf("no tasks to end")
		}
		// Pop from scope stack
		popScope()
	}

	resp, err := client.EndTask(taskID, status, 0)
	if err != nil {
		return fmt.Errorf("failed to end task: %w", err)
	}

	if !resp.Success {
		return fmt.Errorf("failed to end task: %s", resp.Error)
	}

	return nil
}

// execCmd implements "chronos exec [name] -- <command...>"
func execCmd() *cobra.Command {
	return &cobra.Command{
		Use:                "exec [name] -- <command...>",
		Short:              "Run a command as a task",
		Args:               cobra.MinimumNArgs(1),
		DisableFlagParsing: true,
		RunE: func(cmd *cobra.Command, args []string) error {
			// Parse name and command
			// Note: DisableFlagParsing means we see all args including "--"
			var name string
			var cmdArgs []string

			// Find "--" separator
			dashIdx := -1
			for i, arg := range args {
				if arg == "--" {
					dashIdx = i
					break
				}
			}

			if dashIdx == -1 {
				// No "--", everything is command
				cmdArgs = args
				name = strings.Join(args, " ")
			} else if dashIdx == 0 {
				// "-- cmd args..."
				cmdArgs = args[1:]
				name = strings.Join(cmdArgs, " ")
			} else {
				// "name -- cmd args..."
				name = strings.Join(args[:dashIdx], " ")
				cmdArgs = args[dashIdx+1:]
			}

			if len(cmdArgs) == 0 {
				return fmt.Errorf("no command specified")
			}

			client, err := protocol.NewClientFromEnv()
			if err != nil {
				return err
			}

			// Get current scope from stack (fallback to env root)
			parentID := getCurrentScope()
			if parentID == "" {
				parentID = os.Getenv("CHRONOS_PARENT")
			}

			// Start task
			startResp, err := client.StartTask(name, parentID)
			if err != nil {
				return fmt.Errorf("failed to start task: %w", err)
			}

			taskID := startResp.TaskID

			// Run command
			execCmd := exec.Command(cmdArgs[0], cmdArgs[1:]...)
			execCmd.Env = append(os.Environ(),
				"CHRONOS_PARENT="+taskID,
			)

			stdout, _ := execCmd.StdoutPipe()
			stderr, _ := execCmd.StderrPipe()

			if err := execCmd.Start(); err != nil {
				client.EndTask(taskID, "failure", 1)
				return fmt.Errorf("failed to run command: %w", err)
			}

			// Stream output to logs
			go streamLogs(stdout, taskID, client)
			go streamLogs(stderr, taskID, client)

			// Wait for command
			err = execCmd.Wait()

			// End task
			status := "success"
			exitCode := 0
			if err != nil {
				status = "failure"
				exitCode = getExitCode(err)
			}

			client.EndTask(taskID, status, exitCode)

			if err != nil {
				os.Exit(exitCode)
			}

			return nil
		},
	}
}

func streamLogs(r io.Reader, taskID string, client *protocol.Client) {
	scanner := bufio.NewScanner(r)
	for scanner.Scan() {
		line := scanner.Text()
		client.Log(taskID, line)
	}
}

// logCmd implements "chronos log <message>"
func logCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "log <message>",
		Short: "Log a message to current task",
		Args:  cobra.MinimumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			message := strings.Join(args, " ")

			client, err := protocol.NewClientFromEnv()
			if err != nil {
				return err
			}

			// Get current scope from stack (fallback to env root)
			taskID := getCurrentScope()
			if taskID == "" {
				taskID = os.Getenv("CHRONOS_PARENT")
			}
			if taskID == "" {
				return fmt.Errorf("no active task")
			}

			resp, err := client.Log(taskID, message)
			if err != nil {
				return fmt.Errorf("failed to log: %w", err)
			}

			if !resp.Success {
				return fmt.Errorf("failed to log: %s", resp.Error)
			}

			return nil
		},
	}
}

// Task mapping helpers (store in /tmp for simplicity)
func getTaskMappingPath() string {
	sessionID := os.Getenv("CHRONOS_SESSION")
	return fmt.Sprintf("/tmp/chronos-tasks-%s.map", sessionID)
}

func storeTaskMapping(name, taskID string) {
	path := getTaskMappingPath()
	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return
	}
	defer f.Close()
	f.WriteString(fmt.Sprintf("%s=%s\n", name, taskID))
}

func loadTaskMapping(name string) string {
	path := getTaskMappingPath()
	data, err := os.ReadFile(path)
	if err != nil {
		return ""
	}

	lines := strings.Split(string(data), "\n")
	// Search from end (most recent)
	for i := len(lines) - 1; i >= 0; i-- {
		parts := strings.SplitN(lines[i], "=", 2)
		if len(parts) == 2 && parts[0] == name {
			return parts[1]
		}
	}
	return ""
}

// Scope stack helpers - track nested task scope via file
func getScopeStackPath() string {
	sessionID := os.Getenv("CHRONOS_SESSION")
	return fmt.Sprintf("/tmp/chronos-scope-%s.stack", sessionID)
}

func pushScope(taskID string) {
	path := getScopeStackPath()
	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return
	}
	defer f.Close()
	f.WriteString(taskID + "\n")
}

func popScope() string {
	path := getScopeStackPath()
	data, err := os.ReadFile(path)
	if err != nil {
		return ""
	}

	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	if len(lines) == 0 {
		return ""
	}

	// Get the last item
	popped := lines[len(lines)-1]

	// Write back without the last item
	if len(lines) > 1 {
		os.WriteFile(path, []byte(strings.Join(lines[:len(lines)-1], "\n")+"\n"), 0644)
	} else {
		os.Remove(path)
	}

	return popped
}

func getCurrentScope() string {
	path := getScopeStackPath()
	data, err := os.ReadFile(path)
	if err != nil {
		return ""
	}

	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	if len(lines) == 0 {
		return ""
	}

	return lines[len(lines)-1]
}

func removeFromScope(taskID string) {
	path := getScopeStackPath()
	data, err := os.ReadFile(path)
	if err != nil {
		return
	}

	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	var newLines []string
	for _, line := range lines {
		if line != taskID {
			newLines = append(newLines, line)
		}
	}

	if len(newLines) > 0 {
		os.WriteFile(path, []byte(strings.Join(newLines, "\n")+"\n"), 0644)
	} else {
		os.Remove(path)
	}
}
