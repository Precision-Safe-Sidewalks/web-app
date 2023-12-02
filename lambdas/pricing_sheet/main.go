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

	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/documents"
	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/schema"
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
	pricing_sheet := NewPricingSheet(event.RequestId, event.ProjectId)
	err := pricing_sheet.Generate()
	return err
}

type PricingSheet struct {
	RequestId uuid.UUID
	ProjectId int
	Filename  string
	Data      schema.PricingSheetData
}

func NewPricingSheet(requestId uuid.UUID, projectId int) PricingSheet {
	return PricingSheet{
		RequestId: requestId,
		ProjectId: projectId,
	}
}

// Generate the S3 key for the document
func (p PricingSheet) GetKey() string {
	return fmt.Sprintf("pricing_sheets/%s/%s - Pricing Sheet.xlsx", p.RequestId, p.Data.Name)
}

// Generate the pricing sheet document
func (p *PricingSheet) Generate() error {
	var err error
	var generator documents.PricingSheetGenerator

	if err = p.Fetch(); err != nil {
		return err
	}

	switch p.Data.PricingModel {
	case INCH_FOOT:
		generator = documents.NewInchFootPricingSheet(p.Data)
	case SQUARE_FOOT:
		generator = documents.NewSquareFootPricingSheet(p.Data)
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

// Fetch the pricing sheet data from the API
func (p *PricingSheet) Fetch() error {
	api := NewPricingSheetAPI()
	data, err := api.GetData(p.ProjectId)

	if err != nil {
		return err
	}

	p.Data = data
	return nil
}

// Save the pricing sheet document to S3
func (p *PricingSheet) Save() error {
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

// Mark the pricing sheet request as complete
func (p *PricingSheet) MarkComplete() error {
	api := NewPricingSheetAPI()
	key := p.GetKey()
	err := api.MarkComplete(p.RequestId, p.ProjectId, key)
	return err
}

// Application entrypoint
func main() {
	lambda.Start(handler)
}
