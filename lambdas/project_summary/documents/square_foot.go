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
	TEMPLATE_SQUARE_FOOT = "templates/TEMPLATE SQFT PS Clin 123 11-28-23.xlsx"
)

type SquareFootProjectSummary struct {
	Data schema.ProjectSummaryData
}

// Construct an inch foot project summary generator
func NewSquareFootProjectSummary(data schema.ProjectSummaryData) SquareFootProjectSummary {
	return SquareFootProjectSummary{Data: data}
}

// Generate the inch foot project summary document
func (s SquareFootProjectSummary) Generate() (string, error) {
	workbook, err := excelize.OpenFile(TEMPLATE_SQUARE_FOOT)

	if err != nil {
		return "", err
	}

	defer workbook.Close()

	s.UpdateSummary(workbook)
	s.UpdateSurveyData(workbook)

	workbook.UpdateLinkedValue()
	workbook.SetActiveSheet(0)

	filename := s.GenerateFilename()
	err = workbook.SaveAs(filename)

	return filename, err
}

// Generate a unique filename
func (s SquareFootProjectSummary) GenerateFilename() string {
	return fmt.Sprintf("/tmp/%s.xlsx", uuid.New().String())
}

// Update the "SUMMARY" worksheet
func (s SquareFootProjectSummary) UpdateSummary(f *excelize.File) {
	sheet := "SUMMARY"

	year, month, day := time.Now().Date()
	reportDate := time.Date(year, month, day, 0, 0, 0, 0, time.UTC)

	f.SetCellValue(sheet, "A1", s.Data.Customer.Name)
	f.SetCellValue(sheet, "E1", reportDate)
	f.SetCellValue(sheet, "D3", s.Data.Name)
	f.SetCellValue(sheet, "C8", SafeString(s.Data.PONumber))
	f.SetCellValue(sheet, "K4", s.Data.BDM.Initials)
	f.SetCellValue(sheet, "L4", s.Data.Territory.Name)
	f.SetCellValue(sheet, "L6", SafeString(s.Data.SurveyDate))
	f.SetCellValue(sheet, "O6", s.Data.Hazards.Count)
	f.SetCellValue(sheet, "O9", s.Data.Hazards.SquareFeet)

	if s.Data.Surveyor != nil {
		f.SetCellValue(sheet, "K6", s.Data.Surveyor.Initials)
	}

	// Set the CLINs
	for index, clin := range s.Data.Pricing.CLINS {
		f.SetCellValue(sheet, fmt.Sprintf("B%d", index+13), clin.Name)
		f.SetCellValue(sheet, fmt.Sprintf("D%d", index+13), clin.Value)
	}

	// Set the tech initials in columns P - AF
	for index, tech := range s.Data.GetTechs() {
		initials := s.Data.GetTechInitials(tech)
		cell, _ := excelize.CoordinatesToCellName(index+15, 22)
		f.SetCellValue(sheet, cell, initials)
	}
}

// Update the survey data worksheets
func (s SquareFootProjectSummary) UpdateSurveyData(f *excelize.File) {
	techs := s.Data.GetTechs()

	for sheetId, group := range s.Data.Measurements {
		oldSheet := strconv.Itoa(sheetId + 1)

		// Convert the ISO 8601 date format to the preferred MM-DD-YYY
		workDate, _ := time.Parse(time.DateOnly, group.Name)
		sheet := workDate.Format("01-02-2006")

		s.UpdateSheetName(f, oldSheet, sheet)
		f.SetCellValue(sheet, "E12", DateStringToTime(group.Name))

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
func (s SquareFootProjectSummary) UpdateSheetName(f *excelize.File, oldName, newName string) {
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
	s.UpdateCompletedSidewalk(f, newName)
}

// Update the completed sidewalks references
func (s SquareFootProjectSummary) UpdateCompletedSidewalk(f *excelize.File, sheetName string) {
	sheet := "SUMMARY"
	sheetId, _ := f.GetSheetIndex(sheetName)
	rowId := 53 - sheetId // first survey sheet has index = 1

	// Map columns A:Y to O:AM
	for i := 1; i < 26; i++ {
		cell, _ := excelize.CoordinatesToCellName(i, rowId)
		refCell, _ := excelize.CoordinatesToCellName(i+14, 5)
		formula := fmt.Sprintf("='%s'!%s", sheetName, refCell)

		f.SetCellDefault(sheet, cell, "")
		f.SetCellFormula(sheet, cell, formula)
	}

	// Map columns Z:AD to AO:AS
	for i := 26; i < 31; i++ {
		cell, _ := excelize.CoordinatesToCellName(i, rowId)
		refCell, _ := excelize.CoordinatesToCellName(i+15, 5)
		formula := fmt.Sprintf("='%s'!%s", sheetName, refCell)

		f.SetCellDefault(sheet, cell, "")
		f.SetCellFormula(sheet, cell, formula)
	}
}
