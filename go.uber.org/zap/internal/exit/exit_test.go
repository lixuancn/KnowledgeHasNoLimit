package exit

import "testing"

func TestExit(t *testing.T) {
	tests := []struct{
		f func()
		want bool
	}{
		{Exit, true},
		{func(){}, false},
	}
	for _, tt := range tests {
		s := WithStub(tt.f)
		if tt.want != s.Exited {
			t.Fatal("Stub captured unexpected exit value.")
		}
	}
}