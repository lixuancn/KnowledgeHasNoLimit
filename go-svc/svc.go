package svc

import (
	"context"
	"os/signal"
)

var signalNotify = signal.Notify

type Service interface {
	Init(environment Environment) error
	//Init之后调用，不可以被block
	Start() error
	Stop() error
}

type Context interface {
	Context() context.Context
}

type Environment interface {
	IsWindowsService() bool
}