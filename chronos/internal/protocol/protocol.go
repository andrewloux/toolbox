package protocol

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"sync"
)

// EventType represents the type of event
type EventType string

const (
	EventStart EventType = "start"
	EventEnd   EventType = "end"
	EventLog   EventType = "log"
)

// Event represents a message sent over the socket
type Event struct {
	Type     EventType `json:"type"`
	ID       string    `json:"id"`
	Name     string    `json:"name,omitempty"`
	Parent   string    `json:"parent,omitempty"`
	Status   string    `json:"status,omitempty"`
	Code     int       `json:"code,omitempty"`
	Line     string    `json:"line,omitempty"`
	Response *Response `json:"response,omitempty"`
}

// Response is sent back to clients
type Response struct {
	Success bool   `json:"success"`
	TaskID  string `json:"task_id,omitempty"`
	Error   string `json:"error,omitempty"`
}

// Server handles socket communication for a session
type Server struct {
	socketPath string
	listener   net.Listener
	handler    EventHandler
	done       chan struct{}
	wg         sync.WaitGroup
}

// EventHandler processes incoming events
type EventHandler interface {
	HandleEvent(event *Event) *Response
}

// NewServer creates a new protocol server
func NewServer(socketPath string, handler EventHandler) *Server {
	return &Server{
		socketPath: socketPath,
		handler:    handler,
		done:       make(chan struct{}),
	}
}

// Start begins listening on the socket
func (s *Server) Start() error {
	// Remove existing socket if any
	os.Remove(s.socketPath)

	var err error
	s.listener, err = net.Listen("unix", s.socketPath)
	if err != nil {
		return fmt.Errorf("failed to listen on socket: %w", err)
	}

	s.wg.Add(1)
	go s.acceptLoop()

	return nil
}

func (s *Server) acceptLoop() {
	defer s.wg.Done()

	for {
		select {
		case <-s.done:
			return
		default:
		}

		conn, err := s.listener.Accept()
		if err != nil {
			select {
			case <-s.done:
				return
			default:
				continue
			}
		}

		s.wg.Add(1)
		go s.handleConnection(conn)
	}
}

func (s *Server) handleConnection(conn net.Conn) {
	defer s.wg.Done()
	defer conn.Close()

	reader := bufio.NewReader(conn)
	line, err := reader.ReadBytes('\n')
	if err != nil {
		return
	}

	var event Event
	if err := json.Unmarshal(line, &event); err != nil {
		resp := &Response{Success: false, Error: "invalid JSON"}
		s.sendResponse(conn, resp)
		return
	}

	resp := s.handler.HandleEvent(&event)
	s.sendResponse(conn, resp)
}

func (s *Server) sendResponse(conn net.Conn, resp *Response) {
	data, _ := json.Marshal(resp)
	conn.Write(append(data, '\n'))
}

// Stop shuts down the server
func (s *Server) Stop() {
	close(s.done)
	if s.listener != nil {
		s.listener.Close()
	}
	s.wg.Wait()
	os.Remove(s.socketPath)
}

// Client sends events to a session server
type Client struct {
	socketPath string
}

// NewClient creates a new client
func NewClient(socketPath string) *Client {
	return &Client{socketPath: socketPath}
}

// NewClientFromEnv creates a client using environment variables
func NewClientFromEnv() (*Client, error) {
	socketPath := os.Getenv("CHRONOS_SOCK")
	if socketPath == "" {
		return nil, fmt.Errorf("no active session. Use: chronos run ./script.sh")
	}
	return NewClient(socketPath), nil
}

// Send sends an event and waits for response
func (c *Client) Send(event *Event) (*Response, error) {
	conn, err := net.Dial("unix", c.socketPath)
	if err != nil {
		return nil, fmt.Errorf("cannot connect to Chronos session: %w", err)
	}
	defer conn.Close()

	data, err := json.Marshal(event)
	if err != nil {
		return nil, err
	}

	_, err = conn.Write(append(data, '\n'))
	if err != nil {
		return nil, err
	}

	reader := bufio.NewReader(conn)
	line, err := reader.ReadBytes('\n')
	if err != nil {
		return nil, err
	}

	var resp Response
	if err := json.Unmarshal(line, &resp); err != nil {
		return nil, err
	}

	return &resp, nil
}

// StartTask sends a start event
func (c *Client) StartTask(name, parentID string) (*Response, error) {
	return c.Send(&Event{
		Type:   EventStart,
		Name:   name,
		Parent: parentID,
	})
}

// EndTask sends an end event
func (c *Client) EndTask(taskID, status string, code int) (*Response, error) {
	return c.Send(&Event{
		Type:   EventEnd,
		ID:     taskID,
		Status: status,
		Code:   code,
	})
}

// Log sends a log event
func (c *Client) Log(taskID, line string) (*Response, error) {
	return c.Send(&Event{
		Type: EventLog,
		ID:   taskID,
		Line: line,
	})
}
