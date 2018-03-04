package main

import (
	"crypto/sha256"
	"encoding/hex"
	"time"
	"log"
	"github.com/davecgh/go-spew/spew"
	"github.com/joho/godotenv"
	"os"
	"net"
	"io"
	"bufio"
	"strconv"
	"sync"
	"encoding/json"
)

//定义一个块
type Block struct{
	//整个链中的位置
	Index int
	//生成时的时间戳
	Timestamp string
	//值，例子中是医疗行业的心跳值
	BPM int
	//本块的Hash值
	Hash string
	//链中上一个块的Hash值
	PrevHash string
}

//定义一个区块链
type Blockchain []Block

//声明一个区块链
var Blockchains Blockchain

//计算一个块的Hash值
func calculateHash(block Block)string{
	record := string(block.Index) + block.Timestamp + string(block.BPM) + block.PrevHash
	h := sha256.New()
	h.Write([]byte(record))
	hashed := h.Sum(nil)
	return hex.EncodeToString(hashed)
}

//生成一个块
func generateBlock(prevBlock Block, BPM int)Block{
	var newBlock Block
	newBlock.Index = prevBlock.Index + 1
	newBlock.Timestamp = time.Now().String()
	newBlock.BPM = BPM
	newBlock.PrevHash = prevBlock.Hash
	newBlock.Hash = calculateHash(newBlock)
	return newBlock
}

//检验块是否合法
func isBlockValid(prevBlock, block Block)bool{
	if prevBlock.Index + 1 != block.Index{
		return false
	}
	if prevBlock.Hash != block.PrevHash{
		return false
	}
	if calculateHash(block) != block.Hash{
		return false
	}
	return true
}

//2个链长度不一致时，选择最长的链
func replaceChain(newBlockChain Blockchain){
	mutex.Lock()
	defer mutex.Unlock()
	if len(Blockchains) < len(newBlockChain){
		Blockchains = newBlockChain
	}
}

//待同步的区块
var bcServer chan []Block

var mutex = sync.Mutex{}

func main(){
	//待同步的区块
	bcServer = make(chan []Block)
	//创世块
	genesisBlock := Block{0, time.Now().String(), 0, "", ""}
	spew.Dump(genesisBlock)
	Blockchains = append(Blockchains, genesisBlock)
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
			mutex.Lock()
			output, err := json.Marshal(Blockchains)
			if err != nil{
				log.Fatal(err)
			}
			mutex.Unlock()
			io.WriteString(conn, string(output))
		}
	}()
	for _ = range bcServer{
		spew.Dump(Blockchains)
	}
}