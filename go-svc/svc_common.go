package svc

import (
	"context"
	"os"
	"syscall"
)

func Run(service Service, sig ...os.Signal) error{
	env := environment{}
	if err := service.Init(env); err != nil{
		return err
	}
	if err := service.Start(); err != nil{
		return err
	}
	if len(sig) == 0{
		sig = []os.Signal{syscall.SIGINT, syscall.SIGTERM}
	}
	signalChan := make(chan os.Signal, 1)
	signalNotify(signalChan, sig...)
	var ctx context.Context
	if s, ok := service.(Context); ok{
		ctx = s.Context()
	}else{
		ctx = context.Background()
	}
	select{
	case <- signalChan:
	case <- ctx.Done():
	}
	return service.Stop()
}

type environment struct{}

func (environment) IsWindowsService()bool{
	return false
}