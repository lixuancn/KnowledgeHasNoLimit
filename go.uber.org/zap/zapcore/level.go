package zapcore

import (
	"errors"
	"fmt"
	"bytes"
)

var errUnmarshalNilLevel = errors.New("can't, unmarshal a nil *Level")

type Level int8

const (
	DEBUG_LEVEL Level = iota - 1
	INFO_LEVEL
	WARN_LEVEL
	ERROR_LEVEL
	DPANIC_LEVEL
	PANIC_LEVEL
	FATAL_LEVEL

	MIN_LEVEL = DEBUG_LEVEL
	MAX_LEVEL = FATAL_LEVEL
)

func (l Level)String()string{
	switch l{
	case DEBUG_LEVEL:
		return "debug"
	case INFO_LEVEL:
		return "info"
	case WARN_LEVEL:
		return "warn"
	case ERROR_LEVEL:
		return "error"
	case DPANIC_LEVEL:
		return "dpanic"
	case PANIC_LEVEL:
		return "panic"
	case FATAL_LEVEL:
		return "fatal"
	default:
		return fmt.Sprintf("Level(%d)", l)
	}
}

func(l Level)CapitalString()string{
	switch l{
	case DEBUG_LEVEL:
		return "DEBUG"
	case INFO_LEVEL:
		return "INFO"
	case WARN_LEVEL:
		return "WARN"
	case ERROR_LEVEL:
		return "ERROR"
	case DPANIC_LEVEL:
		return "DPANIC"
	case PANIC_LEVEL:
		return "PANIC"
	case FATAL_LEVEL:
		return "FATAL"
	default:
		return fmt.Sprintf("LEVEL(%d)", l)
	}
}

func(l Level)MarshalText()([]byte, error){
	return []byte(l.String()), nil
}

func(l *Level)UnmarshalText(text []byte)error{
	if text == nil{
		return errUnmarshalNilLevel
	}
	if !l.unmarshalText(text){
		return fmt.Errorf("unrecognized level: %q", text)
	}
	return nil
}

func(l *Level)unmarshalText(text []byte)bool{
	t := string(bytes.ToLower(text))
	switch t {
	case "debug":
		*l = DEBUG_LEVEL
	case "info":
		*l = INFO_LEVEL
	case "warn":
		*l = WARN_LEVEL
	case "error":
		*l = ERROR_LEVEL
	case "dpanic":
		*l = DPANIC_LEVEL
	case "panic":
		*l = PANIC_LEVEL
	case "fatal":
		*l = FATAL_LEVEL
	default:
		return false
	}
	return true
}

func(l *Level)Set(s string)error{
	return l.UnmarshalText([]byte(s))
}

func(l Level)Get()interface{}{
	return l
}

func(l Level)Enable(lvl Level)bool{
	return lvl >= l
}

type LevelEnabler interface {
	Enabled(Level) bool
}