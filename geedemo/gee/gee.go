package gee

import "net/http"

type HandlerFunc func(ctx *Context)

type Engine struct {
	router *router
}

func New() *Engine {
	return &Engine{
		router: newRouter(),
	}
}

func (engine *Engine) GET(pattern string, handlerFunc HandlerFunc) {
	engine.router.addRoute("GET", pattern, handlerFunc)
}

func (engine *Engine) POST(pattern string, handlerFunc HandlerFunc) {
	engine.router.addRoute("POST", pattern, handlerFunc)
}

func (engine *Engine) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	ctx := newContext(w, r)
	engine.router.handle(ctx)
}

func (engine *Engine) Run(addr string) error {
	return http.ListenAndServe(addr, engine)
}
