package main

import (
	"github.com/judwhite/go-svc/svc"
	"log"
	"syscall"
	"fmt"
)

type program struct {
}

func main() {
	fmt.Println("启动NSQ:")
	prg := &program{}
	if err := svc.Run(prg, syscall.SIGINT, syscall.SIGTERM); err != nil {
		log.Fatal(err)
	}
}

func (this *program) Init(s svc.Environment) error {
	return nil
}

func (this *program) Start() error {
	return nil
}

func (this *program) Stop() error {
	return nil
}
