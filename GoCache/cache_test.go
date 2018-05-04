package GoCache

import (
	"testing"
	"time"
	"sync"
	"sync/atomic"
	"strconv"
)

var tablename = "testCache"
var k = "testkey"
var v = "testvalue"

func TestCache(t *testing.T){
	table := Cache(tablename)
	table.Add(k + "_1", 0 * time.Second, v)
	table.Add(k + "_2", 1 * time.Second, v)

	p, err := table.Value(k + "_1")
	if err != nil || p == nil || p.GetValue().(string) != v{
		t.Error("Error retrieving non expiring data from cache", err)
	}
	p, err = table.Value(k + "_2")
	if err != nil || p == nil || p.GetValue().(string) != v{
		t.Error("Error retrieving data from cache", err)
	}
	if p.GetAccessCount() != 1{
		t.Error("Error getting correct access count")
	}
	if p.GetLifeSpan() != 1*time.Second {
		t.Error("Error getting correct life-span")
	}
	if p.GetAccessTime().Unix() == 0 {
		t.Error("Error getting access time")
	}
	if p.GetCreateTime().Unix()== 0 {
		t.Error("Error getting creation time")
	}
	time.Sleep(time.Second * 3)
	p, err = table.Value(k + "_2")
	if p != nil || err == nil{
		t.Error("Error key not expire")
	}
}

func TestCacheExpire(t *testing.T){
	table := Cache(tablename)
	table.Add(k + "_1", 100 * time.Millisecond, v + "_1")
	table.Add(k + "_2", 125 * time.Millisecond, v + "_2")
	time.Sleep(75 * time.Millisecond)
	_, err := table.Value(k + "_1")
	if err != nil{
		t.Error("Error retrieving value from cache:", err)
	}
	time.Sleep(75 * time.Millisecond)
	_, err = table.Value(k + "_1")
	if err != nil{
		t.Error("Error retrieving value from cache 2:", err)
	}
	_, err = table.Value(k + "_2")
	if err == nil{
		t.Error("Found key which should have been expire by now")
	}
}

func TestExists(t *testing.T){
	table := Cache(tablename)
	table.Add(k, 0, v)
	if !table.Exists(k){
		t.Error("Error verifying existing data in cache")
	}
}

func TestNotFoundAdd(t *testing.T){
	table := Cache("testNotFoundAdd")
	if !table.NotFoundAdd(k, v, 0){
		t.Error("Error verifying NotFoundAdd data not in cache")
	}
	if table.NotFoundAdd(k, v, 0){
		t.Error("Error verifying NotFoundAdd data in cache")
	}
}

func TestNotFoundAddConcurrency(t *testing.T){
	table := Cache("testNotFoundAdd")
	var finish sync.WaitGroup
	var added int32
	var idle int32
	fn := func(id int){
		for i:=0; i<100; i++{
			if table.NotFoundAdd(i, i+id, 0){
				atomic.AddInt32(&added, 1)
			}else{
				atomic.AddInt32(&idle, 1)
			}
			time.Sleep(0)
		}
		finish.Done()
	}
	finish.Add(10)
	go fn(0x0000)
	go fn(0x1100)
	go fn(0x2200)
	go fn(0x3300)
	go fn(0x4400)
	go fn(0x5500)
	go fn(0x6600)
	go fn(0x7700)
	go fn(0x8800)
	go fn(0x9900)
	finish.Wait()
	t.Log(added, idle)
	table.Foreach(func(key interface{}, item *CacheItem){
		v, _ := item.GetValue().(int)
		k, _ := key.(int)
		t.Logf("%02x %04x\n", k, v)
	})
}

func TestCacheKeepAlive(t *testing.T){
	table := Cache("testKeepAlive")
	p := table.Add(k, 100 * time.Millisecond, v)
	time.Sleep(50 * time.Millisecond)
	p.KeepAlive()
	time.Sleep(75 * time.Millisecond)
	if !table.Exists(k){
		t.Error("Error Keeping item alive")
	}
	time.Sleep(75 * time.Millisecond)
	if table.Exists(k){
		t.Error("Error expiring item after keeping it alive")
	}
}
func TestDelete(t *testing.T) {
	table := Cache("testDelete")
	table.Add(k, 0, v)
	p, err := table.Value(k)
	if err != nil || p == nil || p.GetValue().(string) != v{
		t.Error("Error retrieving data from cache", err)
	}
	table.Delete(k)
	p, err = table.Value(k)
	if err == nil || p != nil{
		t.Error("Error deleting data")
	}
	_, err = table.Delete(k)
	if err == nil{
		t.Error("Expected error deleting item")
	}
}

func TestFlush(t *testing.T){
	table := Cache("testFlush")
	table.Add(k, 10 * time.Second, v)
	table.Flush()
	p, err := table.Value(k)
	if err == nil || p != nil{
		t.Error("Error flushing table")
	}
	if table.Count() != 0{
		t.Error("Error verifying count of flushed table")
	}
}

func TestCount(t *testing.T){
	table := Cache("testCount")
	count := 100000
	for i:=0; i<count; i++{
		key := k + strconv.Itoa(i)
		table.Add(key, 10 * time.Second, v)
	}
	for i:=0; i<count; i++{
		key := k + strconv.Itoa(i)
		p, err := table.Value(key)
		if err != nil || p == nil || p.GetValue().(string) != v{
			t.Error("Error retrieving data")
		}
	}
	if table.Count() != count{
		t.Error("Error data count mismatch")
	}
}