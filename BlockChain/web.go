package main

import (
	"os"
	"github.com/gorilla/mux"
	"encoding/json"
	"log"
	"io"
	"fmt"
	"net/http"
	"time"
	"github.com/davecgh/go-spew/spew"
)

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