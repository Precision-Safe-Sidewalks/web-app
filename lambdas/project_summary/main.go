package main

import (
	"context"
	"fmt"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/google/uuid"
)

// Lambda event payload
type Event struct {
	RequestId uuid.UUID `json:"request_id"`
}

// Lambda function handler
func handler(ctx context.Context, event Event) (string, error) {
	summary := NewProjectSummary(event.RequestId)

	summary.Generate()
	summary.Upload()
	summary.Complete()

	// FIXME: update the response
	return fmt.Sprintf("Test output"), nil
}

// Lambda entrypoint handler
func main() {
	lambda.Start(handler)
}
