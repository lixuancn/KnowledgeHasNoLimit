package main

import (
	"time"
	"GoCache"
)
var tablename = "testCache"
var k = "testkey"
var v = "testvalue"
func main(){
	table := GoCache.Cache(tablename)
	table.Add(k + "_1", 100 * time.Millisecond, v + "_1")
}