package zapcore

import "zap/internal/color"

var (
	levelToColor = map[Level]color.Color{
		DEBUG_LEVEL: color.MAGENTA,
		INFO_LEVEL: color.BULE,
		WARN_LEVEL: color.YELLOW,
		ERROR_LEVEL: color.RED,
		DPANIC_LEVEL: color.RED,
		PANIC_LEVEL: color.RED,
		FATAL_LEVEL: color.RED,
	}
	unknownLevelColor = color.RED
	levelToLowercaseColorString = make(map[Level]string, len(levelToColor))
	levelToCapitalColorString = make(map[Level]string, len(levelToColor))
)

func init(){
	for level, color  := range levelToColor{
		levelToLowercaseColorString[level] =  color.Add(level.String())
		levelToCapitalColorString[level] = color.Add(level.CapitalString())
	}
}