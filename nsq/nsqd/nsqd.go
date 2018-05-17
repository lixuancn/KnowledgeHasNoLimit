package nsqd

const (
	TLSNotRequired = iota
	TLSRequiredExceptHTTP
	TLSRequired
)

type NSQD struct{

}

func New(opts *Options) *NSQD {
	return &NSQD{}
}

func (n *NSQD) LoadMetadata() error {
	return nil
}

func (n *NSQD) PersistMetadata() error {
	return nil
}

func (n *NSQD) Main() {

}

func (n *NSQD)Exit(){

}

func (n *NSQD)getOpts(){

}