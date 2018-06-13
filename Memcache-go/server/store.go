package server

var DataList = map[string]string{}

func Get(key string)(string, error){
	if data, ok := DataList[key]; ok{
		return data, nil
	}
	return "", nil
}

func Set(key string, value string)error{
	DataList[key] = value
	return nil
}