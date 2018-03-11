package main

import (
	"time"
	"log"
	"github.com/davecgh/go-spew/spew"
	"net"
	"io"
	"bufio"
	"strconv"
	"sync"
	"encoding/json"
	"github.com/joho/godotenv"
	"os"
)

//待同步的区块
var bcServer chan []Block

var mutexTcp = sync.Mutex{}

func runTcp()error{
	//待同步的区块
	bcServer = make(chan []Block)

	//TCP监听
	err := godotenv.Load()
	if err != nil{
		log.Fatal(err)
	}
	addr := os.Getenv("ADDR")
	server, err := net.Listen("tcp", ":" + addr)
	if err != nil{
		log.Fatal(err)
	}
	defer server.Close()
	for{
		conn, err := server.Accept()
		if err != nil{
			log.Fatal(err)
		}
		go handleConn(conn)
	}
	return nil
}

func handleConn(conn net.Conn){
	defer conn.Close()
	//新增一个心跳
	go func(){
		io.WriteString(conn, "请输入一个心跳数：")
		scanner := bufio.NewScanner(conn)
		for scanner.Scan(){
			//获取一个新的值
			bpm, err := strconv.Atoi(scanner.Text())
			if err != nil{
				log.Printf("%v not a number: %v", scanner.Text(), err)
				continue
			}
			//生成一个新块
			oldBlock := Blockchains[len(Blockchains)-1]
			newBlock := generateBlock(oldBlock, bpm)
			if isBlockValid(oldBlock, newBlock){
				newBlockchains := append(Blockchains, newBlock)
				replaceChain(newBlockchains)
				bcServer <- Blockchains
				io.WriteString(conn, "\n请输入一个新值：")
			}
		}
	}()
	//广播出去
	go func(){
		for{
			time.Sleep(30 * time.Second)
			mutexTcp.Lock()
			output, err := json.Marshal(Blockchains)
			if err != nil{
				log.Fatal(err)
			}
			mutexTcp.Unlock()
			io.WriteString(conn, string(output))
		}
	}()
	for _ = range bcServer{
		spew.Dump(Blockchains)
	}
}