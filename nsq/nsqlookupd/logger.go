package nsqlookupd

import "nsq/internal/lg"

type Logger lg.Logger

const (
	LOG_DEBUG = lg.LOG_DEBUG
	LOG_INFO = lg.LOG_INFO
	LOG_WARN = lg.LOG_WARN
	LOG_ERROR = lg.LOG_ERROR
	LOG_FATAL = lg.LOG_FATAL
)

func (n *NSQLookupd) logf(level lg.LogLevel, f string, args ...interface{}){
	lg.Logf(n.opts.Logger, n.opts.logLevel, level, f, args...)
}