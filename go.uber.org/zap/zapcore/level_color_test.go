package zapcore

import (
	"testing"
)

func TestAllLevelsCoveredByLevelString(t *testing.T) {
	numLevels := int((MAX_LEVEL - MIN_LEVEL) + 1)

	isComplete := func(m map[Level]string) bool {
		return len(m) == numLevels
	}
	if !isComplete(levelToLowercaseColorString){
		t.Fatal("Colored lowercase strings don't cover all levels.")
	}
	if !isComplete(levelToLowercaseColorString){
		t.Fatal("Colored capital strings don't cover all levels.")
	}
}
