package main

import (
	"demo/geedemo/gee"
	"net/http"
)

func main() {
	server := gee.New()
	// curl "http://localhost:8888/"
	server.GET("/", func(ctx *gee.Context) {
		ctx.HTML(http.StatusOK, "This is Index")
	})
	// curl "http://0.0.0.0:8888/header"
	server.GET("/header", func(ctx *gee.Context) {
		for k, v := range ctx.R.Header {
			ctx.String(http.StatusOK, "Header[%q] = %q\n", k, v)
		}
	})
	// curl "http://localhost:8888/hello?name=lane"
	server.GET("/hello", func(ctx *gee.Context) {
		ctx.String(http.StatusOK, "hello %s", ctx.Query("name"))
	})
	// curl "http://localhost:8888/login" -X POST -d "username=name&password=pw"
	server.POST("/login", func(ctx *gee.Context) {
		ctx.Json(http.StatusOK, gee.H{
			"username": ctx.PostForm("username"),
			"password": ctx.PostForm("password"),
		})
	})
	// curl "http://localhost:8888/hello/lane"
	server.GET("/hello/:name", func(ctx *gee.Context) {
		ctx.String(http.StatusOK, "hello %s, you're at %s\n", ctx.Param("name"), ctx.Path)
	})
	// curl "http://localhost:8888/assets/css/geektutu.css"
	server.GET("/assets/*filepath", func(ctx *gee.Context) {
		ctx.Json(http.StatusOK, gee.H{"filepath": ctx.Param("filepath")})
	})
	err := server.Run(":8888")
	if err != nil {
		panic(err)
	}
}
