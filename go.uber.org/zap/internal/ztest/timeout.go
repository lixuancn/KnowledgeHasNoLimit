package ztest

import (
	"time"
	"strconv"
	"os"
	"log"
)

var TIMEOUT_SCALE = 1.0

func Timeout(base time.Duration)time.Duration{
	return time.Duration(float64(base) * TIMEOUT_SCALE)
}

func Sleep(base time.Duration){
	time.Sleep(Timeout(base))
}

func Initialize(factor string)func(){
	original := TIMEOUT_SCALE
	fv, err := strconv.ParseFloat(factor, 64)
	if err != nil{
		panic(err)
	}
	TIMEOUT_SCALE = fv
	return func(){
		TIMEOUT_SCALE = original
	}
}

func init(){
	if v := os.Getenv("TEST_TMIEOUT_SCALE"); v != ""{
		Initialize(v)
		log.Printf("Scaling timeouts by %vx.\n", TIMEOUT_SCALE)
	}
}