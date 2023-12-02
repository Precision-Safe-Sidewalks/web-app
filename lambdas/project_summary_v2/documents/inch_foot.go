package documents

import (
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/xuri/excelize/v2"

	"app.bluezoneautomation.com/lambda-project-summary/v2/schema"
)

const (
	TEMPLATE_INCH_FOOT = "templates/PS 30 tabs Template - MACRO RB 11-9-2023 Modified.xlsm"
)

type InchFootProjectSummary struct {
	Data schema.ProjectSummaryData
}

// Construct an inch foot project summary generator
func NewInchFootProjectSummary(data schema.ProjectSummaryData) InchFootProjectSummary {
	return InchFootProjectSummary{Data: data}
}

// Generate the inch foot project summary document
func (s InchFootProjectSummary) Generate() (string, error) {
	workbook, err := excelize.OpenFile(TEMPLATE_INCH_FOOT)

	if err != nil {
		return "", err
	}

	defer workbook.Close()

	s.UpdateSummary(workbook)
	s.UpdateSurveyData(workbook)

	workbook.UpdateLinkedValue()
	workbook.SetActiveSheet(1)

	filename := s.GenerateFilename()
	err = workbook.SaveAs(filename)

	return filename, err
}

// Generate a unique filename
func (s InchFootProjectSummary) GenerateFilename() string {
	return fmt.Sprintf("/tmp/%s.xlsm", uuid.New().String())
}

// Update the "SUMMARY" worksheet
func (s InchFootProjectSummary) UpdateSummary(f *excelize.File) {
	sheet := "SUMMARY"

	year, month, day := time.Now().Date()
	report_date := time.Date(year, month, day, 0, 0, 0, 0, time.UTC)

	f.SetCellValue(sheet, "E1", report_date)
	f.SetCellValue(sheet, "D3", s.Data.Name)
	f.SetCellValue(sheet, "C8", SafeString(s.Data.PONumber))
	f.SetCellValue(sheet, "P2", s.Data.BDM.Initials)
	f.SetCellValue(sheet, "Q2", s.Data.Territory.Name)
	f.SetCellValue(sheet, "Q4", SafeString(s.Data.SurveyDate))
	f.SetCellValue(sheet, "R6", s.Data.Hazards.Count)
	f.SetCellValue(sheet, "R10", s.Data.Hazards.InchFeet)
	f.SetCellValue(sheet, "R17", s.Data.Hazards.LinearFeetCurb)
	f.SetCellValue(sheet, "A039", s.Data.Customer.Name)
	f.SetCellValue(sheet, "BN39", s.Data.Pricing.EstimatedSidewalkMiles)

	if s.Data.Surveyor != nil {
		f.SetCellValue(sheet, "P4", s.Data.Surveyor.Initials)
	}

	if s.Data.Contact != nil {
		f.SetCellValue(sheet, "AQ39", SafeString(s.Data.Contact.Address))
		f.SetCellValue(sheet, "AS39", s.Data.Contact.Name)
		f.SetCellValue(sheet, "AY39", SafeString(s.Data.Contact.Title))
		f.SetCellValue(sheet, "BC39", SafeString(s.Data.Contact.PhoneNumber))
		f.SetCellValue(sheet, "BG39", SafeString(s.Data.Contact.Email))
	}

	// Set the tech initials in columns P - AF
	for index, tech := range s.Data.GetTechs() {
		initials := s.Data.GetTechInitials(tech)
		cell, _ := excelize.CoordinatesToCellName(index+14, 43)
		f.SetCellValue(sheet, cell, initials)
	}
}

// Update the survey data worksheets
func (s InchFootProjectSummary) UpdateSurveyData(f *excelize.File) {
}
