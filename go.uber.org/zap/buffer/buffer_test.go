package buffer

import (
	"testing"
	"strings"
	"bytes"
)

func TestBuffer_Write(t *testing.T) {
	buf := NewPool().Get()
	tests := []struct{
		desc string
		f func()
		want string
	}{
		{"AppendByte", func(){buf.AppendByte('v')}, "v"},
		{"AppendString", func(){buf.AppendString("foo")}, "foo"},
		{"AppendInt", func(){buf.AppendInt(42)}, "42"},
		{"AppendInt", func(){buf.AppendInt(-42)}, "-42"},
		{"AppendUint", func(){buf.AppendUint(42)}, "42"},
		{"AppendBool", func(){buf.AppendBool(true)}, "true"},
		{"AppendFloat", func(){buf.AppendFloat(3.14, 64)}, "3.14"},
		{"AppendFloat", func(){buf.AppendFloat(float64(float32(3.14)), 32)}, "3.14"},
		{"Write", func(){buf.Write([]byte("foo"))}, "foo"},
	}
	for _, tt := range tests{
		t.Run(tt.desc, func(t *testing.T) {
			buf.Reset()
			tt.f()
			if tt.want != buf.String(){
				t.Fatal("Unexpected buffer.String().")
			}
			if tt.want != string(buf.Bytes()){
				t.Fatal("Unexpected buffer.Bytes().")
			}
			if len(tt.want) != buf.Len(){
				t.Fatal("Unexpected buffer.Len().")
			}
			if SIZE != buf.Cap(){
				t.Fatal("Unexpected buffer.Cap().")
			}
		})
	}
}

func BenchmarkBuffer(b *testing.B){
	str := strings.Repeat("a", 1024)
	slice := make([]byte, 1024)
	buf := bytes.NewBuffer(slice)
	custom := NewPool().Get()
	b.Run("ByteSlice", func(b *testing.B){
		for i:=0; i<b.N; i++{
			slice = append(slice, str...)
			slice = slice[:0]
		}
	})
	b.Run("ByteBuffer", func(b *testing.B){
		for i:=0; i<b.N; i++{
			buf.WriteString(str)
			buf.Reset()
		}
	})
	b.Run("CustomBuffer", func(b *testing.B){
		for i:=0; i<b.N; i++{
			custom.AppendString(str)
			custom.Reset()
		}
	})
}