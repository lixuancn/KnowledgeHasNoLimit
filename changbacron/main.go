package main

import (
	"fmt"
	"lixuancn/changbacron/internal/modules/logger"
	"log"
	"os"
	"path/filepath"
	"sync"
	"github.com/robfig/cron/v3"
	"github.com/urfave/cli"
	macaron "gopkg.in/macaron.v1"
)

func main() {
	cliApp := cli.NewApp()
	cliApp.Name = "gocron"
	cliApp.Usage = "gocron service"
	cliApp.Version = "1.0"
	cliApp.Commands = []cli.Command{
		cli.Command{
			Name:   "web",
			Usage:  "run web server",
			Action: runWeb,
			Flags: []cli.Flag{
				cli.StringFlag{
					Name:  "host",
					Value: "0.0.0.0",
					Usage: "bind host",
				},
				cli.IntFlag{
					Name:  "port,p",
					Value: 5920,
					Usage: "bind port",
				},
				cli.StringFlag{
					Name:  "env,e",
					Value: "prod",
					Usage: "runtime environment, dev|test|prod",
				},
			},
		},
	}
	cliApp.Flags = append(cliApp.Flags, []cli.Flag{}...)
	err := cliApp.Run(os.Args)
	if err != nil {
		log.Fatal(err)
	}
}

func runWeb(ctx *cli.Context) {
	// 设置运行环境
	env := "prod"
	if ctx.IsSet("env") {
		env = ctx.String("env")
	}
	fmt.Println(env)
	switch env {
	case "test":
		macaron.Env = macaron.TEST
	case "dev":
		macaron.Env = macaron.DEV
	default:
		macaron.Env = macaron.PROD
	}
	app.initEnv(AppVersion)
	//// 初始化模块 DB、定时任务等
	//initModule()
	//// 捕捉信号,配置热更新等
	//go catchSignal()
	//m := macaron.Classic()
	//// 注册路由
	//routers.Register(m)
	//// 注册中间件.
	//routers.RegisterMiddleware(m)
	//host := parseHost(ctx)
	//port := parsePort(ctx)
	//m.Run(host, port)
}

// InitEnv 初始化
func initEnv(versionString string) {
	logger.InitLogger()
	var err error
	AppDir, err = goutil.WorkDir()
	if err != nil {
		logger.Fatal(err)
	}
	ConfDir = filepath.Join(AppDir, "/conf")
	LogDir = filepath.Join(AppDir, "/log")
	AppConfig = filepath.Join(ConfDir, "/app.ini")
	VersionFile = filepath.Join(ConfDir, "/.version")
	createDirIfNotExists(ConfDir, LogDir)
	Installed = IsInstalled()
	VersionId = ToNumberVersion(versionString)
}

func crontab(){
	fmt.Println("启动")
	var w sync.WaitGroup
	w.Add(1)
	c := cron.New()
	//c := cron.New(cron.WithSeconds())

	id, err := c.AddFunc("* * * * *", func() { fmt.Println("每分1") })
	fmt.Println(id)
	fmt.Println(err)
	id, err = c.AddFunc("30 * * * * *", func() { fmt.Println("第30秒") })
	fmt.Println(id)
	fmt.Println(err)
	//c.AddFunc("15 16-17,13-14 * * *", func() { fmt.Println("3-6 20-23每30分钟一次"+time.Now().String())})
	//c.AddFunc("@hourly",      func() { fmt.Println("Every hour, starting an hour from now") })
	c.Start()
	//time.Sleep(10*time.Second)
	//id, err = c.AddFunc("* * * * * *", func() { fmt.Println("每秒2") })
	//fmt.Println(id)
	//fmt.Println(err)
	w.Wait()
}