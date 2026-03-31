package artifact

import (
	"fmt"
	"strings"

	"github.com/andrewloux/toolbox/chronos/internal/session"
)

// Colors (ANSI escape codes)
const (
	colorReset   = "\033[0m"
	colorGreen   = "\033[32m"
	colorRed     = "\033[31m"
	colorYellow  = "\033[33m"
	colorDim     = "\033[90m"
	colorBold    = "\033[1m"
	colorDimRed  = "\033[91m"
)

// Generate creates the artifact output for a completed session
func Generate(sess *session.Session, noColor bool) string {
	width := 64 // Fixed width for artifact

	// Calculate stats
	var failed, total int
	var hasFailed, hasAborted bool
	countTasks(sess.Root, &failed, &total, &hasFailed, &hasAborted)

	// Don't count root in totals
	total--

	// Determine overall status
	status := "SUCCESS"
	statusColor := colorGreen
	if hasAborted {
		status = "ABORTED"
		statusColor = colorYellow
	} else if hasFailed {
		status = fmt.Sprintf("FAILED (%d/%d)", failed, total)
		statusColor = colorRed
	}

	// Build artifact
	var sb strings.Builder

	// Header
	totalDuration := formatArtifactDuration(sess.Root.Duration())
	headerText := sess.ScriptName
	headerRight := totalDuration

	headerPadding := width - len(headerText) - len(headerRight) - 6
	if headerPadding < 1 {
		headerPadding = 1
	}

	header := fmt.Sprintf("┌─ %s %s %s ─┐",
		headerText,
		strings.Repeat("─", headerPadding),
		headerRight,
	)
	sb.WriteString(applyColor(colorDim, header, noColor))
	sb.WriteString("\n")

	// Empty line
	sb.WriteString(applyColor(colorDim, "│", noColor))
	sb.WriteString(strings.Repeat(" ", width-2))
	sb.WriteString(applyColor(colorDim, "│", noColor))
	sb.WriteString("\n")

	// Tasks (skip root, show children)
	for _, child := range sess.Root.Children {
		renderArtifactTask(&sb, child, "", width, noColor)
	}

	// Empty line
	sb.WriteString(applyColor(colorDim, "│", noColor))
	sb.WriteString(strings.Repeat(" ", width-2))
	sb.WriteString(applyColor(colorDim, "│", noColor))
	sb.WriteString("\n")

	// Footer
	footerPadding := width - len(status) - 4
	sb.WriteString(applyColor(colorDim, "└"+strings.Repeat("─", footerPadding-1)+" ", noColor))
	sb.WriteString(applyColor(statusColor+colorBold, status, noColor))
	sb.WriteString(applyColor(colorDim, " ─┘", noColor))
	sb.WriteString("\n")

	return sb.String()
}

func renderArtifactTask(sb *strings.Builder, task *session.Task, indent string, width int, noColor bool) {
	// Determine symbol and colors
	var symbol, symbolColor, nameColor, durationText string

	switch task.State {
	case session.StateSuccess:
		if noColor {
			symbol = "[OK]"
		} else {
			symbol = "✓"
		}
		symbolColor = colorGreen
		nameColor = colorGreen
		durationText = formatArtifactDuration(task.Duration())

	case session.StateFailure:
		if noColor {
			symbol = "[FAIL]"
		} else {
			symbol = "✗"
		}
		symbolColor = colorRed
		nameColor = colorRed
		durationText = formatArtifactDuration(task.Duration())

	case session.StateAborted:
		if noColor {
			symbol = "[ABORT]"
		} else {
			symbol = "⚠"
		}
		symbolColor = colorYellow
		nameColor = colorYellow
		durationText = "aborted"

	default:
		symbol = "○"
		symbolColor = colorDim
		nameColor = colorDim
		durationText = "-"
	}

	// Build line
	sb.WriteString(applyColor(colorDim, "│", noColor))
	sb.WriteString("  ")
	sb.WriteString(indent)
	sb.WriteString(applyColor(symbolColor, symbol, noColor))
	sb.WriteString(" ")
	sb.WriteString(applyColor(nameColor, task.Name, noColor))
	sb.WriteString(" ")

	// Calculate dotted leader
	usedWidth := 4 + len(indent) + len(symbol) + 1 + len(task.Name) + 1 + len(durationText) + 2
	dots := width - usedWidth
	if dots < 3 {
		dots = 3
	}

	// Only show dots for successful tasks
	if task.State == session.StateSuccess {
		sb.WriteString(applyColor(colorDim, strings.Repeat(".", dots), noColor))
	} else {
		sb.WriteString(strings.Repeat(" ", dots))
	}

	sb.WriteString(" ")
	if task.State == session.StateSuccess {
		sb.WriteString(applyColor(colorDim, durationText, noColor))
	} else {
		sb.WriteString(applyColor(symbolColor, durationText, noColor))
	}
	sb.WriteString("  ")
	sb.WriteString(applyColor(colorDim, "│", noColor))
	sb.WriteString("\n")

	// For failed tasks, show last few lines of output
	if task.State == session.StateFailure {
		logs := task.GetLogs()
		if len(logs) > 5 {
			logs = logs[len(logs)-5:]
		}

		for _, log := range logs {
			// Truncate log line
			maxLogLen := width - 12 - len(indent)
			if len(log) > maxLogLen {
				log = log[:maxLogLen-3] + "..."
			}

			sb.WriteString(applyColor(colorDim, "│", noColor))
			sb.WriteString("     ")
			sb.WriteString(indent)
			sb.WriteString(applyColor(colorDimRed, "└─ "+log, noColor))

			// Pad to border
			padding := width - 8 - len(indent) - len(log)
			if padding > 0 {
				sb.WriteString(strings.Repeat(" ", padding))
			}
			sb.WriteString(applyColor(colorDim, "│", noColor))
			sb.WriteString("\n")
		}

		// Show exit code if it's a command
		if task.ExitCode != 0 {
			exitLine := fmt.Sprintf("exit code %d", task.ExitCode)
			sb.WriteString(applyColor(colorDim, "│", noColor))
			sb.WriteString("     ")
			sb.WriteString(indent)
			sb.WriteString(applyColor(colorDimRed, "└─ "+exitLine, noColor))

			padding := width - 8 - len(indent) - len(exitLine)
			if padding > 0 {
				sb.WriteString(strings.Repeat(" ", padding))
			}
			sb.WriteString(applyColor(colorDim, "│", noColor))
			sb.WriteString("\n")
		}
	}

	// Recursively render children if:
	// - Parent failed/aborted, OR
	// - Any child (or descendant) failed/aborted
	if task.State != session.StateSuccess || hasFailedDescendants(task) {
		for _, child := range task.Children {
			renderArtifactTask(sb, child, indent+"   ", width, noColor)
		}
	}
}

// hasFailedDescendants checks if any child (recursive) is failed or aborted
func hasFailedDescendants(task *session.Task) bool {
	for _, child := range task.Children {
		if child.State == session.StateFailure || child.State == session.StateAborted {
			return true
		}
		if hasFailedDescendants(child) {
			return true
		}
	}
	return false
}

func countTasks(task *session.Task, failed, total *int, hasFailed, hasAborted *bool) {
	*total++

	switch task.State {
	case session.StateFailure:
		*failed++
		*hasFailed = true
	case session.StateAborted:
		*hasAborted = true
	}

	for _, child := range task.Children {
		countTasks(child, failed, total, hasFailed, hasAborted)
	}
}

func formatArtifactDuration(d interface{}) string {
	var dur float64
	switch v := d.(type) {
	case float64:
		dur = v
	case interface{ Seconds() float64 }:
		dur = v.Seconds()
	default:
		return "-"
	}

	if dur < 1 {
		return fmt.Sprintf("%dms", int(dur*1000))
	}
	if dur < 60 {
		return fmt.Sprintf("%.1fs", dur)
	}

	mins := int(dur / 60)
	secs := int(dur) % 60
	return fmt.Sprintf("%dm %ds", mins, secs)
}

func applyColor(color, text string, noColor bool) string {
	if noColor {
		return text
	}
	return color + text + colorReset
}

// GeneratePlain generates artifact without colors
func GeneratePlain(sess *session.Session) string {
	return Generate(sess, true)
}
