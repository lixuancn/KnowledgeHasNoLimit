package main

import (
	"crypto/sha256"
	"encoding/hex"
	"time"
	"sync"
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

var mutexBlock = sync.Mutex{}

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
	mutexBlock.Lock()
	defer mutexBlock.Unlock()
	if len(Blockchains) < len(newBlockChain){
		Blockchains = newBlockChain
	}
}