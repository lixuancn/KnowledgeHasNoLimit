package color

import "fmt"

const (
	BLACK Color = iota + 30
	RED
	GREEN
	YELLOW
	BULE
	MAGENTA
	CYAN
	WHITE
)

type Color uint8

func (c Color)Add(s string)string{
	return fmt.Sprintf("\x1b[%dm%s\x1b[0m", uint8(c), s)
}