package GoCache

import (
	"sync"
	"time"
)

type CacheItem struct{
	sync.RWMutex
	key interface{}
	value interface{}
	lifeSpan time.Duration
	createTime time.Time
	accessTime time.Time
	accessCount int64
	aboutToExpire func(key interface{})
}

func NewCacheItem(key, value interface{}, lifeSpan time.Duration)*CacheItem{
	t := time.Now()
	return &CacheItem{
		key: key,
		value: value,
		lifeSpan: lifeSpan,
		createTime: t,
		accessTime: t,
		accessCount: 0,
		aboutToExpire: nil,
	}
}

func (item *CacheItem)KeepAlive(){
	item.Lock()
	defer item.Unlock()
	item.accessTime = time.Now()
	item.accessCount++
}

func (item *CacheItem)GetLifeSpan()time.Duration{
	return item.lifeSpan
}
func (item *CacheItem)GetAccessTime()time.Time{
	item.RLock()
	defer item.RUnlock()
	return item.accessTime
}
func (item *CacheItem)GetCreateTime()time.Time{
	return item.createTime
}
func (item *CacheItem)GetAccessCount()int64{
	item.RLock()
	defer item.RUnlock()
	return item.accessCount
}
func (item *CacheItem)GetKey()interface{}{
	return item.key
}
func (item *CacheItem)GetValue()interface{}{
	return item.value
}
func (item *CacheItem)SetAboutToExpireCallback(f func(interface{})){
	item.Lock()
	defer item.Unlock()
	item.aboutToExpire = f
}