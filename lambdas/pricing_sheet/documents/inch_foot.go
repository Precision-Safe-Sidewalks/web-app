package documents

import (
	"fmt"
	"strconv"

	"github.com/google/uuid"
	"github.com/xuri/excelize/v2"

	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/schema"
	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/utils"
)

const (
	TEMPLATE_INCH_FOOT = "templates/TEMP Pricing Inch Foot - 10-2-2023- FINAL.xltx"
)

type InchFootPricingSheet struct {
	Data schema.PricingSheetData
}

// Construct an inch foot pricing sheet generator
func NewInchFootPricingSheet(data schema.PricingSheetData) InchFootPricingSheet {
	return InchFootPricingSheet{Data: data}
}

// Generate the pricing sheet document
func (p InchFootPricingSheet) Generate() (string, error) {
	workbook, err := excelize.OpenFile(TEMPLATE_INCH_FOOT)

	if err != nil {
		return "", err
	}

	defer workbook.Close()

	p.UpdateProjectSurveyCost(workbook)
	p.UpdateJPCFullScope(workbook)
	p.UpdateSummary(workbook)
	p.UpdateGreenSavings(workbook)
	p.UpdateSurveyData(workbook)

	workbook.UpdateLinkedValue()

	filename := p.GenerateFilename()
	err = workbook.SaveAs(filename)

	return filename, err
}

// Generate a unique filename for a pricing sheet
func (p InchFootPricingSheet) GenerateFilename() string {
	return fmt.Sprintf("/tmp/%s.xlsx", uuid.New().String())
}

// Update the "Project Survey Cost" worksheet
func (p InchFootPricingSheet) UpdateProjectSurveyCost(f *excelize.File) {
	sheet := "Project Survey Cost"

	f.SetCellValue(sheet, "D4", p.Data.Pricing.EstimatedSidewalkMiles)
	f.SetCellValue(sheet, "D5", p.Data.Pricing.SurveyorSpeed)
	f.SetCellValue(sheet, "D7", utils.BoolToInt(p.Data.Pricing.SurveyHazards == 1))
	f.SetCellValue(sheet, "D8", utils.BoolToInt(p.Data.Pricing.SurveyHazards == 2))
	f.SetCellValue(sheet, "D9", utils.BoolToInt(p.Data.Pricing.SurveyHazards == 3))
	f.SetCellValue(sheet, "D11", utils.BoolToInt(p.Data.Pricing.HazardDensity == 1))
	f.SetCellValue(sheet, "D12", utils.BoolToInt(p.Data.Pricing.HazardDensity == 2))
	f.SetCellValue(sheet, "D13", utils.BoolToInt(p.Data.Pricing.HazardDensity == 3))
	f.SetCellValue(sheet, "D15", utils.BoolToInt(p.Data.Pricing.PanelSize == 1))
	f.SetCellValue(sheet, "D16", utils.BoolToInt(p.Data.Pricing.PanelSize == 2))
	f.SetCellValue(sheet, "D17", utils.BoolToInt(p.Data.Pricing.PanelSize == 3))
}

// Update the "JPC - Full Scope" worksheet
func (p InchFootPricingSheet) UpdateJPCFullScope(f *excelize.File) {
	sheet := "JPC - Full Scope"

	f.SetCellValue(sheet, "C6", p.Data.Pricing.DistanceFromSurveyor)
	f.SetCellValue(sheet, "C7", p.Data.Pricing.DistanceFromOps)
	f.SetCellValue(sheet, "C10", p.Data.Territory.RoyaltyRate/100.0)
	f.SetCellValue(sheet, "C11", p.Data.Pricing.CommissionRate/100.0)
}

// Update the "SUMMARY" worksheet
func (p InchFootPricingSheet) UpdateSummary(f *excelize.File) {
	sheet := "SUMMARY"

	f.SetCellValue(sheet, "D3", p.Data.Customer.Name)
	f.SetCellValue(sheet, "F3", p.Data.BDM.Initials)
	f.SetCellValue(sheet, "H3", "") // TODO: alt deal owner

	if p.Data.Surveyor != nil {
		f.SetCellValue(sheet, "G3", p.Data.Surveyor.Initials)
	}

	if p.Data.Contact != nil {
		f.SetCellValue(sheet, "E3", utils.SafeString(p.Data.Contact.Address))
		f.SetCellValue(sheet, "I3", p.Data.Contact.Name)
		f.SetCellValue(sheet, "J3", utils.SafeString(p.Data.Contact.Title))
		f.SetCellValue(sheet, "K3", utils.SafeString(p.Data.Contact.Email))
		f.SetCellValue(sheet, "L3", utils.SafeString(p.Data.Contact.PhoneNumber))
	}
}

// Update the "GREEN SAVINGS" worksheet
func (p InchFootPricingSheet) UpdateGreenSavings(f *excelize.File) {
	sheet := "GREEN SAVINGS"

	f.SetCellValue(sheet, "E44", p.Data.Pricing.NumberOfTechnicians)
	f.SetCellValue(sheet, "F44", p.Data.Pricing.NumberOfTechnicians)
}

// Update the survey data worksheets
func (p InchFootPricingSheet) UpdateSurveyData(f *excelize.File) {
	offset := 26

	for sheetId, group := range p.Data.Measurements {
		sheet := strconv.Itoa(sheetId + 1)
		f.SetCellValue(sheet, "C1", group.Name)

		for i, item := range group.Measurements {
			hazard_size := utils.SafeString(item.HazardSize)

			f.SetCellValue(sheet, fmt.Sprintf("B%d", i+offset), utils.BoolToInt(hazard_size == "Small"))
			f.SetCellValue(sheet, fmt.Sprintf("C%d", i+offset), utils.BoolToInt(hazard_size == "Medium"))
			f.SetCellValue(sheet, fmt.Sprintf("D%d", i+offset), utils.BoolToInt(hazard_size == "Large"))
			f.SetCellValue(sheet, fmt.Sprintf("E%d", i+offset), item.CurbLength)
			f.SetCellValue(sheet, fmt.Sprintf("F%d", i+offset), item.Description)
			f.SetCellValue(sheet, fmt.Sprintf("G%d", i+offset), item.Width)
			f.SetCellValue(sheet, fmt.Sprintf("H%d", i+offset), item.Length)
			f.SetCellValue(sheet, fmt.Sprintf("J%d", i+offset), item.MeasuredHazardLength)
			f.SetCellValue(sheet, fmt.Sprintf("K%d", i+offset), item.InchFeet)
			f.SetCellValue(sheet, fmt.Sprintf("T%d", i+offset), item.ObjectId)

			if hazard_size == "Other" {
				var cell string

				cell = fmt.Sprintf("A%d", i+offset)
				HighlightCell(f, sheet, cell, true)

				cell = fmt.Sprintf("V%d", i+offset)
				f.SetCellValue(sheet, cell, "Other")
				HighlightCell(f, sheet, cell, true)
			}
		}
	}
}
