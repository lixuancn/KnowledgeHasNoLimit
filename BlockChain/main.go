package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"time"
	"net/http"
	"os"
	"log"
	"io"
	"github.com/davecgh/go-spew/spew"
	"github.com/joho/godotenv"
	"github.com/gorilla/mux"
	"fmt"
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
	if len(Blockchains) < len(newBlockChain){
		Blockchains = newBlockChain
	}
}

//web服务来实现增删改查
func run()error{
	mux := makeMuxRouter()
	httpAddr := os.Getenv("ADDR")
	log.Println("Listening on ", httpAddr)
	s := &http.Server{
		Addr: ":" + httpAddr,
		Handler: mux,
		ReadTimeout: 10 * time.Second,
		WriteTimeout: 10 * time.Second,
		MaxHeaderBytes: 1 << 20,
	}
	if err := s.ListenAndServe(); err != nil{
		return err
	}
	return nil
}

func makeMuxRouter()http.Handler{
	muxRouter := mux.NewRouter()
	muxRouter.HandleFunc("/", handleGetBlockchain).Methods("GET")
	muxRouter.HandleFunc("/", handleWriteBlock).Methods("POST")
	return muxRouter
}

type Message struct{
	BPM int
}

func handleGetBlockchain(w http.ResponseWriter, r *http.Request){
	bytes, err := json.MarshalIndent(Blockchains, "", "  ")
	if err != nil{
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	io.WriteString(w, string(bytes))
}
func handleWriteBlock(w http.ResponseWriter, r *http.Request){
	var m Message
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&m); err != nil{
		fmt.Println(m)
		responseWithJson(w, r, http.StatusBadRequest, r.Body)
		return
	}
	defer r.Body.Close()
	newBlock := generateBlock(Blockchains[len(Blockchains)-1], m.BPM)
	if isBlockValid(Blockchains[len(Blockchains)-1], newBlock){
		newBlockchains := append(Blockchains, newBlock)
		replaceChain(newBlockchains)
		spew.Dump(newBlockchains)
	}
	responseWithJson(w, r, http.StatusCreated, newBlock)
}
func responseWithJson(w http.ResponseWriter, r *http.Request, code int, payload interface{}){
	response, err := json.MarshalIndent(payload, "", "  ")
	if err != nil{
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("HTTP 500: Internal Server Error"))
		return
	}
	w.WriteHeader(code)
	w.Write(response)
}

func main(){
	err := godotenv.Load()
	if err != nil{
		log.Fatal(err)
	}
	go func(){
		genesisBlock := Block{0, time.Now().String(), 0, "", ""}
		spew.Dump(genesisBlock)
		Blockchains = append(Blockchains, genesisBlock)
	}()
	log.Fatal(run())
}