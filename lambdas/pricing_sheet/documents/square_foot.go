package documents

import (
	"fmt"

	"github.com/google/uuid"
	"github.com/xuri/excelize/v2"

	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/schema"
)

const (
	TEMPLATE_SQUARE_FOOT = "templates/TEMPLATE - SQFT Pricing - 11-28-23.xlsx"
)

type SquareFootPricingSheet struct {
	Data schema.PricingSheetData
}

// Construct an square foot pricing sheet generator
func NewSquareFootPricingSheet(data schema.PricingSheetData) SquareFootPricingSheet {
	return SquareFootPricingSheet{Data: data}
}

// Generate the pricing sheet document
func (p SquareFootPricingSheet) Generate() (string, error) {
	workbook, err := excelize.OpenFile(TEMPLATE_SQUARE_FOOT)

	if err != nil {
		return "", err
	}

	defer workbook.Close()

	p.UpdateSummary(workbook)
	p.UpdateSurveyData(workbook)

	workbook.UpdateLinkedValue()

	filename := p.GenerateFilename()
	err = workbook.SaveAs(filename)

	return filename, err
}

// Generate a unique filename for a pricing sheet
func (p SquareFootPricingSheet) GenerateFilename() string {
	return fmt.Sprintf("/tmp/%s.xlsx", uuid.New().String())
}

// Update the "SUMMARY" worksheet
func (p SquareFootPricingSheet) UpdateSummary(f *excelize.File) {
	sheet := "SUMMARY"

	f.SetCellValue(sheet, "B2", p.Data.Customer.Name)
	f.SetCellValue(sheet, "B4", p.Data.Name)
	f.SetCellValue(sheet, "K17", p.Data.Pricing.EstimatedSidewalkMiles)

	// TODO: handle CLIN (H13/H14/H15)
}

// Update the "DATA1" worksheet
func (p SquareFootPricingSheet) UpdateSurveyData(f *excelize.File) {
	sheet := "DATA1"

	for index, group := range p.Data.Measurements {
		offset := 4 + (index * 401)
		row_label := offset + 400

		f.SetCellValue(sheet, fmt.Sprintf("B%d", row_label), group.Name)

		for i, item := range group.Measurements {
			f.SetCellValue(sheet, fmt.Sprintf("B%d", offset+i), SafeString(item.Address))
			f.SetCellValue(sheet, fmt.Sprintf("C%d", offset+i), item.Description())
			f.SetCellValue(sheet, fmt.Sprintf("D%d", offset+i), item.Latitude)
			f.SetCellValue(sheet, fmt.Sprintf("E%d", offset+i), item.Longitude)
			f.SetCellValue(sheet, fmt.Sprintf("F%d", offset+i), SafeString(item.HazardSize))
			f.SetCellValue(sheet, fmt.Sprintf("G%d", offset+i), item.Area)
			f.SetCellValue(sheet, fmt.Sprintf("H%d", offset+i), item.Width)
			f.SetCellValue(sheet, fmt.Sprintf("I%d", offset+i), item.Length)
		}
	}
}
