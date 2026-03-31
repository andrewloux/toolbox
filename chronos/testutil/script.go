package testutil

import (
	"fmt"
	"strings"
)

// Op represents a single operation in a test script.
type Op interface {
	// Render returns the shell command for this operation.
	Render(binary string) string
}

// startOp implements "chronos start <name>"
type startOp struct {
	name string
}

func (o *startOp) Render(binary string) string {
	return fmt.Sprintf("%s start %s", binary, shellQuote(o.name))
}

// endOp implements "chronos end [name]"
type endOp struct {
	name string
}

func (o *endOp) Render(binary string) string {
	if o.name == "" {
		return binary + " end"
	}
	return fmt.Sprintf("%s end %s", binary, shellQuote(o.name))
}

// failOp implements "chronos fail [name]"
type failOp struct {
	name string
}

func (o *failOp) Render(binary string) string {
	if o.name == "" {
		return binary + " fail"
	}
	return fmt.Sprintf("%s fail %s", binary, shellQuote(o.name))
}

// logOp implements "chronos log <message>"
type logOp struct {
	message string
}

func (o *logOp) Render(binary string) string {
	return fmt.Sprintf("%s log %s", binary, shellQuote(o.message))
}

// ExecOp implements "chronos exec [name] -- <command...>"
type ExecOp struct {
	name string
	args []string
}

// Cmd sets the command to execute.
func (o *ExecOp) Cmd(args ...string) *ExecOp {
	o.args = args
	return o
}

// CmdString sets the command from a string (passed to sh -c).
func (o *ExecOp) CmdString(cmd string) *ExecOp {
	o.args = []string{"sh", "-c", cmd}
	return o
}

func (o *ExecOp) Render(binary string) string {
	var sb strings.Builder
	sb.WriteString(binary)
	sb.WriteString(" exec")

	if o.name != "" {
		sb.WriteString(" ")
		sb.WriteString(shellQuote(o.name))
	}

	sb.WriteString(" --")

	for _, arg := range o.args {
		sb.WriteString(" ")
		sb.WriteString(shellQuote(arg))
	}

	return sb.String()
}

// shellOp is a raw shell command
type shellOp struct {
	command string
}

func (o *shellOp) Render(binary string) string {
	return o.command
}

// CompositeOp groups multiple operations (useful for parallel subshells, etc.)
type CompositeOp struct {
	ops []Op
}

func (o *CompositeOp) Render(binary string) string {
	var lines []string
	for _, op := range o.ops {
		lines = append(lines, op.Render(binary))
	}
	return strings.Join(lines, "\n")
}

// Subshell wraps operations in a subshell (for parallel execution tests)
type Subshell struct {
	ops        []Op
	background bool
}

// SubshellOp creates a subshell containing the given operations.
func SubshellOp(ops ...Op) *Subshell {
	return &Subshell{ops: ops}
}

// Background makes the subshell run in background (&)
func (s *Subshell) Background() *Subshell {
	s.background = true
	return s
}

func (s *Subshell) Render(binary string) string {
	var sb strings.Builder
	sb.WriteString("(\n")
	for _, op := range s.ops {
		sb.WriteString("  ")
		sb.WriteString(op.Render(binary))
		sb.WriteString("\n")
	}
	sb.WriteString(")")
	if s.background {
		sb.WriteString(" &")
	}
	return sb.String()
}

// WaitOp creates a "wait" command (for parallel subshells)
type WaitOp struct{}

func (o *WaitOp) Render(binary string) string {
	return "wait"
}

// Wait creates a wait command.
func Wait() Op {
	return &WaitOp{}
}

// shellQuote quotes a string for safe shell usage.
func shellQuote(s string) string {
	// If it's simple, no quoting needed
	if isSimpleShellString(s) {
		return s
	}
	// Use single quotes, escaping any single quotes in the string
	return "'" + strings.ReplaceAll(s, "'", "'\"'\"'") + "'"
}

func isSimpleShellString(s string) bool {
	for _, c := range s {
		if !isSimpleShellChar(c) {
			return false
		}
	}
	return len(s) > 0
}

func isSimpleShellChar(c rune) bool {
	return (c >= 'a' && c <= 'z') ||
		(c >= 'A' && c <= 'Z') ||
		(c >= '0' && c <= '9') ||
		c == '_' || c == '-' || c == '.' || c == '/'
}
