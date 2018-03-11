package main

import (
	"BlockChain/model"
	"BlockChain/bcnet"
)

func main(){
	//创世块
	model.GenesisBlock()
	//Web方式
	//bcnet.RunWeb()
	//Tcp广播同步
	bcnet.RunTcp()
}