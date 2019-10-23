package main

import (
	"fmt"
	"github.com/robfig/cron/v3"
	"sync"
)

func main(){
	fmt.Println("启动")
	var w sync.WaitGroup
	w.Add(1)
	c := cron.New()
	//c := cron.New(cron.WithSeconds())

	id, err := c.AddFunc("* * * * *", func() { fmt.Println("每秒1") })
	fmt.Println(id)
	fmt.Println(err)
	//id, err = c.AddFunc("30 * * * * *", func() { fmt.Println("第30秒") })
	//fmt.Println(id)
	//fmt.Println(err)
	//c.AddFunc("15 16-17,13-14 * * *", func() { fmt.Println("3-6 20-23每30分钟一次"+time.Now().String())})
	//c.AddFunc("@hourly",      func() { fmt.Println("Every hour, starting an hour from now") })
	c.Start()
	//time.Sleep(10*time.Second)
	//id, err = c.AddFunc("* * * * * *", func() { fmt.Println("每秒2") })
	//fmt.Println(id)
	//fmt.Println(err)
	w.Wait()
}