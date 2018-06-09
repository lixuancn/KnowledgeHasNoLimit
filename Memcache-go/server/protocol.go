package server

import (
	"net"
	"strings"
	"github.com/go-errors/errors"
	"bufio"
	"log"
	"fmt"
)

type Protocol interface{
	Handle(conn net.Conn)
	parse(message string)bool
}

func GetProtocol(protocol string)(Protocol, error){
	switch(strings.ToLower(protocol)){
	case "memcache":
		return NewMemcache(), nil
	}
	return nil, errors.New("协议未实现")
}

type Memcache struct{
}

func NewMemcache()*Memcache{
	return &Memcache{}
}

func (mc *Memcache)Handle(clientConn net.Conn){
	reader := bufio.NewReader(clientConn)
	message := ""
	for{
		msg, err := reader.ReadString('\n')
		if err != nil{
			log.Println("读取链接数据错误: " + err.Error())
			return
		}
		message += msg
		parseResult := mc.parse(message)
		if parseResult{
			clientConn.Write([]byte("STORED\r\n"))
			message = ""
		}
	}
}

func (mc *Memcache)parse(message string)bool{
	fmt.Println(len(message))
	if message[len(message)-1] != '\n'{
		fmt.Println("消息最后一位不是\\n")
		return false
	}
	if message[len(message)-2] != '\r'{
		fmt.Println("消息倒数第二位不是\\r")
		return false
	}
	headList := strings.Split(message, "\r\n")
	fmt.Println(len(headList))
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