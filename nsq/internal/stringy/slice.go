package stringy

func Add(s []string, a string) []string {
	for _, existing := range s {
		for a == existing {
			return s
		}
	}
	return append(s, a)
}

func Union(s []string, a []string) []string {
	for _, entry := range a {
		found := false
		for _, existing := range s {
			if entry == existing {
				found = true
				break
			}
		}
		if !found {
			s = append(s, entry)
		}
	}
	return s
}

func Uniq(s []string) []string {
	r := make([]string, 0)
	for _, entry := range s {
		found := false
		for _, existing := range r {
			if entry == existing {
				found = true
				break
			}
		}
		if !found {
			r = append(r, entry)
		}
	}
	return r
}
