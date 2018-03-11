package model

import (
	"crypto/sha256"
	"encoding/hex"
	"time"
	"sync"
	"BlockChain/conf"
	"github.com/davecgh/go-spew/spew"
	"strings"
	"fmt"
	"log"
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
	//难度（前导0的个数）
	Difficulty int
	//随机数
	Nonce string
}

//定义一个区块链
type Blockchain []Block

//声明一个区块链
var Blockchains Blockchain

var mutexBlock = sync.Mutex{}

//计算一个块的Hash值
func CalculateHash(block Block)string{
	record := string(block.Index) + block.Timestamp + string(block.BPM) + block.PrevHash + string(block.Difficulty) + block.Nonce
	h := sha256.New()
	h.Write([]byte(record))
	hashed := h.Sum(nil)
	return hex.EncodeToString(hashed)
}

//生成一个块
func GenerateBlock(prevBlock Block, BPM int)Block{
	var newBlock Block
	newBlock.Index = prevBlock.Index + 1
	newBlock.Timestamp = time.Now().String()
	newBlock.BPM = BPM
	newBlock.PrevHash = prevBlock.Hash
	newBlock.Difficulty = conf.DIFFICULTY
	//newBlock.Hash = CalculateHash(newBlock)
	newBlock = ProofOfWork(newBlock)
	return newBlock
}

//检验块是否合法
func IsBlockValid(prevBlock, block Block)bool{
	if prevBlock.Index + 1 != block.Index{
		return false
	}
	if prevBlock.Hash != block.PrevHash{
		return false
	}
	if CalculateHash(block) != block.Hash{
		return false
	}
	return true
}

//2个链长度不一致时，选择最长的链
func ReplaceChain(newBlockChain Blockchain){
	mutexBlock.Lock()
	defer mutexBlock.Unlock()
	if len(Blockchains) < len(newBlockChain){
		Blockchains = newBlockChain
	}
}

//生成初始块
func GenesisBlock(){
	genesisBlock := Block{0, time.Now().String(), 0, "", "", conf.DIFFICULTY, "0"}
	spew.Dump(genesisBlock)
	Blockchains = append(Blockchains, genesisBlock)
}


//hash是否满足前导0的个数
func isHashValid(hash string, difficulty int)bool{
	prefix := strings.Repeat("0", difficulty)
	return strings.HasPrefix(hash, prefix)
}

//工作量证明（Proof-of-Work）算法的核心
func ProofOfWork(newBlock Block)Block{
	for i := 0; ; i++ {
		hex := fmt.Sprintf("%x", i)
		newBlock.Nonce = hex
		h := CalculateHash(newBlock)
		if !isHashValid(h, newBlock.Difficulty){
			log.Println(i, " ", h, " failed")
			if i % 100 == 0{
				time.Sleep(1 * time.Second)
			}
			continue
		}else{
			log.Println("success! ", h)
			newBlock.Hash = h
		}
		return newBlock
	}
}