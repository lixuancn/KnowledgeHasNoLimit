package nsqd

type Channel struct {
	name string
}

func NewChannel(topicName, channelName string, ctx *context, deleteCallback func(*Channel))*Channel{
	return &Channel{}
}