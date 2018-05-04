package app

import "strings"

type StringArray []string

func (sa *StringArray) Set(s string) error {
	*sa = append(*sa, s)
	return nil
}

func (sa *StringArray) String() string {
	return strings.Join(*sa, ",")
}
