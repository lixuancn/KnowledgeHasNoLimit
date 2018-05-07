package nsqlookupd

import (
	"sync"
	"net"
	"nsq/internal/util"
)

type NSQLookupd struct {
	sync.RWMutex
	opts *Options
	tcpListener net.Listener
	httpListener net.Listener
	waitGroup util.WaitGroupWrapper
	DB *RegisterationDB
}