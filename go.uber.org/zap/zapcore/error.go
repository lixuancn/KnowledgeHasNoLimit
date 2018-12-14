package zapcore

func encodeError(key string, err error, enc ObjectEncoder){
	basic := err.Error()
	enc.AddString(key, basic)
	switch e:=err.(type){
	case errorGroup:
		return enc.AddArray(key+"Causes", errArray(e.Errors))
	}
}


type errorGroup interface {
	Errors() []error
}

type causer interface {
	Cause() error
}

type errArray []error

func (errs errArray) MarshalLogArray(arr ArrayEncoder) error {
	for i := range errs {
		if errs[i] == nil {
			continue
		}

		el := newErrArrayElem(errs[i])
		arr.AppendObject(el)
		el.Free()
	}
	return nil
}

var _errArrayElemPool = sync.Pool{New: func() interface{} {
	return &errArrayElem{}
}}