package atomic

type Error struct {
	v Value
}

type errorHolder struct {
	err error
}

func NewError(err error) *Error {
	e := &Error{}
	if err != nil {
		e.Store(err)
	}
	return e
}

func (e *Error) Load() error {
	v := e.v.Load()
	if v == nil {
		return nil
	}
	eh := v.(errorHolder)
	return eh.err
}

func (e *Error) Store(err error) {
	e.v.Store(errorHolder{err: err})
}
