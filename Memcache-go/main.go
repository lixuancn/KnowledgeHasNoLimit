package main

import (
	"net"
	"fmt"
	"bufio"
	"strings"
)


func main(){
	tcpAddr, err := net.ResolveTCPAddr("tcp", "127.0.0.1:19910")
	if err != nil{
		fmt.Println(err)
		return
	}
	tcpListener, err := net.ListenTCP("tcp", tcpAddr)
	if err != nil{
		fmt.Println(err)
		return
	}
	defer tcpListener.Close()
	fmt.Println("tcp开启")
	for {
		clientConn, err := tcpListener.AcceptTCP()
		if err != nil{
			fmt.Println(err)
			continue
		}
		fmt.Println("新连接: " + clientConn.RemoteAddr().String())
		go tcpPipe(clientConn)
	}
}

func tcpPipe(conn *net.TCPConn){
	ipStr := conn.RemoteAddr().String()
	defer func(){
		fmt.Println("断开连接：" + ipStr)
		conn.Close()
	}()
	reader := bufio.NewReader(conn)
	message := ""
	for{
		msg, err := reader.ReadString('\n')
		if err != nil{
			fmt.Println("错误: " + err.Error())
			return
		}
		message += msg
		result := parse(message)
		if result{
			conn.Write([]byte("STORED\r\n"))
			message = ""
		}
	}
}

func parse(message string) bool{
	fmt.Println(len(message))
	if message[len(message)-1] != '\n'{
		fmt.Println("协议错误1")
		return false
	}
	if message[len(message)-2] != '\r'{
		fmt.Println("协议错误2")
		return false
	}
	headList := strings.Split(message, "\r\n")
	fmt.Println( len(headList))
	if len(headList) != 3{
		return false
	}
	return true
	fmt.Println("消息：" + message)
	headList = strings.Split(message, " ")
	if headList[0] != "set" || len(headList) != 5 || len(headList[4]) <= 0{
		fmt.Println("协议错误3")
		return false
	}

	return true
}
