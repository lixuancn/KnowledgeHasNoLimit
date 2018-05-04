package writers

import (
	"io"
	"time"
)

type SpreadWrite struct {
	w        io.Writer
	interval time.Duration
	buf      [][]byte
}

func NewSpreadWrite(w io.Writer, interval time.Duration) *SpreadWrite {
	return &SpreadWrite{
		w:        w,
		interval: interval,
		buf:      make([][]byte, 0),
	}
}

func (s *SpreadWrite) Write(p []byte) (int, error) {
	b := make([]byte, len(p))
	copy(b, p)
	s.buf = append(s.buf, b)
	return len(p), nil
}

func (s *SpreadWrite) Flush() {
	sleep := s.interval / time.Duration(len(s.buf))
	for _, b := range s.buf {
		start := time.Now()
		s.w.Write(b)
		latency := time.Now().Sub(start)
		time.Sleep(sleep - latency)
	}
	s.buf = s.buf[:0]
}
