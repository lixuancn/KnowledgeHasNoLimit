package zapcore

import (
	"zap/buffer"
	"time"
)

const DEFAULT_LINE_ENDING = "\n"

type LevelEncoder func(Level, PrimitiveArrayEncoder)

func LowercaseLevelEncoder(l Level, enc PrimitiveArrayEncoder){
	enc.AppendString(l.String())
}

func LowercaseColorLevelEncoder(l Level, enc PrimitiveArrayEncoder){
	//s, ok := _levelToLowercaseColorString
	enc.AppendString(l.String())
}

type NameEncoder func(string, PrimitiveArrayEncoder)

func (e *NameEncoder)UnmarshalText(text []byte)error{
	switch string(text){
	case "full":
		*e = FullNameEncoder
	default:
		*e = FullNameEncoder
	}
	return nil
}

func FullNameEncoder(loggerName string, enc PrimitiveArrayEncoder){
	enc.AppendString(loggerName)
}

type EncoderConfig struct{
	MessageKey    string `json:"messageKey" yaml:"messageKey"`
	LevelKey      string `json:"levelKey" yaml:"levelKey"`
	TimeKey       string `json:"timeKey" yaml:"timeKey"`
	NameKey       string `json:"nameKey" yaml:"nameKey"`
	CallerKey     string `json:"callerKey" yaml:"callerKey"`
	StacktraceKey string `json:"stacktraceKey" yaml:"stacktraceKey"`
	LineEnding    string `json:"lineEnding" yaml:"lineEnding"`

	EncodeLevel    LevelEncoder    `json:"levelEncoder" yaml:"levelEncoder"`
	EncodeTime     TimeEncoder     `json:"timeEncoder" yaml:"timeEncoder"`
	EncodeDuration DurationEncoder `json:"durationEncoder" yaml:"durationEncoder"`
	EncodeCaller   CallerEncoder   `json:"callerEncoder" yaml:"callerEncoder"`

	EncodeName NameEncoder `json:"nameEncoder" yaml:"nameEncoder"`
}

type ObjectEncoder interface {
	AddArray(key string, marshaler ArrayMarshaler)error
	AddObject(key string, marshaler ObjectMarshaler)error

	AddBinary(key string, value []byte)
	AddByteString(key string, value []byte)
	AddString(key, value string)
	AddDuration(key string, value time.Duration)
	AddTime(key string, value time.Time)
	AddBool(key string, value bool)
	AddComplex128(key string, value complex128)
	AddComplex64(key string, value complex64)
	AddFloat64(key string, value float64)
	AddFloat32(key string, value float32)
	AddInt(key string, value int)
	AddInt64(key string, value int64)
	AddInt32(key string, value int32)
	AddInt16(key string, value int16)
	AddInt8(key string, value int8)
	AddUint(key string, value uint)
	AddUint64(key string, value uint64)
	AddUint32(key string, value uint32)
	AddUint16(key string, value uint16)
	AddUint8(key string, value uint8)
	AddUintptr(key string, value uintptr)
	AddReflected(key string, value interface{})error
	OpenNamespace(key string)
}

type ArrayEncoder interface {
	PrimitiveArrayEncoder
	AppendDuration(time.Duration)
	AppendTime(time.Time)
	AppendArray(ArrayMarshaler)
	AppendObject(ObjectMarshaler)
}

type PrimitiveArrayEncoder interface {
	AppendBool(bool)
	AppendByteString([]byte)
	AppendComplex128(complex128)
	AppendComple64(complex64)
	AppendFloat64(float64)
	AppendFloat32(float32)
	AppendInt(int)
	AppendInt64(int64)
	AppendInt32(int32)
	AppendInt16(int16)
	AppendInt8(int8)
	AppendString(string)
	AppendUint(uint)
	AppendUint64(uint64)
	AppendUint32(uint32)
	AppendUint16(uint16)
	AppendUint8(uint8)
	AppendUintptr(uintptr)
}

type Encoder interface{
	ObjectEncoder
	Clone() Encoder
	EncodeEntry(Entry, []Field)(*buffer.Buffer, error)
}