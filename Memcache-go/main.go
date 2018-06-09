package main

import (
	"Memcache-go/server"
)

const TCP_NETWORK = "tcp"
const TCP_HOST = "127.0.0.1"
const TCP_PORT = "19910"
const TCP_PROTOCOL = "memcache"

func main(){
	tcpServer := server.NewTcpServer(TCP_NETWORK, TCP_HOST, TCP_PORT, TCP_PROTOCOL)
	tcpServer.Run()
}