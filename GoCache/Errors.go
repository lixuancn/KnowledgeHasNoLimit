package GoCache

import "errors"

var ERROR_KEY_NOT_FOUND = errors.New("key not found in cache")

var ERROR_KEY_NOT_FOUND_OR_LOADABLE = errors.New("key not found and could not be loaded into cache")