package common

import (
	"context"
	"io"
	"log"
	"os"

	"github.com/cloudwego/eino-ext/components/model/openai"
	"github.com/cloudwego/eino/schema"
)

func GetModelClient(ctx context.Context) (*openai.ChatModel, error) {
	return openai.NewChatModel(ctx, &openai.ChatModelConfig{
		BaseURL: "https://ark.cn-beijing.volces.com/api/v3",
		Model:   "doubao-1-5-pro-32k-character-250715",
		APIKey:  os.Getenv("HOU_SHAN_FANG_ZHOU_API_KEY"),
	})
}

func GetStreamResult(ctx context.Context, sr *schema.StreamReader[*schema.Message]) {
	defer sr.Close()
	i := 0
	for {
		msg, err := sr.Recv()
		if err == io.EOF {
			return
		}
		if err != nil {
			log.Fatalf("recv failed: %v", err)
		}
		log.Printf("message[%d]: %+v\n", i, msg)
		i++
	}
}
