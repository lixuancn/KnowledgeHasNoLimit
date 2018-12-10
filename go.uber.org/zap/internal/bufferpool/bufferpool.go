package bufferpool

import "zap/buffer"

var pool = buffer.NewPool()
var Get = pool.Get