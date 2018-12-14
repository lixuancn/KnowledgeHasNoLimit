package zapcore

import "sync"

var cePool = sync.Pool{
	New: func()interface{}{
		return &CheckedEntry{
			cores: make([]Core, 4),
		}
	}
}