package test

import (
	"path/filepath"
	"reflect"
	"runtime"
	"testing"
)

func Equal(t *testing.T, act, exp interface{}) {
	if !reflect.DeepEqual(exp, act) {
		_, file, line, _ := runtime.Caller(1)
		t.Logf("\033[31m%s:%d:\n\texp: %#v\n\tgot: %#v\033[39m\n",
			filepath.Base(file), line, exp, act)
		t.FailNow()
	}
}

func NotEqual(t *testing.T, act, exp interface{}) {
	if reflect.DeepEqual(exp, act) {
		_, file, line, _ := runtime.Caller(1)
		t.Logf("\033[31m%s:%d:\n\texp: %#v\n\tgot: %#v\033[39m\n",
			filepath.Base(file), line, exp, act)
		t.FailNow()
	}
}

func Nil(t *testing.T, obj interface{}) {
	if !IsNil(obj) {
		_, file, line, _ := runtime.Caller(1)
		t.Logf("\033[31m%s:%d:\n\n\t   <nil> (expected)\n\n\t!= %#v (actual)\033[39m\n\n",
			filepath.Base(file), line, obj)
		t.FailNow()
	}
}

func NotNil(t *testing.T, obj interface{}) {
	if IsNil(obj) {
		_, file, line, _ := runtime.Caller(1)
		t.Logf("\033[31m%s:%d:\n\n\t   <nil> (expected)\n\n\t!= %#v (actual)\033[39m\n\n",
			filepath.Base(file), line, obj)
		t.FailNow()
	}
}

func IsNil(obj interface{}) bool {
	if obj == nil {
		return true
	}
	value := reflect.ValueOf(obj)
	kind := value.Kind()
	if kind >= reflect.Chan && kind <= reflect.Slice && value.IsNil() {
		return true
	}
	return false
}
