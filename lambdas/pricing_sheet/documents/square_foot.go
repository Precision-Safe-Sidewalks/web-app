package documents

import (
	"fmt"
	//"strconv"

	"github.com/google/uuid"
	"github.com/xuri/excelize/v2"

	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/schema"
)

const (
	TEMPLATE_SQUARE_FOOT = "templates/TEMPLATE SQFT Pricing - 11-28-23.xlsx"
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

	// TODO: calculate these
	groupRows := []int{17, 918, 1182, 1446, 1708, 2108, 2436, 2700, 2964, 3228, 3556, 4572, 4772, 4972}

	for index, group := range p.Data.Measurements {
		offset := groupRows[index]

		f.SetCellValue(sheet, fmt.Sprintf("B%d", groupRows[index+1]-1), group.Name)

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
