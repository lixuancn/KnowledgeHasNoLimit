package nsqd

type Channel struct {
	name string
}

func NewChannel(topicName, channelName string, ctx *context, deleteCallback func(*Channel)) *Channel {
	return &Channel{}
}

func (c *Channel) Delete() error {
	return c.exit(true)
}

func (c *Channel) exit(delete bool) error {
	return nil
}
