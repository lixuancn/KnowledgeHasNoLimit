package main

import (
	"time"
	"github.com/davecgh/go-spew/spew"
)

func main(){
	//创世块
	genesisBlock := Block{0, time.Now().String(), 0, "", ""}
	spew.Dump(genesisBlock)
	Blockchains = append(Blockchains, genesisBlock)
	//Web方式
	runWeb()
	//Tcp广播同步
	//runTcp()
}