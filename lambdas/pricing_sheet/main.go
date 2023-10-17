package main

import (
	"context"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/google/uuid"
	"github.com/xuri/excelize/v2"
)

const (
	TEMPLATE_INCH_FOOT     = "templates/TEMP Pricing Inch Foot  - 10-2-2023- FINAL.xltx"
	TEMPLATE_SQUARE_FOOT   = ""
	TEMPLATE_SURVEY_GROUPS = 20
)

const (
	WORKSHEET_PROJECT_SURVEY_COST = "Project Survey Cost"
	WORKSHEET_JPC_FULL_SCOPE      = "JPC - Full Scope"
	WORKSHEET_SUMMARY             = "SUMMARY"
	WORKSHEET_GREEN_SAVINGS       = "GREEN SAVINGS"
)

const (
	S3_BUCKET = "precision-safe-sidewalks"
)

// Lambda event payload
type Event struct {
	RequestId uuid.UUID `json:"request_id"`
}

// Lambda function handler
func handler(ctx context.Context, event Event) (string, error) {
	sheet := NewPricingSheet(event.RequestId)

	sheet.Generate()
	sheet.Upload()
	sheet.Complete()

	return fmt.Sprintf("Test output"), nil
}

// Pricing sheet generator
type PricingSheet struct {
	RequestId uuid.UUID
	Filename  string
	Data      *PricingSheetData
	S3Key     string
}

// Construct a new Pricing Sheet
func NewPricingSheet(requestId uuid.UUID) *PricingSheet {
	return &PricingSheet{
		RequestId: requestId,
		Data:      NewPricingSheetData(requestId),
		Filename:  fmt.Sprintf("/tmp/%s.xlsx", requestId),
	}
}

// Generate the Pricing Sheet Excel file
func (p *PricingSheet) Generate() {
	p.Data.Fetch()

	template := p.GetTemplate()
	workbook, err := excelize.OpenFile(template)

	if err != nil {
		panic(err)
	}

	defer workbook.Close()

	p.UpdateProjectSurveyCost(workbook)
	p.UpdateJPCFullScope(workbook)
	p.UpdateSummary(workbook)
	p.UpdateGreenSavings(workbook)
	p.UpdateSurveyData(workbook)

	workbook.UpdateLinkedValue()

	fmt.Printf("Saving %s\n", p.Filename)

	if err := workbook.SaveAs(p.Filename); err != nil {
		panic(err)
	}
}

// Return the template file path
func (p *PricingSheet) GetTemplate() string {
	switch p.Data.PricingModel {
	case 1:
		return TEMPLATE_INCH_FOOT
	case 2:
		return TEMPLATE_SQUARE_FOOT
	default:
		panic("Invalid pricing model")
	}
}

// Update the "Project Survey Cost" worksheet
func (p *PricingSheet) UpdateProjectSurveyCost(f *excelize.File) {
	sheet := WORKSHEET_PROJECT_SURVEY_COST

	f.SetCellValue(sheet, "D4", p.Data.EstimatedSidewalkMiles)
	f.SetCellValue(sheet, "D5", p.Data.SurveyorSpeed)
	f.SetCellValue(sheet, "D7", BoolToInt(p.Data.SurveyHazards == 1))
	f.SetCellValue(sheet, "D8", BoolToInt(p.Data.SurveyHazards == 2))
	f.SetCellValue(sheet, "D9", BoolToInt(p.Data.SurveyHazards == 3))
	f.SetCellValue(sheet, "D11", BoolToInt(p.Data.HazardDensity == 1))
	f.SetCellValue(sheet, "D12", BoolToInt(p.Data.HazardDensity == 2))
	f.SetCellValue(sheet, "D13", BoolToInt(p.Data.HazardDensity == 3))
	f.SetCellValue(sheet, "D15", BoolToInt(p.Data.PanelSize == 1))
	f.SetCellValue(sheet, "D16", BoolToInt(p.Data.PanelSize == 2))
	f.SetCellValue(sheet, "D17", BoolToInt(p.Data.PanelSize == 3))
}

// Update the "JPC - Full Scope" worksheet
func (p *PricingSheet) UpdateJPCFullScope(f *excelize.File) {
	sheet := WORKSHEET_JPC_FULL_SCOPE

	f.SetCellValue(sheet, "C6", p.Data.DistanceFromSurveyor)
	f.SetCellValue(sheet, "C7", p.Data.DistanceFromOps)
	f.SetCellValue(sheet, "C10", p.Data.TerritoryRate)
	f.SetCellValue(sheet, "C11", p.Data.CommissionRate)
}

// Update the "SUMMARY" worksheet
func (p *PricingSheet) UpdateSummary(f *excelize.File) {
	sheet := WORKSHEET_SUMMARY

	f.SetCellValue(sheet, "D3", p.Data.OrganizationName)
	f.SetCellValue(sheet, "E3", p.Data.ContactAddress)
	f.SetCellValue(sheet, "F3", p.Data.BDM)
	f.SetCellValue(sheet, "G3", p.Data.Surveyor)
	f.SetCellValue(sheet, "H3", "") // TODO: alt deal owner
	f.SetCellValue(sheet, "I3", p.Data.ContactName)
	f.SetCellValue(sheet, "J3", p.Data.ContactTitle)
	f.SetCellValue(sheet, "K3", p.Data.ContactEmail)
	f.SetCellValue(sheet, "L3", p.Data.ContactPhoneNumber)
}

// Update the "GREEN SAVINGS" worksheet
func (p *PricingSheet) UpdateGreenSavings(f *excelize.File) {
	sheet := WORKSHEET_GREEN_SAVINGS

	f.SetCellValue(sheet, "E44", p.Data.NumberOfTechnicians)
	f.SetCellValue(sheet, "F44", p.Data.NumberOfTechnicians)
}

// Update the survey data worksheets
func (p *PricingSheet) UpdateSurveyData(f *excelize.File) {
	groups := p.DistributeSurveyData()
	sheetId := 1
	offset := 26

	for group, items := range groups {
		sheet := strconv.Itoa(sheetId)

		f.SetCellValue(sheet, "C1", group)

		for i, item := range items {
			f.SetCellValue(sheet, fmt.Sprintf("B%d", i+offset), BoolToInt(item.HazardSize == "S"))
			f.SetCellValue(sheet, fmt.Sprintf("C%d", i+offset), BoolToInt(item.HazardSize == "M"))
			f.SetCellValue(sheet, fmt.Sprintf("D%d", i+offset), BoolToInt(item.HazardSize == "L"))
			f.SetCellValue(sheet, fmt.Sprintf("E%d", i+offset), item.CurbLength)
			f.SetCellValue(sheet, fmt.Sprintf("F%d", i+offset), item.Address)
			f.SetCellValue(sheet, fmt.Sprintf("G%d", i+offset), item.Width)
			f.SetCellValue(sheet, fmt.Sprintf("H%d", i+offset), item.Length)
			f.SetCellValue(sheet, fmt.Sprintf("J%d", i+offset), item.MeasuredHazardLength)
			f.SetCellValue(sheet, fmt.Sprintf("K%d", i+offset), item.InchFeet)
			f.SetCellValue(sheet, fmt.Sprintf("T%d", i+offset), item.ObjectId)
		}

		sheetId++
	}
}

// Distribute the survey data by the survey group. If more than the allowed
// number of groups are used, combine the two smallest groups until the
// constraint is satisfied.
func (p *PricingSheet) DistributeSurveyData() map[string][]SurveyRecord {
	groups := make(map[string][]SurveyRecord)

	for _, record := range p.Data.SurveyData {
		if items, ok := groups[record.SurveyGroup]; ok {
			groups[record.SurveyGroup] = append(items, record)
		} else {
			groups[record.SurveyGroup] = []SurveyRecord{record}
		}
	}

	for len(groups) > TEMPLATE_SURVEY_GROUPS {
		minGroups := []string{}
		minCounts := []int{}

		for group, items := range groups {
			count := len(items)

			if len(minGroups) < 2 {
				minGroups = append(minGroups, group)
				minCounts = append(minCounts, count)
				continue
			}

			if count < minCounts[0] {
				minGroups[1] = minGroups[0]
				minCounts[1] = minCounts[0]
				minGroups[0] = group
				minCounts[0] = count
			} else if count < minCounts[1] {
				minGroups[1] = group
				minCounts[1] = count
			}
		}

		name := strings.Join(minGroups[:], " & ")
		items := append(groups[minGroups[0]], groups[minGroups[1]]...)
		groups[name] = items

		delete(groups, minGroups[0])
		delete(groups, minGroups[1])
	}

	return groups
}

// Upload the Pricing Sheet Excel file to S3
func (p *PricingSheet) Upload() {
	f, err := os.Open(p.Filename)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	sess, err := session.NewSession(&aws.Config{
		Region: aws.String("us-east-1"),
	})

	if err != nil {
		panic(err)
	}

	uploader := s3manager.NewUploader(sess)
	key := fmt.Sprintf("pricing_sheets/%s/%s - Pricing Sheet.xlsx", p.RequestId, p.Data.ProjectName)
	fmt.Printf("Uploading %s to S3\n", key)

	params := s3manager.UploadInput{
		Bucket: aws.String(S3_BUCKET),
		Key:    aws.String(key),
		Body:   f,
	}

	if _, err := uploader.Upload(&params); err != nil {
		panic(err)
	}

	p.S3Key = key
	os.Remove(p.Filename)
}

// Mark the Pricing Sheet request as complete
func (p *PricingSheet) Complete() {
	query := `
		UPDATE repairs_pricingsheetrequest SET
			s3_bucket = $1,
			s3_key = $2,
			updated_at = CURRENT_TIMESTAMP
		WHERE request_id = $3
	`

	ctx := context.Background()
	db := GetDatabase()
	defer db.Close(ctx)

	_, err := db.Exec(ctx, query, S3_BUCKET, p.S3Key, p.RequestId.String())
	if err != nil {
		panic(err)
	}
}

// Lambda entrypoint handler
func main() {
	lambda.Start(handler)
}
