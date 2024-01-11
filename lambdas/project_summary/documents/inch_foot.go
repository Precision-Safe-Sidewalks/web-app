package documents

import (
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/xuri/excelize/v2"

	"app.bluezoneautomation.com/lambda-project-summary/v2/schema"
)

const (
	TEMPLATE_INCH_FOOT = "templates/PS 30 tabs Template - MACRO RB 11-9-2023.xlsm"
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
	reportDate := time.Date(year, month, day, 0, 0, 0, 0, time.UTC)

	f.SetCellValue(sheet, "E1", reportDate)
	f.SetCellValue(sheet, "D3", s.Data.Name)
	f.SetCellValue(sheet, "C8", SafeString(s.Data.PONumber))
	f.SetCellValue(sheet, "P2", s.Data.BDM.Initials)
	f.SetCellValue(sheet, "Q2", s.Data.Territory.Name)
	f.SetCellValue(sheet, "Q4", SafeString(s.Data.SurveyDate))
	f.SetCellValue(sheet, "R6", s.Data.Hazards.Count)
	f.SetCellValue(sheet, "R10", s.Data.Hazards.InchFeet)
	f.SetCellValue(sheet, "R17", s.Data.Hazards.LinearFeetCurb)
	f.SetCellValue(sheet, "BE89", s.Data.Customer.Name)
	f.SetCellValue(sheet, "CD89", s.Data.Pricing.EstimatedSidewalkMiles)

	if s.Data.Surveyor != nil {
		f.SetCellValue(sheet, "P4", s.Data.Surveyor.Initials)
	}

	// Set the PPR macro information
	if s.Data.Contact != nil {
		f.SetCellValue(sheet, "BG89", SafeString(s.Data.Contact.Address))
		f.SetCellValue(sheet, "BI89", s.Data.Contact.Name)
		f.SetCellValue(sheet, "BO89", SafeString(s.Data.Contact.Title))
		f.SetCellValue(sheet, "BS89", SafeString(s.Data.Contact.PhoneNumber))
		f.SetCellValue(sheet, "BW89", SafeString(s.Data.Contact.Email))
	}

	// Set the tech initials in columns P - AF
	for index, tech := range s.Data.GetTechs() {
		initials := s.Data.GetTechInitials(tech)
		cell, _ := excelize.CoordinatesToCellName(index+14, 57)
		f.SetCellValue(sheet, cell, initials)
	}
}

// Update the survey data worksheets
func (s InchFootProjectSummary) UpdateSurveyData(f *excelize.File) {
	techs := s.Data.GetTechs()

	for sheetId, group := range s.Data.Measurements {
		oldSheet := strconv.Itoa(sheetId + 1)

		// Convert the ISO 8601 date to the preferred MM-DD-YYYY format
		workDate, _ := time.Parse(time.DateOnly, group.Name)
		sheet := workDate.Format("01-02-2006")

		s.UpdateSheetName(f, oldSheet, sheet)
		f.SetCellValue(sheet, "E11", DateStringToTime(group.Name))

		// For each tech, set the column header
		for j, tech := range techs {
			cell, _ := excelize.CoordinatesToCellName(j+16, 21)
			initials := s.Data.GetTechInitials(tech)
			f.SetCellValue(sheet, cell, initials)
		}

		for i, item := range group.Measurements {
			rowId := i + 22

			f.SetCellValue(sheet, fmt.Sprintf("A%d", rowId), item.Width)
			f.SetCellValue(sheet, fmt.Sprintf("B%d", rowId), item.Length)
			f.SetCellValue(sheet, fmt.Sprintf("D%d", rowId), item.H1)
			f.SetCellValue(sheet, fmt.Sprintf("E%d", rowId), item.H2)
			f.SetCellValue(sheet, fmt.Sprintf("F%d", rowId), item.MeasuredHazardLength)
			f.SetCellValue(sheet, fmt.Sprintf("G%d", rowId), SafeString(item.Address))
			f.SetCellValue(sheet, fmt.Sprintf("H%d", rowId), item.Description)
			f.SetCellValue(sheet, fmt.Sprintf("M%d", rowId), s.Data.GetTechInitials(item.Tech))
			f.SetCellValue(sheet, fmt.Sprintf("N%d", rowId), item.ObjectId)

			// Apply the conditional highlighting
			if color := item.GetHighlightColor(); color != "" {
				HighlightCell(f, sheet, fmt.Sprintf("E%d", rowId), color)
				HighlightCell(f, sheet, fmt.Sprintf("N%d", rowId), color)
			}

			// Update the formulas for the tech totals
			for j, tech := range techs {
				cell, _ := excelize.CoordinatesToCellName(j+16, rowId)
				enabled := tech == item.Tech
				formula := fmt.Sprintf("=IF(%v, J%d, 0.)", enabled, rowId)

				f.SetCellDefault(sheet, cell, "")
				f.SetCellFormula(sheet, cell, formula)
			}
		}
	}
}

// Update the sheet name
func (s InchFootProjectSummary) UpdateSheetName(f *excelize.File, oldName, newName string) {
	f.SetSheetName(oldName, newName)

	// Check for any defined names
	for _, definedName := range f.GetDefinedName() {
		if definedName.Scope == newName {
			f.DeleteDefinedName(&definedName)

			oldPattern := fmt.Sprintf("'%s'", oldName)
			newPattern := fmt.Sprintf("'%s'", newName)
			refersTo := strings.Replace(definedName.RefersTo, oldPattern, newPattern, 1)

			definedName.RefersTo = refersTo
			f.SetDefinedName(&definedName)
		}
	}

	// Update the formula references on the SUMMARY sheet
	s.UpdateCompletedCurb(f, newName)
	s.UpdateCompletedSidewalk(f, newName)
}

// Update the completed curbs references
func (s InchFootProjectSummary) UpdateCompletedCurb(f *excelize.File, sheetName string) {
	sheet := "SUMMARY"
	sheetId, _ := f.GetSheetIndex(sheetName)
	rowId := 50 - sheetId // first survey sheet has index = 1

	f.SetCellFormula(sheet, fmt.Sprintf("E%d", rowId), fmt.Sprintf("='%s'!O8", sheetName))
	f.SetCellFormula(sheet, fmt.Sprintf("F%d", rowId), fmt.Sprintf("='%s'!P8", sheetName))
	f.SetCellFormula(sheet, fmt.Sprintf("G%d", rowId), fmt.Sprintf("='%s'!Q8", sheetName))
	f.SetCellFormula(sheet, fmt.Sprintf("H%d", rowId), fmt.Sprintf("='%s'!R8", sheetName))
	f.SetCellFormula(sheet, fmt.Sprintf("I%d", rowId), fmt.Sprintf("='%s'!S8", sheetName))
}

// Update the completed sidewalks references
func (s InchFootProjectSummary) UpdateCompletedSidewalk(f *excelize.File, sheetName string) {
	sheet := "SUMMARY"
	sheetId, _ := f.GetSheetIndex(sheetName)
	rowId := 88 - sheetId // first survey sheet has index = 1

	// Map columns A:AK to O:AY
	for i := 1; i < 38; i++ {
		cell, _ := excelize.CoordinatesToCellName(i, rowId)
		refCell, _ := excelize.CoordinatesToCellName(i+14, 5)
		formula := fmt.Sprintf("='%s'!%s", sheetName, refCell)
		f.SetCellFormula(sheet, cell, formula)
	}
}
