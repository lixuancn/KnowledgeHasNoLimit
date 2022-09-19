package main

import (
	"demo/geedemo/gee"
	"fmt"
	"net/http"
)

func main() {
	server := gee.New()
	server.Use(gee.Logger())
	// curl "http://localhost:8888/"
	server.GET("/", func(ctx *gee.Context) {
		ctx.HTML(http.StatusOK, "This is Index")
	})
	v1 := server.Group("/v1")
	{
		// curl "http://0.0.0.0:8888/v1/header"
		v1.GET("/header", func(ctx *gee.Context) {
			data := ""
			for k, v := range ctx.R.Header {
				data += fmt.Sprintf("Header[%q] = %q\n", k, v)
			}
			ctx.String(http.StatusOK, data)
		})
		// curl "http://localhost:8888/v1/hello?name=lane"
		v1.GET("/hello", func(ctx *gee.Context) {
			ctx.String(http.StatusOK, "hello %s", ctx.Query("name"))
		})
		// curl "http://localhost:8888/v1/login" -X POST -d "username=name&password=pw"
		v1.POST("/login", func(ctx *gee.Context) {
			ctx.Json(http.StatusOK, gee.H{
				"username": ctx.PostForm("username"),
				"password": ctx.PostForm("password"),
			})
		})
	}
	v2 := server.Group("/v2")
	v2.Use(middlewaresV2())
	{
		// curl "http://localhost:8888/v2/hello/lane"
		v2.GET("/hello/:name", func(ctx *gee.Context) {
			ctx.String(http.StatusOK, "hello %s, you're at %s\n", ctx.Param("name"), ctx.Path)
		})
		// curl "http://localhost:8888/v2/assets/css/geektutu.css"
		v2.GET("/assets/*filepath", func(ctx *gee.Context) {
			ctx.Json(http.StatusOK, gee.H{"filepath": ctx.Param("filepath")})
		})
	}
	err := server.Run(":8888")
	if err != nil {
		panic(err)
	}
}

func middlewaresV2() gee.HandlerFunc {
	return func(ctx *gee.Context) {
		fmt.Println("This is a middlewares for v2 group. start")
		ctx.Next()
		fmt.Println("This is a middlewares for v2 group. end")
	}
}
