package server

import (
	"bufio"
	"fmt"
	"github.com/go-errors/errors"
	"log"
	"net"
	"strconv"
	"strings"
)

type Memcache struct {
	//指令，如set，get
	Commend string
	Key     string
	Value   string
	//标识
	Flag uint16
	//数据长度
	ValueLength int
	//有效期
	Expires int64
	//成功响应
	Response string
}

func NewMemcache() *Memcache {
	return &Memcache{}
}

func (mc *Memcache) Handle(clientConn net.Conn) {
	reader := bufio.NewReader(clientConn)
	message := ""
	for {
		msg, err := reader.ReadString('\n')
		if err != nil {
			log.Println("读取链接数据错误: " + err.Error())
			return
		}
		message += msg
		parseResult, err := mc.parse(message)
		if err != nil {
			clientConn.Write([]byte(mc.Response))
			log.Println("解析数据错误: " + err.Error())
			return
		}
		if parseResult {
			clientConn.Write([]byte(mc.Response))
			message = ""
		}
	}
}

func (mc *Memcache) parse(message string) (bool, error) {
	fmt.Println("消息：" + message)
	fmt.Println(len(message))
	if message[len(message)-1] != '\n' {
		fmt.Println("消息最后一位不是\\n")
		return false, nil
	}
	if message[len(message)-2] != '\r' {
		fmt.Println("消息倒数第二位不是\\r")
		return false, nil
	}
	//headList := strings.Split(message, "\r\n")
	fieldList := strings.Fields(message)
	if len(fieldList) != 6 {
		return false, nil
	}
	if len(fieldList[0]) <= 0 {
		return false, errors.New("协议解析错误：首位命令为空")
	}
	command := strings.ToLower(fieldList[0])
	fmt.Println(command)
	mc.Commend = command
	var err error
	if mc.Commend == "set" || mc.Commend == "add" || mc.Commend == "replace" {
		err = mc.parseSet(fieldList)
	} else if mc.Commend == "get" {
		err = mc.parseGet(fieldList)
	} else {
		return false, errors.New("协议解析错误：首位命令非法")
	}
	if err != nil {
		return false, err
	}
	return true, nil
}

func (mc *Memcache) parseSet(fieldList []string) error {
	mc.Response = "NOT_STORED/r/n"
	mc.Key = fieldList[1]
	flag, err := strconv.Atoi(fieldList[2])
	if err != nil {
		return err
	}
	mc.Flag = uint16(flag)
	expire, err := strconv.Atoi(fieldList[3])
	if err != nil {
		return err
	}
	mc.Expires = int64(expire)
	valueLength, err := strconv.Atoi(fieldList[4])
	if err != nil {
		return err
	}
	mc.ValueLength = valueLength
	mc.Value = fieldList[5]
	if mc.ValueLength != len(mc.Value) {
		return errors.New("数据长度错误")
	}
	mc.Response = "STORED\r\n"
	return nil
}

func (mc *Memcache) parseGet(fieldList []string) error {
	return nil
}
