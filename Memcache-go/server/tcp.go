package server

import (
	"fmt"
	"log"
	"net"
)

type TcpServer struct {
	network        string
	host           string
	port           string
	protocol       Protocol
	tcpListener    *net.TCPListener
	clientConnList []net.Conn
}

func NewTcpServer(network, host, port, protocol string) *TcpServer {
	pro, err := GetProtocol(protocol)
	if err != nil {
		log.Fatalf("应用层协议错误")
	}
	return &TcpServer{
		network:  network,
		host:     host,
		port:     port,
		protocol: pro,
	}
}

func (tcp *TcpServer) Run() {
	fmt.Println("TCP服务启动中...")
	tcpAddr, err := net.ResolveTCPAddr(tcp.network, tcp.host+":"+tcp.port)
	if err != nil {
		log.Fatalf("构造TCP失败")
	}
	tcpListener, err := net.ListenTCP(tcp.network, tcpAddr)
	if err != nil {
		log.Fatalf("TCP监听失败")
	}
	tcp.tcpListener = tcpListener
	defer tcpListener.Close()
	log.Println("TCP服务启动完成")
	tcp.loop()
}

func (tcp *TcpServer) loop() {
	log.Println("TCP服务等待链接")
	for {
		clientConn, err := tcp.tcpListener.AcceptTCP()
		if err != nil {
			log.Println("接受连接失败" + err.Error())
			continue
		}
		log.Println("接收新连接: " + clientConn.RemoteAddr().String())
		tcp.clientConnList = append(tcp.clientConnList, clientConn)
		go tcp.Handle(clientConn)
	}
}

func (tcp *TcpServer) Handle(clientConn net.Conn) {
	defer func() {
		fmt.Println("断开连接：" + clientConn.RemoteAddr().String())
		clientConn.Close()
	}()
	tcp.protocol.Handle(clientConn)
}
