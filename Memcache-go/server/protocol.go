package server

import (
	"github.com/go-errors/errors"
	"net"
	"strings"
)

type Protocol interface {
	Handle(conn net.Conn)
	parse(message string) (bool, error)
}

func GetProtocol(protocol string) (Protocol, error) {
	switch strings.ToLower(protocol) {
	case "memcache":
		return NewMemcache(), nil
	}
	return nil, errors.New("协议未实现")
}
