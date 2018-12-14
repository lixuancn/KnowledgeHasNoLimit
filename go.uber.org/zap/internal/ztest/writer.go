package ztest

import (
	"io/ioutil"
	"github.com/go-errors/errors"
	"bytes"
	"strings"
)

type Syncer struct{
	err error
	called bool
}

func (s *Syncer)SetError(err error){
	s.err = err
}

func (s *Syncer)Sync ()error{
	s.called = true
	return s.err
}

func (s *Syncer)Called()bool{
	return s.called
}

type Discarder struct {
	Syncer
}

func (d *Discarder)Write(b []byte)(int, error){
	return ioutil.Discard.Write(b)
}

type FailWriter struct {
	Syncer
}

func (w FailWriter)Write(b []byte)(int, error){
	return len(b), errors.New("failed")
}

type ShortWriter struct{
	Syncer
}

func (w ShortWriter)Write(b []byte)(int, error){
	return len(b) - 1, nil
}

type Buffer struct {
	bytes.Buffer
	Syncer
}

func (b *Buffer)Lines()[]string{
	output := strings.Split(b.String(), "\n")
	return output[:len(output) - 1]
}

func (b *Buffer)Stripped()string{
	return strings.TrimRight(b.String(), "\n")
}