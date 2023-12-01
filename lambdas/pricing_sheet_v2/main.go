package main

import (
	"context"

	"github.com/aws/aws-lambda-go/lambda"
	//"github.com/aws/aws-sdk-go/aws"
	//"github.com/aws/aws-sdk-go/aws/session"
	//"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/google/uuid"

	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/documents"
	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/schema"
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

func (p *PricingSheet) Generate() error {
	if err := p.Fetch(); err != nil {
		return err
	}

	var generator documents.PricingSheetGenerator

	switch p.Data.PricingModel {
	case "Inch Foot":
		generator = documents.NewInchFootPricingSheet(p.Data)
	case "Square Foot":
		generator = documents.NewSquareFootPricingSheet()
	}

	filename, err := generator.Generate()

	if err != nil {
		return err
	}

	p.Filename = filename

	return nil
}

func (p *PricingSheet) Fetch() error {
	api := NewPricingSheetAPI()
	data, err := api.GetData(p.ProjectId)

	if err != nil {
		return err
	}

	p.Data = data
	return nil
}

func (p *PricingSheet) Save() error {
	return nil
}

func (p *PricingSheet) MarkComplete() error {
	return nil
}

// Application entrypoint
func main() {
	lambda.Start(handler)
}
