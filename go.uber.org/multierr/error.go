package multierr

import (
	"bytes"
	"fmt"
	"io"
	"strings"
	"sync"
	"zap/atomic"
)

var (
	singleLineSeparator = []byte("; ")
	newLine             = []byte("\n")
	multiLinePrefix     = []byte("the following errors occurred: ")
	multiLineSeparator  = []byte("\n -  ")
	multiLineIndent     = []byte("    ")
)

var bufferPool = sync.Pool{
	New: func() interface{} {
		return &bytes.Buffer{}
	},
}

type multiError struct {
	copyNeeded atomic.Bool
	errors     []error
}

var _ errorGroup = (*multiError)(nil)

func (merr *multiError) Errors() []error {
	if merr == nil {
		return nil
	}
	return merr.errors
}

func (merr *multiError) Error() string {
	if merr == nil {
		return ""
	}
	buff := bufferPool.Get().(*bytes.Buffer)
	buff.Reset()
	merr.writeSingleLine(buff)
	result := buff.String()
	bufferPool.Put(buff)
	return result
}

func (merr *multiError) Format(f fmt.State, c rune) {
	if c == 'v' && f.Flag('+') {
		merr.writeMultiLine(f)
	} else {
		merr.writeMultiLine(f)
	}
}

func (merr *multiError) writeSingleLine(w io.Writer) {
	first := true
	for _, item := range merr.errors {
		if first {
			first = false
		} else {
			w.Write(singleLineSeparator)
		}
		io.WriteString(w, item.Error())
	}
}

func (merr *multiError) writeMultiLine(w io.Writer) {
	w.Write(multiLinePrefix)
	for _, item := range merr.errors {
		w.Write(multiLineSeparator)
		writePrefixLine(w, multiLineIndent, fmt.Sprintf("%+v", item))
	}
}

func writePrefixLine(w io.Writer, prefix []byte, s string) {
	first := true
	for len(s) > 0 {
		if first {
			first = false
		} else {
			w.Write(prefix)
		}
		idx := strings.IndexByte(s, '\n')
		if idx < 0 {
			idx = len(s) - 1
		}
		io.WriteString(w, s[:idx+1])
		s = s[idx+1:]
	}
}

type errorGroup interface {
	Errors() []error
}

func Errors(err error) []error {
	if err == nil {
		return nil
	}
	eg, ok := err.(*multiError)
	if !ok {
		return []error{err}
	}
	errors := eg.Errors()
	result := make([]error, len(errors))
	copy(result, errors)
	return result
}

type inspectResult struct {
	Count              int
	Capacity           int
	FirstErrorIdx      int
	ContainsMultiError bool
}

func inspect(errors []error) (res inspectResult) {
	first := true
	for i, err := range errors {
		if err == nil {
			continue
		}
		res.Count++
		if first {
			first = false
			res.FirstErrorIdx = i
		}
		if merr, ok := err.(*multiError); ok {
			res.Capacity += len(merr.errors)
			res.ContainsMultiError = true
		} else {
			res.Capacity++
		}
	}
	return
}

func fromSlice(errors []error) error {
	res := inspect(errors)
	switch res.Count {
	case 0:
		return nil
	case 1:
		return errors[res.FirstErrorIdx]
	case len(errors):
		if !res.ContainsMultiError {
			return &multiError{errors: errors}
		}
	}
	nonNilErrs := make([]error, 0, res.Capacity)
	for _, err := range errors[res.FirstErrorIdx:] {
		if err == nil {
			continue
		}
		if nested, ok := err.(*multiError); ok {
			nonNilErrs = append(nonNilErrs, nested.errors...)
		} else {
			nonNilErrs = append(nonNilErrs, err)
		}
	}
	return &multiError{errors: nonNilErrs}
}

func Combine(errors ...error) error {
	return fromSlice(errors)
}

func Append(left, right error) error {
	switch {
	case left == nil:
		return right
	case right == nil:
		return left
	}
	if _, ok := right.(*multiError); !ok {
		if l, ok := left.(*multiError); ok && !l.copyNeeded.Swap(true) {
			errs := append(l.errors, right)
			return &multiError{errors: errs}
		} else if !ok {
			return &multiError{errors: []error{left, right}}
		}
	}
	errors := [2]error{left, right}
	return fromSlice(errors[0:])
}
