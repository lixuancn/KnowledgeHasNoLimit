package nsqlookupd

import (
	"nsq/internal/http_api"
	"nsq/internal/version"
	"github.com/julienschmidt/httprouter"
	"net/http"
	"net/http/pprof"
	"github.com/mcuadros/go-version"
)

type httpServer struct {
	ctx *Context
	router http.Handler
}

func newHTTPServer(ctx *Context)*httpServer{
	log := http_api.Log(ctx.nsqlookupd.logf)
	router := httprouter.New()
	router.HandleMethodNotAllowed = true
	router.PanicHandler = http_api.LogPanicHandler(ctx.nsqlookupd.logf)
	router.NotFound = http_api.LogNotFoundHandler(ctx.nsqlookupd.logf)
	router.MethodNotAllowed = http_api.LogMethodNotAllowedHandler(ctx.nsqlookupd.logf)
	s := &httpServer{
		ctx: ctx,
		router: router,
	}

	router.Handle("GET", "/ping", http_api.Decorate(s.pingHandler, log, http_api.PlainText))
	router.Handle("GET", "/info", http_api.Decorate(s.doInfo, log, http_api.V1))

	// v1 negotiate
	router.Handle("GET", "/debug", http_api.Decorate(s.doDebug, log, http_api.V1))
	router.Handle("GET", "/lookup", http_api.Decorate(s.doLookup, log, http_api.V1))
	router.Handle("GET", "/topics", http_api.Decorate(s.doTopics, log, http_api.V1))
	router.Handle("GET", "/channels", http_api.Decorate(s.doChannels, log, http_api.V1))
	router.Handle("GET", "/nodes", http_api.Decorate(s.doNodes, log, http_api.V1))

	// only v1
	router.Handle("POST", "/topic/create", http_api.Decorate(s.doCreateTopic, log, http_api.V1))
	router.Handle("POST", "/topic/delete", http_api.Decorate(s.doDeleteTopic, log, http_api.V1))
	router.Handle("POST", "/channel/create", http_api.Decorate(s.doCreateChannel, log, http_api.V1))
	router.Handle("POST", "/channel/delete", http_api.Decorate(s.doDeleteChannel, log, http_api.V1))
	router.Handle("POST", "/topic/tombstone", http_api.Decorate(s.doTombstoneTopicProducer, log, http_api.V1))

	// debug
	router.HandlerFunc("GET", "/debug/pprof", pprof.Index())
	router.HandlerFunc("GET", "/debug/pprof/cmdline", pprof.Cmdline)
	router.HandlerFunc("GET", "/debug/pprof/symbol", pprof.Symbol)
	router.HandlerFunc("POST", "/debug/pprof/symbol", pprof.Symbol)
	router.HandlerFunc("GET", "/debug/pprof/profile", pprof.Profile)
	router.Handler("GET", "/debug/pprof/heap", pprof.Handler("heap"))
	router.Handler("GET", "/debug/pprof/goroutine", pprof.Handler("goroutine"))
	router.Handler("GET", "/debug/pprof/block", pprof.Handler("block"))
	router.Handler("GET", "/debug/pprof/threadcreate", pprof.Handler("threadcreate"))

	return s
}

func (s *httpServer)ServeHTTP(w http.ResponseWriter, req *http.Request){
	s.router.ServeHTTP(w, req)
}

func (s *httpServer)pingHandler(w http.ResponseWriter, req *http.Request, ps httprouter.Params)(interface{}, error){
	return "OK", nil
}

func (s *httpServer)doInfo(w http.ResponseWriter, req *http.Request, ps httprouter.Params)(interface{}, error){
	return struct {
		Version string `json:"version"`
	}{
		Version: version.BINARY,
	}, nil
}
func (s *httpServer)doTopic(w http.ResponseWriter, req *http.Request, ps httprouter.Params)(interface{}, error){
	topics := s.ctx.nsqlookupd.DB.FindRegistrations("topic", "*", "").Keys()
	return map[string]interface{}{
		"topics": topics,
	}, nil
}

func (s *httpServer)bak(w http.ResponseWriter, req *http.Request){}