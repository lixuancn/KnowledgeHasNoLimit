package nsqd

import (
	"nsq/internal/util"
	"sync"
	"sync/atomic"
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

func NewTopic(topicName string, ctx *context, deleteCallback func(*Topic)) *Topic {
	return &Topic{}
}

func (t *Topic) Exiting() bool {
	return atomic.LoadInt32(&t.exitFlag) == 1
}

func (t *Topic) GetChannel(channelName string) *Channel {
	t.Lock()
	channel, isNew := t.getOrCreateChannel(channelName)
	t.Unlock()
	if isNew {
		select {
		case t.channelUpdateChan <- 1:
		case <-t.exitChan:
		}
	}
	return channel
}

func (t *Topic) getOrCreateChannel(channelName string)(*Channel, bool){
	channel, ok := t.channelMap[channelName]
	if !ok{
		deleteCallback := func(c *Channel){
			t.DeleteExistingChannel(c.name)
		}
		channel = NewChannel(t.name, channelName, t.ctx, deleteCallback)
		t.channelMap[channelName] = channel
		t.ctx.nsqd.logf(LOG_INFO, "TOPIC(%s) new channel(%s)", t.name, channel.name)
		return channel, true
	}
	return channel, false
}

func (t *Topic) DeleteExistingChannel(channelName string) {

}
func (t *Topic) Pause() {

}