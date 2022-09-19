package gee

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type H map[string]interface{}

type Context struct {
	W          http.ResponseWriter
	R          *http.Request
	Path       string
	Method     string
	Params     map[string]string
	StatusCode int
	handlers   []HandlerFunc
	index      int
}

func newContext(w http.ResponseWriter, r *http.Request) *Context {
	return &Context{
		W:        w,
		R:        r,
		Path:     r.URL.Path,
		Method:   r.Method,
		handlers: make([]HandlerFunc, 0),
		index:    -1,
	}
}

func (c *Context) Next() {
	c.index++
	for ; c.index < len(c.handlers); c.index++ {
		c.handlers[c.index](c)
	}
}

func (c *Context) Param(key string) string {
	value, _ := c.Params[key]
	return value
}

func (c *Context) PostForm(key string) string {
	return c.R.FormValue(key)
}

func (c *Context) Query(key string) string {
	return c.R.URL.Query().Get(key)
}

func (c *Context) Status(code int) {
	c.StatusCode = code
	c.W.WriteHeader(code)
}

func (c *Context) SetHeader(key, value string) {
	c.W.Header().Set(key, value)
}

func (c *Context) String(code int, format string, values ...interface{}) {
	c.SetHeader("Context-type", "text/plain")
	c.Status(code)
	_, err := c.W.Write([]byte(fmt.Sprintf(format, values...)))
	if err != nil {
		c.error(err)
	}
}

func (c *Context) Json(code int, obj interface{}) {
	c.SetHeader("Context-type", "application/json")
	c.Status(code)
	encoder := json.NewEncoder(c.W)
	if err := encoder.Encode(obj); err != nil {
		c.error(err)
	}
}

func (c *Context) Data(code int, data []byte) {
	c.Status(code)
	_, err := c.W.Write(data)
	if err != nil {
		c.error(err)
	}
}

func (c *Context) HTML(code int, html string) {
	c.SetHeader("Context-type", "text/html")
	c.Status(code)
	_, err := c.W.Write([]byte(html))
	if err != nil {
		c.error(err)
	}
}

func (c *Context) error(err error) {
	c.httpError("server error: "+err.Error(), http.StatusInternalServerError)
}

func (c *Context) httpError(error string, code int) {
	http.Error(c.W, error, code)
}

func (c *Context) NotFount() {
	http.NotFound(c.W, c.R)
}
