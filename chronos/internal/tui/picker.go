package tui

import (
	"strings"

	"github.com/andrewloux/toolbox/chronos/internal/session"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/sahilm/fuzzy"
)

// PickerResult is sent when user makes a selection
type PickerResult struct {
	Task     *session.Task
	Canceled bool
}

// PickerModel is the interactive task picker
type PickerModel struct {
	tasks        []*session.Task
	filtered     []*session.Task
	matches      []fuzzy.Match
	cursor       int
	filter       string
	action       string // "end" or "fail"
	width        int
	height       int
	selected     *session.Task
	canceled     bool
	done         bool
}

// NewPickerModel creates a new picker
func NewPickerModel(tasks []*session.Task, action string) PickerModel {
	return PickerModel{
		tasks:    tasks,
		filtered: tasks,
		action:   action,
	}
}

// Init initializes the picker
func (m PickerModel) Init() tea.Cmd {
	return nil
}

// Update handles picker input
func (m PickerModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "up", "k":
			if m.cursor > 0 {
				m.cursor--
			}

		case "down", "j":
			if m.cursor < len(m.filtered)-1 {
				m.cursor++
			}

		case "enter":
			if len(m.filtered) > 0 && m.cursor < len(m.filtered) {
				m.selected = m.filtered[m.cursor]
				m.done = true
				return m, tea.Quit
			}

		case "esc":
			m.canceled = true
			m.done = true
			return m, tea.Quit

		case "backspace":
			if len(m.filter) > 0 {
				m.filter = m.filter[:len(m.filter)-1]
				m.updateFilter()
			}

		default:
			if len(msg.String()) == 1 && msg.String() >= " " {
				m.filter += msg.String()
				m.updateFilter()
			}
		}

	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
	}

	return m, nil
}

func (m *PickerModel) updateFilter() {
	if m.filter == "" {
		m.filtered = m.tasks
		m.matches = nil
		m.cursor = 0
		return
	}

	// Create searchable strings
	var names []string
	for _, t := range m.tasks {
		names = append(names, t.Name)
	}

	// Fuzzy match
	m.matches = fuzzy.Find(m.filter, names)

	m.filtered = make([]*session.Task, len(m.matches))
	for i, match := range m.matches {
		m.filtered[i] = m.tasks[match.Index]
	}

	if m.cursor >= len(m.filtered) {
		m.cursor = len(m.filtered) - 1
	}
	if m.cursor < 0 {
		m.cursor = 0
	}
}

// View renders the picker
func (m PickerModel) View() string {
	if m.done {
		return ""
	}

	// Styles
	boxStyle := lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(colorDim).
		Padding(1, 2)

	headerStyle := lipgloss.NewStyle().
		Foreground(colorWhite).
		Bold(true)

	selectedStyle := lipgloss.NewStyle().
		Background(colorFocus).
		Foreground(colorWhite)

	normalStyle := lipgloss.NewStyle().
		Foreground(colorGray)

	// Header
	action := "End"
	if m.action == "fail" {
		action = "Fail"
	}
	header := headerStyle.Render(action + " which task?")
	if m.filter != "" {
		header += " " + dimStyle.Render("> "+m.filter)
	}

	// Task list
	var lines []string
	for i, task := range m.filtered {
		symbol := runningStyle.Render("●")
		duration := formatDuration(task.Duration(), true)

		name := task.Name

		// Highlight fuzzy matches
		if m.filter != "" && i < len(m.matches) {
			name = highlightMatches(task.Name, m.matches[i].MatchedIndexes)
		}

		line := "   " + symbol + " " + name

		// Pad to align duration
		padding := 40 - len(task.Name) - 5
		if padding < 1 {
			padding = 1
		}
		line += strings.Repeat(" ", padding) + runningStyle.Render(duration)

		if i == m.cursor {
			line = selectedStyle.Render(" ❯" + line[2:])
		} else {
			line = normalStyle.Render(line)
		}

		lines = append(lines, line)
	}

	if len(lines) == 0 {
		lines = append(lines, dimStyle.Render("   No matching tasks"))
	}

	content := header + "\n\n" + strings.Join(lines, "\n")

	return boxStyle.Render(content)
}

func highlightMatches(s string, indexes []int) string {
	if len(indexes) == 0 {
		return s
	}

	// Create a set of matched indexes
	matchSet := make(map[int]bool)
	for _, idx := range indexes {
		matchSet[idx] = true
	}

	// Build highlighted string
	var result strings.Builder
	boldStyle := lipgloss.NewStyle().Bold(true).Underline(true)

	for i, c := range s {
		if matchSet[i] {
			result.WriteString(boldStyle.Render(string(c)))
		} else {
			result.WriteRune(c)
		}
	}

	return result.String()
}

// Result returns the picker result
func (m PickerModel) Result() PickerResult {
	return PickerResult{
		Task:     m.selected,
		Canceled: m.canceled,
	}
}

// RunPicker runs the interactive picker
func RunPicker(tasks []*session.Task, action string) (*session.Task, bool, error) {
	model := NewPickerModel(tasks, action)
	p := tea.NewProgram(model)

	finalModel, err := p.Run()
	if err != nil {
		return nil, false, err
	}

	result := finalModel.(PickerModel).Result()
	return result.Task, result.Canceled, nil
}
