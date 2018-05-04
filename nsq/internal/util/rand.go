package util

import "math/rand"

func UniqRands(quantity, maxval int) []int {
	if maxval < quantity {
		quantity = maxval
	}
	intSlice := make([]int, maxval)
	for i := 0; i < maxval; i++ {
		intSlice[i] = i
	}
	for i := 0; i < quantity; i++ {
		j := rand.Int()%maxval + i
		intSlice[i], intSlice[j] = intSlice[j], intSlice[i]
		maxval--
	}
	return intSlice[0:quantity]
}
