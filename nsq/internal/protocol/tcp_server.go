package protocol

import (
	"net"
	"nsq/internal/lg"
	"runtime"
	"strings"
)

type TCPHandler interface {
	Handle(conn net.Conn)
}

func TCPServer(listener net.Listener, handler TCPHandler, logf lg.AppLogFunc) {
	logf(lg.LOG_INFO, "TCP: listen on %s", listener.Addr())
	for {
		clientConn, err := listener.Accept()
		if err != nil {
			if nerr, ok := err.(net.Error); ok && nerr.Temporary() {
				logf(lg.LOG_WARN, "temporary Accept() failure - %s", err)
				runtime.Gosched()
				continue
			}
			if !strings.Contains(err.Error(), "use of closed network connection") {
				logf(lg.LOG_ERROR, "listener.Accept() - %s", err)
			}
			break
		}
		go handler.Handle(clientConn)
	}
	logf(lg.LOG_INFO, "TCP: closing %s", listener.Addr())
}
