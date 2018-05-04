package protocol

import "errors"

var errBase10 = errors.New("failed to convert to Base10")

func ByteToBase10(b []byte) (uint64, error) {
	base := uint64(10)
	n := uint64(0)
	for i := 0; i < len(b); i++ {
		var v byte
		d := b[i]
		switch {
		case '0' <= d && d <= '9':
			v = d - '0'
		default:
			n = 0
			err := errBase10
			return n, err
		}
		n *= base
		n += uint64(v)
	}
	return n, nil
}
