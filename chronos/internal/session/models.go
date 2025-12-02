package session

import (
	"sync"
	"time"

	"github.com/google/uuid"
)

// TaskState represents the current state of a task
type TaskState string

const (
	StateRunning TaskState = "running"
	StateSuccess TaskState = "success"
	StateFailure TaskState = "failure"
	StateAborted TaskState = "aborted"
)

// StateSymbol returns the display symbol for a task state
func (s TaskState) Symbol() string {
	switch s {
	case StateRunning:
		return "●"
	case StateSuccess:
		return "✓"
	case StateFailure:
		return "✗"
	case StateAborted:
		return "⚠"
	default:
		return "○"
	}
}

// Task represents a unit of work in the task tree
type Task struct {
	ID        string
	Name      string
	ParentID  string
	State     TaskState
	StartTime time.Time
	EndTime   time.Time
	ExitCode  int
	Logs      []string
	Children  []*Task

	mu sync.RWMutex
}

// NewTask creates a new task with the given name and parent
func NewTask(name, parentID string) *Task {
	return &Task{
		ID:        uuid.New().String(),
		Name:      name,
		ParentID:  parentID,
		State:     StateRunning,
		StartTime: time.Now(),
		Logs:      make([]string, 0),
		Children:  make([]*Task, 0),
	}
}

// Duration returns the task's duration
func (t *Task) Duration() time.Duration {
	t.mu.RLock()
	defer t.mu.RUnlock()

	if t.EndTime.IsZero() {
		return time.Since(t.StartTime)
	}
	return t.EndTime.Sub(t.StartTime)
}

// End marks the task as completed with the given state
func (t *Task) End(state TaskState, exitCode int) {
	t.mu.Lock()
	defer t.mu.Unlock()

	t.State = state
	t.EndTime = time.Now()
	t.ExitCode = exitCode
}

// AddLog appends a log line to the task
func (t *Task) AddLog(line string) {
	t.mu.Lock()
	defer t.mu.Unlock()

	t.Logs = append(t.Logs, line)
}

// GetLogs returns a copy of the task's logs
func (t *Task) GetLogs() []string {
	t.mu.RLock()
	defer t.mu.RUnlock()

	logs := make([]string, len(t.Logs))
	copy(logs, t.Logs)
	return logs
}

// IsRunning returns true if the task is still running
func (t *Task) IsRunning() bool {
	t.mu.RLock()
	defer t.mu.RUnlock()
	return t.State == StateRunning
}

// Session represents a single chronos run session
type Session struct {
	ID        string
	ScriptName string
	StartTime time.Time
	Root      *Task
	SocketPath string

	tasks    map[string]*Task // ID -> Task
	nameToID map[string]string // Name -> ID (for running tasks only)
	mu       sync.RWMutex
}

// NewSession creates a new session for the given script
func NewSession(scriptName string) *Session {
	sessionID := uuid.New().String()
	root := NewTask(scriptName, "")

	s := &Session{
		ID:         sessionID,
		ScriptName: scriptName,
		StartTime:  time.Now(),
		Root:       root,
		SocketPath: "/tmp/chronos-" + sessionID + ".sock",
		tasks:      make(map[string]*Task),
		nameToID:   make(map[string]string),
	}

	s.tasks[root.ID] = root
	s.nameToID[scriptName] = root.ID

	return s
}

// StartTask creates and registers a new task
func (s *Session) StartTask(name, parentID string) *Task {
	s.mu.Lock()
	defer s.mu.Unlock()

	task := NewTask(name, parentID)
	s.tasks[task.ID] = task
	s.nameToID[name] = task.ID

	// Add as child of parent
	if parent, ok := s.tasks[parentID]; ok {
		parent.mu.Lock()
		parent.Children = append(parent.Children, task)
		parent.mu.Unlock()
	}

	return task
}

// EndTask ends a task by ID
func (s *Session) EndTask(taskID string, state TaskState, exitCode int) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if task, ok := s.tasks[taskID]; ok {
		task.End(state, exitCode)
		// Remove from nameToID since it's no longer running
		delete(s.nameToID, task.Name)
	}
}

// GetTask returns a task by ID
func (s *Session) GetTask(taskID string) *Task {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.tasks[taskID]
}

// GetTaskByName returns a running task by name
func (s *Session) GetTaskByName(name string) *Task {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if id, ok := s.nameToID[name]; ok {
		return s.tasks[id]
	}
	return nil
}

// GetRunningTasks returns all currently running tasks (excluding root)
func (s *Session) GetRunningTasks() []*Task {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var running []*Task
	for _, task := range s.tasks {
		if task.IsRunning() && task.ID != s.Root.ID {
			running = append(running, task)
		}
	}
	return running
}

// GetAllTasks returns all tasks
func (s *Session) GetAllTasks() []*Task {
	s.mu.RLock()
	defer s.mu.RUnlock()

	tasks := make([]*Task, 0, len(s.tasks))
	for _, task := range s.tasks {
		tasks = append(tasks, task)
	}
	return tasks
}

// AddLog adds a log line to a task
func (s *Session) AddLog(taskID, line string) {
	s.mu.RLock()
	task := s.tasks[taskID]
	s.mu.RUnlock()

	if task != nil {
		task.AddLog(line)
	}
}

// AbortAllRunning marks all running tasks as aborted
func (s *Session) AbortAllRunning() {
	s.mu.Lock()
	defer s.mu.Unlock()

	for _, task := range s.tasks {
		if task.IsRunning() {
			task.End(StateAborted, -1)
		}
	}
}

// Stats returns running and completed task counts
func (s *Session) Stats() (running, done int) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	for _, task := range s.tasks {
		if task.IsRunning() {
			running++
		} else {
			done++
		}
	}
	return
}

// Duration returns the session duration
func (s *Session) Duration() time.Duration {
	return time.Since(s.StartTime)
}
