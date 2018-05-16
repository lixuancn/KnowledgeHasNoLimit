package lg

import (
	"fmt"
	"strings"
)

type LogLevel int

const (
	LOG_DEBUG = LogLevel(1)
	LOG_INFO  = LogLevel(2)
	LOG_WARN  = LogLevel(3)
	LOG_ERROR = LogLevel(4)
	LOG_FATAL = LogLevel(5)
)

type AppLogFunc func(lvl LogLevel, f string, args ...interface{})

type Logger interface {
	Output(maxdepth int, s string) error
}

type NilLogger struct{}

func (l NilLogger) Output(maxdepath int, s string) error {
	return nil
}

func (l LogLevel) String() string {
	switch l {
	case LOG_DEBUG:
		return "DEBUG"
	case LOG_INFO:
		return "INFO"
	case LOG_WARN:
		return "WARN"
	case LOG_ERROR:
		return "ERROR"
	case LOG_FATAL:
		return "FATAL"
	}
	panic("invalid LogLevel")
}

func ParseLogLevel(levelstr string, verbose bool) (LogLevel, error) {
	lvl := LOG_INFO
	levelstr = strings.ToUpper(levelstr)
	switch levelstr {
	case "DEBUG":
		lvl = LOG_DEBUG
	case "INFO":
		lvl = LOG_INFO
	case "WARN":
		lvl = LOG_WARN
	case "ERROR":
		lvl = LOG_ERROR
	case "FATAL":
		lvl = LOG_FATAL
	default:
		return lvl, fmt.Errorf("invalid log-level '%s'", levelstr)
	}
	if verbose {
		lvl = LOG_DEBUG
	}
	return lvl, nil
}

func Logf(logger Logger, cfgLevel LogLevel, msgLevel LogLevel, f string, args ...interface{}) {
	if cfgLevel > msgLevel {
		return
	}
	logger.Output(3, fmt.Sprintf(msgLevel.String()+": "+f, args))
}
