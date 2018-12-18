package zapcore

import (
	"sync"
	"zap/internal/bufferpool"
	"strings"
)

var cePool = sync.Pool{
	New: func()interface{}{
		return &CheckedEntry{
			cores: make([]Core, 4),
		}
	}
}


type CheckedEntry struct{
	Entry
	ErrorOutput WriteSyncer
	dirty bool
	should CheckWriteAction
	cores []Core
}

type EntryCaller struct{
	Defined bool
	PC uintptr
	File string
	Line int
}

func NewEntryCaller(pc uintptr, file string, line int, ok bool)EntryCaller{
	if !ok{
		return EntryCaller{}
	}
	return EntryCaller{
		PC: pc,
		File: file,
		Line: line,
		Defined: true,
	}
}

func (ec EntryCaller)String()string{
	return ec.FullPath()
}

func (ec EntryCaller)FullPath()string{
	if !ec.Defined{
		return "undefined"
	}
	buf := bufferpool.Get()
	buf.AppendString(ec.File)
	buf.AppendByte(':')
	buf.AppendInt(int64(ec.Line))
	caller := buf.String()
	buf.Free()
	return caller
}

func (ec EntryCaller)TrimmedPath()string{
	if !ec.Defined{
		return "undefined"
	}
	idx := strings.LastIndexByte(ec.File, '/')
	if idx == -1{
		return ec.FullPath()
	}
	buf := bufferpool.Get()
	buf.AppendString(ec.File[idx+1:])
	buf.AppendByte(':')
	buf.AppendInt(int64(ec.Line))
	caller := buf.String()
	buf.Free()
	return caller
}