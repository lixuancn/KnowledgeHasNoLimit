package zapcore

import (
	"testing"
	"strings"
	"bytes"
	"flag"
)

func TestLevel_String(t *testing.T) {
	tests := map[Level]string{
		DEBUG_LEVEL: "debug",
		INFO_LEVEL: "info",
		WARN_LEVEL: "warn",
		ERROR_LEVEL: "error",
		DPANIC_LEVEL: "dpanic",
		PANIC_LEVEL: "panic",
		FATAL_LEVEL: "fatal",
		Level(-42): "Level(-42)",
	}
	for lvl, stringLevel := range tests {
		if stringLevel != lvl.String() {
			t.Fatal("Unexpected lowercase level string")
		}
		if strings.ToUpper(stringLevel) != lvl.CapitalString() {
			t.Fatal("Unexpected all-caps level string")
		}
	}
}

func TestLevelText(t *testing.T) {
	tests := []struct{
		text string
		level Level
	}{
		{"debug", DEBUG_LEVEL},
		{"info", INFO_LEVEL},
		{"warn", WARN_LEVEL},
		{"error", ERROR_LEVEL},
		{"dpanic", DPANIC_LEVEL},
		{"panic", PANIC_LEVEL},
		{"fatal", FATAL_LEVEL},
	}
	for _, tt := range tests {
		if tt.text != "" {
			lvl := tt.level
			marshaled, err := lvl.MarshalText()
			if err != nil {
				t.Fatalf("Unexpected error marshaling level %v to text.", &lvl)
			}
			if tt.text != string(marshaled) {
				t.Fatalf("Marshaling level %v to text yielded unexpected result.", &lvl)
			}
		}
		var unmarshaled Level
		err := unmarshaled.UnmarshalText([]byte(tt.text))
		if err != nil {
			t.Fatalf("Unexpected error unmarshaling text %q to level.", tt.text)
		}
		if tt.level != unmarshaled {
			t.Fatalf("Text %q unmarshaled to an unexpected level.", tt.text)
		}
	}
}

func TestCapitalLevelsParse(t *testing.T) {
	tests := []struct {
		text  string
		level Level
	}{
		{"DEBUG", DEBUG_LEVEL},
		{"INFO", INFO_LEVEL},
		{"WARN", WARN_LEVEL},
		{"ERROR", ERROR_LEVEL},
		{"DPANIC", DPANIC_LEVEL},
		{"PANIC", PANIC_LEVEL},
		{"FATAL", FATAL_LEVEL},
	}
	for _, tt := range tests {
		var unmarshaled Level
		err := unmarshaled.UnmarshalText([]byte(tt.text))
		if err != nil {
			t.Fatalf("Unexpected error unmarshaling text %q to level.", tt.text)
		}
		if tt.level != unmarshaled {
			t.Fatalf("Text %q unmarshaled to an unexpected level.", tt.text)
		}
	}
}

func TestWeirdLevelsParse(t *testing.T) {
	tests := []struct {
		text  string
		level Level
	}{
		{"Debug", DEBUG_LEVEL},
		{"Info", INFO_LEVEL},
		{"Warn", WARN_LEVEL},
		{"Error", ERROR_LEVEL},
		{"Dpanic", DPANIC_LEVEL},
		{"Panic", PANIC_LEVEL},
		{"Fatal", FATAL_LEVEL},

		// What even is...
		{"DeBuG", DEBUG_LEVEL},
		{"InFo", INFO_LEVEL},
		{"WaRn", WARN_LEVEL},
		{"ErRor", ERROR_LEVEL},
		{"DpAnIc", DPANIC_LEVEL},
		{"PaNiC", PANIC_LEVEL},
		{"FaTaL", FATAL_LEVEL},
	}
	for _, tt := range tests {
		var unmarshaled Level
		err := unmarshaled.UnmarshalText([]byte(tt.text))
		if err != nil {
			t.Fatalf("Unexpected error unmarshaling text %q to level.", tt.text)
		}
		if tt.level != unmarshaled {
			t.Fatalf("Text %q unmarshaled to an unexpected level.", tt.text)
		}
	}
}

func TestLevelUnmarshalUnknownText(t *testing.T) {
	var l Level
	err := l.UnmarshalText([]byte("foo"))
	if !strings.Contains(err.Error(), "unrecognized level"){
		t.Fatalf("Expected unmarshaling arbitrary text to fail.")
	}
}

func TestLevelAsFlagValue(t *testing.T) {
	var (
		buf bytes.Buffer
		lvl Level
	)
	fs := flag.NewFlagSet("levelTest", flag.ContinueOnError)
	fs.SetOutput(&buf)
	fs.Var(&lvl, "level", "log level")

	for _, expected := range []Level{DEBUG_LEVEL, INFO_LEVEL, WARN_LEVEL, ERROR_LEVEL, DPANIC_LEVEL, PANIC_LEVEL, FATAL_LEVEL} {
		err := fs.Parse([]string{"-level", expected.String()})
		if err != nil{
			t.Fatalf(err.Error())
		}
		if expected != lvl{
			t.Fatalf("Unexpected level after parsing flag.")
		}
		if expected != lvl.Get(){
			t.Fatalf("Unexpected output using flag.Getter API.")
		}
		if len(buf.String()) != 0{
			t.Fatalf("Unexpected error output parsing level flag.")
		}
		buf.Reset()
	}
	err := fs.Parse([]string{"-level", "nope"})
	if err == nil{
		t.Fatalf(err.Error())
	}
	if `invalid value "nope" for flag -level: unrecognized level: "nope"` != strings.Split(buf.String(), "\n")[0]{
		t.Fatalf("Unexpected error output from invalid flag input.")
	}
}