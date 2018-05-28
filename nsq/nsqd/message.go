package nsqd

import "time"

const (
	MsgIDLength       = 16
	minValidMsgLength = MsgIDLength + 8 + 2 // Timestamp + Attempts
)

type MessageID [MsgIDLength]byte

type Message struct {
	ID MessageID
	Body []byte
	Timestamp int64
	Attempts uint64

	deliveryTS time.Time
	clientID int64
	pri int64
	index int
	deferred time.Duration
}