package nsqlookupd

import (
	"log"
	"nsq/internal/lg"
	"os"
	"time"
)

type Options struct {
	LogLevel  string `flag:"log-level"`
	LogPrefox string `flag:"log-prefix"`
	Verbose   bool   `flag:"verbose"` // for backwards compatibility
	Logger    Logger
	logLevel  lg.LogLevel

	TCPAddress       string `flag:"tcp-address"`
	HTTPAddress      string `flag:"http-address"`
	BroadcastAddress string `flag:"broadcast-address"`

	InactiveProducerTimeout time.Duration `flag:"inactive-producer-timeout"`
	TombstoneLifetime       time.Duration `flag:"tombstone-lifetime"`
}

func NewOptions() *Options {
	hostname, err := os.Hostname()
	if err != nil {
		log.Fatal("err")
	}
	return &Options{
		LogLevel:         "INFO",
		LogPrefox:        "[nsqlookupd]",
		TCPAddress:       "0.0.0.0:4160",
		HTTPAddress:      "0.0.0.0:4161",
		BroadcastAddress: hostname,

		InactiveProducerTimeout: 300 * time.Second,
		TombstoneLifetime:       45 * time.Second,
	}
}
