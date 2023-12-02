package main

import (
	"context"
	"fmt"
	"os"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/google/uuid"

	"app.bluezoneautomation.com/lambda-project-summary/v2/documents"
	"app.bluezoneautomation.com/lambda-project-summary/v2/schema"
)

const (
	INCH_FOOT   = "Inch Foot"
	SQUARE_FOOT = "Square Foot"
)

// Lambda event payload
type Event struct {
	RequestId uuid.UUID `json:"request_id"`
	ProjectId int       `json:"project_id"`
}

// Lambda function handler
func handler(ctx context.Context, event Event) error {
	project_summary := NewProjectSummary(event.RequestId, event.ProjectId)
	err := project_summary.Generate()
	return err
}

type ProjectSummary struct {
	RequestId uuid.UUID
	ProjectId int
	Filename  string
	Data      schema.ProjectSummaryData
}

func NewProjectSummary(requestId uuid.UUID, projectId int) ProjectSummary {
	return ProjectSummary{
		RequestId: requestId,
		ProjectId: projectId,
	}
}

// Generate the S3 key for the document
func (p ProjectSummary) GetKey() string {
	return fmt.Sprintf("project_summarys/%s/%s - Project Summary.xlsx", p.RequestId, p.Data.Name)
}

// Generate the project summary document
func (p *ProjectSummary) Generate() error {
	var err error
	var generator documents.ProjectSummaryGenerator

	if err = p.Fetch(); err != nil {
		return err
	}

	switch p.Data.PricingModel {
	case INCH_FOOT:
		generator = documents.NewInchFootProjectSummary(p.Data)
	case SQUARE_FOOT:
		generator = documents.NewSquareFootProjectSummary(p.Data)
	}

	if p.Filename, err = generator.Generate(); err != nil {
		return err
	}

	if err = p.Save(); err != nil {
		return err
	}

	if err = p.MarkComplete(); err != nil {
		return err
	}

	return nil
}

// Fetch the project summary data from the API
func (p *ProjectSummary) Fetch() error {
	api := NewProjectSummaryAPI()
	data, err := api.GetData(p.ProjectId)

	if err != nil {
		return err
	}

	p.Data = data
	return nil
}

// Save the project summary document to S3
func (p *ProjectSummary) Save() error {
	file, err := os.Open(p.Filename)
	if err != nil {
		return err
	}
	defer file.Close()

	sess, err := session.NewSession(&aws.Config{
		Region: aws.String("us-east-1"),
	})

	if err != nil {
		return err
	}

	uploader := s3manager.NewUploader(sess)
	key := p.GetKey()
	fmt.Printf("Uploading %s to S3\n", key)

	params := s3manager.UploadInput{
		Bucket: aws.String(S3_BUCKET),
		Key:    aws.String(key),
		Body:   file,
	}

	if _, err := uploader.Upload(&params); err != nil {
		return err
	}

	os.Remove(p.Filename)

	return nil
}

// Mark the project summary request as complete
func (p *ProjectSummary) MarkComplete() error {
	api := NewProjectSummaryAPI()
	key := p.GetKey()
	err := api.MarkComplete(p.RequestId, p.ProjectId, key)
	return err
}

// Application entrypoint
func main() {
	lambda.Start(handler)
}
