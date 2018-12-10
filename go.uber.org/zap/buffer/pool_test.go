package buffer

import (
	"testing"
	"sync"
)

func TestNewPool(t *testing.T) {
	const dummyData = "hello world"
	p := NewPool()
	wg := sync.WaitGroup{}
	for i:=0; i<10; i++{
		wg.Add(1)
		go func(){
			defer wg.Done()
			buf := p.Get()
			if buf.Len() != 0{
				t.Fatal("excepted len")
			}
			if buf.Cap() == 0{
				t.Fatal("excepted cap")
			}
			buf.AppendString(dummyData)
			if buf.Len() != len(dummyData){
				t.Fatal("excepted len2")
			}
			buf.Free()
		}()
	}
	wg.Wait()
}