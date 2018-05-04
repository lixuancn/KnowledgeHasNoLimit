package version

import (
	"fmt"
	"runtime"
)

const BINARY = "1.0.0-alpha"

func String(app string) string {
	return fmt.Sprintf("%s v%s (built w/%s)", app, BINARY, runtime.Version())
}
