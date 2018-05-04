package app

import (
	"fmt"
	"log"
	"sort"
	"strconv"
	"strings"
)

type FloatArray []float64

func (fa *FloatArray) Set(param string) error {
	fmt.Println(1213)
	for _, s := range strings.Split(param, ",") {
		v, err := strconv.ParseFloat(s, 64)
		if err != nil {
			log.Fatalf("Could not parse %s", s)
			return err
		}
		*fa = append(*fa, v)
	}
	sort.Sort(*fa)

	return nil
}

func (fa *FloatArray) String() string {
	var s []string
	for _, v := range *fa {
		s = append(s, fmt.Sprintf("%f", v))
	}
	return strings.Join(s, ",")
}

func (fa FloatArray) Swap(i, j int) {
	fa[i], fa[j] = fa[j], fa[i]
	fmt.Println(222)
}

func (fa FloatArray) Less(i, j int) bool { return fa[i] > fa[j] }

func (fa FloatArray) Len() int { return len(fa) }
