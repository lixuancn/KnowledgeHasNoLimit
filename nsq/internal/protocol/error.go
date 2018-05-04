package protocol

type ChildErr interface {
	Parent() error
}

type ClientErr struct {
	ParentErr error
	Code      string
	Desc      string
}

func NewClientErr(parent error, code, desc string) *ClientErr {
	return &ClientErr{
		ParentErr: parent,
		Code:      code,
		Desc:      desc,
	}
}

func (e *ClientErr) Error() string {
	return e.Code + " " + e.Desc
}

func (e *ClientErr) Parent() error {
	return e.ParentErr
}

type FatalClientErr struct {
	ParentErr error
	Code      string
	Desc      string
}

func NewFatalClientErr(parent error, code, desc string) *FatalClientErr {
	return &FatalClientErr{
		ParentErr: parent,
		Code:      code,
		Desc:      desc,
	}
}

func (e *FatalClientErr) Error() string {
	return e.Code + " " + e.Desc
}

func (e *FatalClientErr) Parent() error {
	return e.ParentErr
}
