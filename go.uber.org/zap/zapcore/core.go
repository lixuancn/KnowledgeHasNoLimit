package zapcore

type Core interface {
	LevelEnabler
	With([]Field)Core
}