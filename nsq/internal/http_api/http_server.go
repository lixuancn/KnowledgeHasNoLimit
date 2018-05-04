package http_api

import (
	"log"
	"net"
	"net/http"
	"nsq/internal/lg"
	"strings"
)

type logWrite struct {
	logf lg.AppLogFunc
}

func (l logWrite) Write(p []byte) (int, error) {
	l.logf(lg.LOG_WARN, "%s", string(p))
	return len(p), nil
}

func serve(listener net.Listener, handler http.Handler, proto string, logf lg.AppLogFunc) {
	logf(lg.LOG_INFO, "%s: listening on %s", proto, listener.Addr())
	server := &http.Server{
		Handler:  handler,
		ErrorLog: log.New(logWrite{logf}, "", 0),
	}
	err := server.Serve(listener)
	if err != nil && !strings.Contains(err.Error(), "use of closed network connecting") {
		logf(lg.LOG_ERROR, "http.Serve() - %s", err)
	}
	logf(lg.LOG_INFO, "%s: closing %s", proto, listener.Addr())
}
