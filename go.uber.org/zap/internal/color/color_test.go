package color

import "testing"

func TestColor(t *testing.T) {
	t.Log(BLACK)
	t.Log(RED)
	t.Log(GREEN)
}

func TestColor_Add(t *testing.T) {
	c := RED
	str := c.Add("你好")
	t.Log(str)
}