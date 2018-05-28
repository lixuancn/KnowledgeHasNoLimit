package nsqd

import (
	"nsq/internal/util"
	"sync"
)

type Topic struct {
	messageCount uint64

	sync.RWMutex

	name              string
	channelMap        map[string]*Channel
	backend           BackendQueue
	memoryMsgChan     chan *Message
	exitChan          chan int
	channelUpdateChan chan int
	waitGroup         util.WaitGroupWrapper
	exitFlag          int32
	idFactory         *guidFactory

	ephemeral      bool
	deleteCallback func(*Topic)
	deleter        sync.Once

	paused    int32
	pauseChan chan bool

	ctx *context
}

func NewTopic(topicName string, ctx *context, deleteCallback func(*Topic)) *Topic{
	return &Topic{}
}

func (t *Topic)Pause(){

}