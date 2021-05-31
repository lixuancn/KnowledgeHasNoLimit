package main

import (
	"context"
	"log"
	"os"
	"sync"
	"time"
	"lixuancn/go-svc"
)

type program struct{
	logFile *os.File
	svr *server
	ctx context.Context
}

func (p *program)Context()context.Context{
	return p.ctx
}

func main(){
	ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Minute)
	defer cancel()
	prg := program{
		logFile: os.Stdout,
		svr:     &server{},
		ctx:     ctx,
	}
	defer func(){
		if err := prg.logFile.Close(); err != nil{
			log.Printf("error closing '%s': %v\n", prg.logFile.Name(), err)
		}
	}()
	if err := svc.Run(&prg); err != nil{
		log.Fatalln(err.Error())
	}
}

func (p *program)Init(env svc.Environment)error{
	return nil
}

func (p *program)Start()error{
	log.Println("Starting...")
	go p.svr.start()
	log.Println("Started...")
	return nil
}

func (p *program)Stop()error{
	log.Println("Stopping...")
	if err := p.svr.stop(); err != nil{
		return err
	}
	log.Println("Stopped...")
	return nil
}


type server struct{
	data chan int
	exit chan struct{}
	wg sync.WaitGroup
}

func (s *server)start(){
	s.data = make(chan int)
	s.exit = make(chan struct{})
	s.wg.Add(2)
	go s.startSender()
	go s.startReceiver()
}

func (s *server)stop()error{
	close(s.exit)
	log.Println("wg.Wait()")
	s.wg.Wait()
	return nil
}

func (s *server)startSender(){
	ticker := time.NewTicker(20 * time.Millisecond)
	defer s.wg.Done()
	count := 1
	for {
		select{
		case <- ticker.C:
			select{
			case s.data <- count:
				count++
			case <- s.exit:
				return
			}
		case <- s.exit:
			return
		}
	}
}

func (s *server)startReceiver(){
	defer s.wg.Done()
	for{
		select{
		case n := <- s.data:
			log.Printf("计数%d\n", n)
		case <- s.exit:
			return
		}
	}
}