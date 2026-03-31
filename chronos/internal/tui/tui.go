package tui

import (
	"fmt"
	"strings"
	"time"

	"github.com/andrewloux/toolbox/chronos/internal/session"
	"github.com/charmbracelet/bubbles/key"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// Colors
var (
	colorCyan    = lipgloss.Color("#00FFFF")
	colorGreen   = lipgloss.Color("#00FF00")
	colorRed     = lipgloss.Color("#FF0000")
	colorYellow  = lipgloss.Color("#FFFF00")
	colorDimGray = lipgloss.Color("#666666")
	colorGray    = lipgloss.Color("#888888")
	colorDim     = lipgloss.Color("#444444")
	colorWhite   = lipgloss.Color("#FFFFFF")
	colorFocus   = lipgloss.Color("#1a1a2e")
)

// Styles
var (
	borderStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(colorDim)

	headerStyle = lipgloss.NewStyle().
			Foreground(colorWhite).
			Bold(true)

	runningStyle = lipgloss.NewStyle().
			Foreground(colorCyan)

	successStyle = lipgloss.NewStyle().
			Foreground(colorGreen)

	failureStyle = lipgloss.NewStyle().
			Foreground(colorRed)

	abortedStyle = lipgloss.NewStyle().
			Foreground(colorYellow)

	dimStyle = lipgloss.NewStyle().
			Foreground(colorDimGray)

	grayStyle = lipgloss.NewStyle().
			Foreground(colorGray)

	treeLineStyle = lipgloss.NewStyle().
			Foreground(colorDim)

	logHeaderStyle = lipgloss.NewStyle().
			Foreground(colorCyan).
			Bold(true)

	focusedStyle = lipgloss.NewStyle().
			Background(colorFocus)
)

// KeyMap defines key bindings
type KeyMap struct {
	Up   key.Binding
	Down key.Binding
	Esc  key.Binding
	Quit key.Binding
}

var keys = KeyMap{
	Up: key.NewBinding(
		key.WithKeys("up", "k"),
		key.WithHelp("↑/k", "move up"),
	),
	Down: key.NewBinding(
		key.WithKeys("down", "j"),
		key.WithHelp("↓/j", "move down"),
	),
	Esc: key.NewBinding(
		key.WithKeys("esc"),
		key.WithHelp("esc", "auto-follow"),
	),
	Quit: key.NewBinding(
		key.WithKeys("q"),
		key.WithHelp("q", "quit"),
	),
}

// TickMsg triggers a refresh
type TickMsg time.Time

// SessionUpdateMsg signals session state changed
type SessionUpdateMsg struct{}

// Model is the TUI model
type Model struct {
	session      *session.Session
	width        int
	height       int
	focusedTask  *session.Task
	autoFollow   bool
	flatTasks    []*session.Task // Flattened task list for navigation
	focusIndex   int
	quitting     bool
	quitCallback func()
}

// NewModel creates a new TUI model
func NewModel(sess *session.Session, quitCallback func()) Model {
	return Model{
		session:      sess,
		autoFollow:   true,
		quitCallback: quitCallback,
	}
}

// Init initializes the model
func (m Model) Init() tea.Cmd {
	return tea.Batch(tickCmd(), tea.EnterAltScreen)
}

func tickCmd() tea.Cmd {
	return tea.Tick(time.Second, func(t time.Time) tea.Msg {
		return TickMsg(t)
	})
}

// Update handles messages
func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch {
		case key.Matches(msg, keys.Quit):
			m.quitting = true
			if m.quitCallback != nil {
				m.quitCallback()
			}
			return m, tea.Quit

		case key.Matches(msg, keys.Up):
			m.autoFollow = false
			if m.focusIndex > 0 {
				m.focusIndex--
				if m.focusIndex < len(m.flatTasks) {
					m.focusedTask = m.flatTasks[m.focusIndex]
				}
			}

		case key.Matches(msg, keys.Down):
			m.autoFollow = false
			if m.focusIndex < len(m.flatTasks)-1 {
				m.focusIndex++
				if m.focusIndex < len(m.flatTasks) {
					m.focusedTask = m.flatTasks[m.focusIndex]
				}
			}

		case key.Matches(msg, keys.Esc):
			m.autoFollow = true
		}

	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height

	case TickMsg:
		return m, tickCmd()

	case SessionUpdateMsg:
		// Session updated, will re-render
	}

	// Update flat task list
	m.flatTasks = m.flattenTasks(m.session.Root)

	// Auto-follow: focus on most recently active task
	if m.autoFollow && len(m.flatTasks) > 0 {
		m.focusedTask = m.findMostRecentActive()
		for i, t := range m.flatTasks {
			if t == m.focusedTask {
				m.focusIndex = i
				break
			}
		}
	}

	return m, nil
}

func (m Model) flattenTasks(root *session.Task) []*session.Task {
	var tasks []*session.Task
	var flatten func(t *session.Task)
	flatten = func(t *session.Task) {
		tasks = append(tasks, t)
		for _, child := range t.Children {
			flatten(child)
		}
	}
	flatten(root)
	return tasks
}

func (m Model) findMostRecentActive() *session.Task {
	var mostRecent *session.Task
	var mostRecentTime time.Time

	for _, task := range m.flatTasks {
		if task.IsRunning() {
			if mostRecent == nil || task.StartTime.After(mostRecentTime) {
				mostRecent = task
				mostRecentTime = task.StartTime
			}
		}
	}

	if mostRecent == nil && len(m.flatTasks) > 0 {
		// No running tasks, pick the last one
		mostRecent = m.flatTasks[len(m.flatTasks)-1]
	}

	return mostRecent
}

// View renders the TUI
func (m Model) View() string {
	if m.quitting {
		return ""
	}

	if m.width == 0 || m.height == 0 {
		return "Loading..."
	}

	// Calculate dimensions
	contentWidth := m.width - 4 // Account for borders
	if contentWidth < 40 {
		contentWidth = 40
	}

	// Build sections
	header := m.renderHeader(contentWidth)
	tree := m.renderTree(contentWidth)
	logPane := m.renderLogPane(contentWidth)

	// Combine with borders
	headerBox := borderStyle.Width(contentWidth).Render(
		lipgloss.NewStyle().Padding(0, 1).Render(
			headerStyle.Render("CHRONOS") + "\n\n" + header,
		),
	)

	// Calculate remaining height for tree and logs
	headerHeight := lipgloss.Height(headerBox)
	remainingHeight := m.height - headerHeight - 2

	treeHeight := remainingHeight * 2 / 3
	if treeHeight < 10 {
		treeHeight = 10
	}
	logHeight := remainingHeight - treeHeight

	treeBox := borderStyle.Width(contentWidth).Height(treeHeight).Render(
		lipgloss.NewStyle().Padding(0, 1).Render(tree),
	)

	logBox := borderStyle.Width(contentWidth).Height(logHeight).Render(
		lipgloss.NewStyle().Padding(0, 1).Render(logPane),
	)

	return lipgloss.JoinVertical(lipgloss.Left, headerBox, treeBox, logBox)
}

func (m Model) renderHeader(width int) string {
	running, done := m.session.Stats()
	elapsed := formatDuration(m.session.Duration(), true)

	return fmt.Sprintf("%s  •  %s  •  %d running  •  %d done",
		m.session.ScriptName,
		runningStyle.Render(elapsed),
		running,
		done,
	)
}

func (m Model) renderTree(width int) string {
	var lines []string
	m.renderTaskTree(m.session.Root, "", true, &lines, width)
	return strings.Join(lines, "\n")
}

func (m Model) renderTaskTree(task *session.Task, prefix string, isLast bool, lines *[]string, width int) {
	// Render this task
	line := m.renderTaskLine(task, prefix, isLast, width)
	*lines = append(*lines, line)

	// Render children
	childPrefix := prefix
	if prefix != "" {
		if isLast {
			childPrefix += "    "
		} else {
			childPrefix += treeLineStyle.Render("│") + "   "
		}
	}

	for i, child := range task.Children {
		isChildLast := i == len(task.Children)-1

		// Add blank line between top-level siblings
		if task == m.session.Root && i > 0 {
			*lines = append(*lines, "")
		}

		m.renderTaskTree(child, childPrefix, isChildLast, lines, width)
	}
}

func (m Model) renderTaskLine(task *session.Task, prefix string, isLast bool, width int) string {
	// Status symbol
	symbol := task.State.Symbol()
	var styledSymbol string
	switch task.State {
	case session.StateRunning:
		styledSymbol = runningStyle.Render(symbol)
	case session.StateSuccess:
		styledSymbol = successStyle.Render(symbol)
	case session.StateFailure:
		styledSymbol = failureStyle.Render(symbol)
	case session.StateAborted:
		styledSymbol = abortedStyle.Render(symbol)
	default:
		styledSymbol = dimStyle.Render(symbol)
	}

	// Tree connector
	connector := ""
	if prefix != "" {
		if isLast {
			connector = treeLineStyle.Render("└── ")
		} else {
			connector = treeLineStyle.Render("├── ")
		}
	}

	// Name styling
	name := task.Name
	var styledName string
	if task.IsRunning() {
		styledName = lipgloss.NewStyle().Foreground(colorWhite).Bold(true).Render(name)
	} else {
		styledName = grayStyle.Render(name)
	}

	// Duration
	duration := formatDuration(task.Duration(), task.IsRunning())
	var styledDuration string
	if task.IsRunning() {
		styledDuration = runningStyle.Render(duration)
	} else {
		styledDuration = grayStyle.Render(duration)
	}

	// Calculate spacing
	leftPart := prefix + connector + styledSymbol + " " + styledName
	leftLen := len(prefix) + len(connector) + 2 + len(name) // Approximate visible length

	rightPart := styledDuration
	rightLen := len(duration)

	spacing := width - leftLen - rightLen - 4
	if spacing < 1 {
		spacing = 1
	}

	line := leftPart + strings.Repeat(" ", spacing) + rightPart

	// Highlight if focused
	if task == m.focusedTask {
		line = focusedStyle.Render(line)
	}

	return line
}

func (m Model) renderLogPane(width int) string {
	if m.focusedTask == nil {
		return dimStyle.Render("No task selected")
	}

	header := logHeaderStyle.Render(m.focusedTask.Name)
	logs := m.focusedTask.GetLogs()

	if len(logs) == 0 {
		return header + "\n\n" + dimStyle.Render("  No output yet...")
	}

	// Show last N lines that fit
	maxLines := 10
	if len(logs) > maxLines {
		logs = logs[len(logs)-maxLines:]
	}

	var logLines []string
	for _, log := range logs {
		// Truncate long lines
		if len(log) > width-4 {
			log = log[:width-7] + "..."
		}
		logLines = append(logLines, "  "+log)
	}

	return header + "\n\n" + strings.Join(logLines, "\n")
}

// formatDuration formats a duration for display
func formatDuration(d time.Duration, running bool) string {
	if running {
		// MM:SS format for running tasks
		mins := int(d.Minutes())
		secs := int(d.Seconds()) % 60
		return fmt.Sprintf("%02d:%02d", mins, secs)
	}

	// Completed task formatting
	if d < time.Second {
		return fmt.Sprintf("%dms", d.Milliseconds())
	}
	if d < time.Minute {
		return fmt.Sprintf("%.1fs", d.Seconds())
	}
	mins := int(d.Minutes())
	secs := int(d.Seconds()) % 60
	return fmt.Sprintf("%dm %ds", mins, secs)
}

// SendUpdate can be called to trigger a TUI refresh
func SendUpdate(p *tea.Program) {
	if p != nil {
		p.Send(SessionUpdateMsg{})
	}
}
