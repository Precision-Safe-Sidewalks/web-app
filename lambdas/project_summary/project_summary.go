package main

import (
	"context"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/xuri/excelize/v2"
)

const (
	TEMPLATE = "templates/PS Template - MACRO RB 8-29-23 Modified.xlsm"
)

const (
	WORKSHEET_SUMMARY = "SUMMARY"
)

const (
	S3_BUCKET = "precision-safe-sidewalks"
)

// Project Summary
type ProjectSummary struct {
	RequestId           uuid.UUID
	Filename            string
	Project             Project
	PricingSheet        PricingSheet
	SurveyInstructions  SurveyInstructions
	ProjectInstructions ProjectInstructions
	Measurements        []Measurement
	TechIndex           map[string]int
	TechInitials        map[string]string
}

// Construct a new Project Summary
func NewProjectSummary(requestId uuid.UUID) *ProjectSummary {
	return &ProjectSummary{
		RequestId:           requestId,
		Filename:            fmt.Sprintf("/tmp/%s.xlsm", requestId),
		Project:             Project{},
		PricingSheet:        PricingSheet{},
		SurveyInstructions:  SurveyInstructions{},
		ProjectInstructions: ProjectInstructions{},
		Measurements:        []Measurement{},
		TechIndex:           map[string]int{},
		TechInitials:        map[string]string{},
	}
}

// Fetch the data from the database
func (s *ProjectSummary) Fetch() {
	db, err := GetDatabase()

	if err != nil {
		panic(err)
	}

	defer db.Close(context.Background())

	s.FetchProject(db)
	s.FetchPricingSheet(db)
	s.FetchSurveyInstructions(db)
	s.FetchProjectInstructions(db)
	s.FetchMeasurements(db)
}

// Fetch the Project data
func (s *ProjectSummary) FetchProject(db *pgx.Conn) {
	query := `
		SELECT
			p.id,
			p.name,
			COALESCE(p.po_number, '') AS po_number,
			COALESCE(u.initials, '') AS bdm,
			t.name AS territory_name,
			c.name AS organization_name
		FROM repairs_project p
			JOIN repairs_projectsummaryrequest r ON p.id = r.project_id
			JOIN customers_customer c ON p.customer_id = c.id
			JOIN core_territory t ON p.territory_id = t.id
			LEFT JOIN accounts_user u ON p.business_development_manager_id = u.id
		WHERE r.request_id = $1
	`

	err := db.QueryRow(context.Background(), query, s.RequestId).Scan(
		&s.Project.Id,
		&s.Project.Name,
		&s.Project.PONumber,
		&s.Project.BDM,
		&s.Project.TerritoryName,
		&s.Project.OrganizationName,
	)

	if err != nil {
		panic(err)
	}
}

// Fetch the Pricing Sheet data
func (s *ProjectSummary) FetchPricingSheet(db *pgx.Conn) {
	query := `
		SELECT
			p.id,
			p.estimated_sidewalk_miles,
			c.name AS contact_name,
			COALESCE(c.title, '') AS contact_title,
			COALESCE(c.phone_number, '') AS phone_number,
			COALESCE(c.email, '') AS email,
			COALESCE(c.address, '') AS address
		FROM repairs_pricingsheet p
			JOIN repairs_pricingsheetcontact c ON p.id = c.pricing_sheet_id
		WHERE p.project_id = $1
	`

	err := db.QueryRow(context.Background(), query, s.Project.Id).Scan(
		&s.PricingSheet.Id,
		&s.PricingSheet.EstimatedSidewalkMiles,
		&s.PricingSheet.ContactName,
		&s.PricingSheet.ContactTitle,
		&s.PricingSheet.ContactPhoneNumber,
		&s.PricingSheet.ContactEmail,
		&s.PricingSheet.ContactAddress,
	)

	if err != nil {
		fmt.Sprintf("FetchPricingSheet error: %v", err)
		return
	}
}

// Fetch the Survey Instructions data
func (s *ProjectSummary) FetchSurveyInstructions(db *pgx.Conn) {
	query := `
		WITH measurements AS (
			SELECT
				MIN(project_id) AS project_id,
				TO_CHAR(MIN(measured_at), 'FMMM/FMDD/YYYY') AS survey_date
			FROM repairs_measurement
			WHERE project_id = $1
				AND stage = 'SURVEY'
		)
		SELECT
			i.id,
			COALESCE(u.initials, '') AS surveyor,
			COALESCE(m.survey_date, '') AS survey_date
		FROM repairs_instruction i
			LEFT JOIN accounts_user u ON i.surveyed_by_id = u.id
			LEFT JOIN measurements m ON i.project_id = m.project_id
		WHERE i.project_id = $1
			AND i.stage = 'SURVEY'
	`

	err := db.QueryRow(context.Background(), query, s.Project.Id).Scan(
		&s.SurveyInstructions.Id,
		&s.SurveyInstructions.Surveyor,
		&s.SurveyInstructions.SurveyDate,
	)

	if err != nil {
		fmt.Sprintf("FetchSurveyInstructions error: %v", err)
		return
	}
}

// Fetch the Project Instructions data
func (s *ProjectSummary) FetchProjectInstructions(db *pgx.Conn) {
	sizes := []string{"S", "M", "L"}

	for _, size := range sizes {
		var hazards int
		var inchFeet float64

		query := fmt.Sprintf(`
			SELECT
				COALESCE((hazards->'%s'->'count')::int, 0) AS hazards,
				COALESCE((hazards->'%s'->'inch_feet')::float, 0) AS inch_feet,
				i.linear_feet_curb
			FROM repairs_instruction i
			WHERE i.project_id = $1
				AND i.stage = 'PRODUCTION'
		`, size, size)

		err := db.QueryRow(context.Background(), query, s.Project.Id).Scan(
			&hazards,
			&inchFeet,
			&s.ProjectInstructions.CurbLength,
		)

		if err != nil {
			fmt.Sprintf("FetchProjectInstructions error: %v", err)
			return
		}

		s.ProjectInstructions.Hazards += hazards
		s.ProjectInstructions.InchFeet += inchFeet
	}
}

// Fetch the production Measurements data
func (s *ProjectSummary) FetchMeasurements(db *pgx.Conn) {
	query := `
		SELECT
			m.object_id,
			COALESCE(m.length, 0) AS length,
			COALESCE(m.width, 0) AS width,
			COALESCE(m.h1, 0) AS h1,
			COALESCE(m.h2, 0) AS h2,
			COALESCE(m.inch_feet, 0) AS inch_feet,
			COALESCE(m.curb_length, 0) AS curb_length,
			COALESCE(m.measured_hazard_length, 0) AS measured_hazard_length,
			COALESCE(m.geocoded_address, '') AS address,
			COALESCE(m.note, '') AS note,
			COALESCE(UPPER(SUBSTRING(m.tech, 1, 1)) || UPPER(SUBSTRING(m.tech, 3, 1)), '') AS tech,
			COALESCE(m.tech, '') AS tech_email,
			DATE(m.measured_at) AS work_date
		FROM repairs_measurement m
		WHERE m.project_id = $1
			AND m.stage = 'PRODUCTION'
		ORDER BY m.tech, m.object_id
	`

	rows, err := db.Query(context.Background(), query, s.Project.Id)

	if err != nil {
		fmt.Sprintf("FetchMeasurements error: %v", err)
		return
	}

	defer rows.Close()

	for rows.Next() {
		var m Measurement

		err := rows.Scan(
			&m.ObjectId,
			&m.Length,
			&m.Width,
			&m.H1,
			&m.H2,
			&m.InchFeet,
			&m.CurbLength,
			&m.MeasuredHazardLength,
			&m.Address,
			&m.Note,
			&m.Tech,
			&m.TechEmail,
			&m.WorkDate,
		)

		if err != nil {
			panic(err)
		}

		s.Measurements = append(s.Measurements, m)
	}

	// Index all the technicians by their email address to the order they
	// appear in the measurements
	for _, item := range s.Measurements {
		if _, ok := s.TechIndex[item.TechEmail]; !ok {
			s.TechIndex[item.TechEmail] = len(s.TechIndex)
			s.TechInitials[item.TechEmail] = item.Tech
		}
	}
}

// Return the total hazards count
func (s *ProjectSummary) TotalHazards() int {
	return s.ProjectInstructions.Hazards
}

// Return the total inch feet
func (s *ProjectSummary) TotalInchFeet() float64 {
	return s.ProjectInstructions.InchFeet
}

// Return the total linear feet curbs
func (s *ProjectSummary) TotalCurbLength() float64 {
	return s.ProjectInstructions.CurbLength
}

// Generate the Project Summary Excel file
func (s *ProjectSummary) Generate() {
	fmt.Printf("Generating project summary for request: %s\n", s.RequestId)

	workbook, err := excelize.OpenFile(TEMPLATE)

	if err != nil {
		panic(err)
	}

	defer workbook.Close()

	workbook.UpdateLinkedValue()
	s.Fetch()
	s.UpdateSummary(workbook)
	s.UpdateProductionData(workbook)
	workbook.UpdateLinkedValue()

	if err := workbook.SaveAs(s.Filename); err != nil {
		panic(err)
	}
}

// Update the "SUMMARY" worksheet
func (s *ProjectSummary) UpdateSummary(f *excelize.File) {
	sheet := WORKSHEET_SUMMARY

	year, month, day := time.Now().Date()
	reportDate := time.Date(year, month, day, 0, 0, 0, 0, time.UTC)

	f.SetCellValue(sheet, "E1", reportDate)
	f.SetCellValue(sheet, "D3", s.Project.Name)
	f.SetCellValue(sheet, "C8", s.Project.PONumber)
	f.SetCellValue(sheet, "P2", s.Project.BDM)
	f.SetCellValue(sheet, "P4", s.SurveyInstructions.Surveyor)
	f.SetCellValue(sheet, "Q2", s.Project.TerritoryName)
	f.SetCellValue(sheet, "Q4", s.SurveyInstructions.SurveyDate)
	f.SetCellValue(sheet, "R6", s.TotalHazards())
	f.SetCellValue(sheet, "R10", s.TotalInchFeet())
	f.SetCellValue(sheet, "R17", s.TotalCurbLength())
	f.SetCellValue(sheet, "AO39", s.Project.OrganizationName)
	f.SetCellValue(sheet, "AQ39", s.PricingSheet.ContactAddress)
	f.SetCellValue(sheet, "AS39", s.PricingSheet.ContactName)
	f.SetCellValue(sheet, "AY39", s.PricingSheet.ContactTitle)
	f.SetCellValue(sheet, "BC39", s.PricingSheet.ContactPhoneNumber)
	f.SetCellValue(sheet, "BG39", s.PricingSheet.ContactEmail)
	f.SetCellValue(sheet, "BN39", s.PricingSheet.EstimatedSidewalkMiles)

	// Set the tech initials in columns P - AF
	for techEmail, techId := range s.TechIndex {
		cell, _ := excelize.CoordinatesToCellName(techId+14, 43)
		f.SetCellValue(sheet, cell, s.TechInitials[techEmail])
	}
}

// Update the production survey data worksheets
func (s *ProjectSummary) UpdateProductionData(f *excelize.File) {
	// Group all of the production data measurements by the work date. The
	// measurements should be sorted by the the surveyor already.
	groups := map[time.Time][]Measurement{}
	workDates := []time.Time{}

	for _, item := range s.Measurements {
		if items, ok := groups[item.WorkDate]; ok {
			groups[item.WorkDate] = append(items, item)
		} else {
			groups[item.WorkDate] = []Measurement{item}
			workDates = append(workDates, item.WorkDate)
		}
	}

	// For each work date, set the sheet name and insert the data
	// into the table
	sort.Slice(workDates, func(i, j int) bool { return workDates[i].Before(workDates[j]) })

	for i, workDate := range workDates {
		sheet := workDate.Format("01-02-2006")
		sheetData := groups[workDate]

		s.UpdateSheetName(f, strconv.Itoa(i+1), sheet)
		s.UpdateSummaryCompletedCurbs(f, sheet, i)
		s.UpdateSummaryCompletedSidewalks(f, sheet, i)
		f.SetCellValue(sheet, "E11", workDate)

		// Set the tech initials in columns P - AF
		for techEmail, techId := range s.TechIndex {
			cell, _ := excelize.CoordinatesToCellName(techId+16, 21)
			f.SetCellValue(sheet, cell, s.TechInitials[techEmail])
		}

		for j, item := range sheetData {
			rowId := 22 + j
			currentTechId := s.TechIndex[item.TechEmail]

			f.SetCellValue(sheet, fmt.Sprintf("A%d", rowId), item.Width)
			f.SetCellValue(sheet, fmt.Sprintf("B%d", rowId), item.Length)
			f.SetCellValue(sheet, fmt.Sprintf("D%d", rowId), item.H1)
			f.SetCellValue(sheet, fmt.Sprintf("E%d", rowId), item.H2)
			f.SetCellValue(sheet, fmt.Sprintf("F%d", rowId), item.MeasuredHazardLength)
			f.SetCellValue(sheet, fmt.Sprintf("G%d", rowId), item.Address)
			f.SetCellValue(sheet, fmt.Sprintf("H%d", rowId), item.Note)
			f.SetCellValue(sheet, fmt.Sprintf("M%d", rowId), item.Tech)
			f.SetCellValue(sheet, fmt.Sprintf("N%d", rowId), item.ObjectId)

			for techId := 0; techId < 17; techId++ {
				cell, _ := excelize.CoordinatesToCellName(techId+16, rowId)
				enabled := currentTechId == techId
				formula := fmt.Sprintf(`=IF(%v, J%d, 0.)`, enabled, rowId)

				f.SetCellDefault(sheet, cell, "")
				f.SetCellFormula(sheet, cell, formula)
			}
		}

		fmt.Printf("Completed worksheet %s\n", sheet)
	}
}

// Update the sheet name and references
func (s *ProjectSummary) UpdateSheetName(f *excelize.File, oldName string, newName string) {
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
}

// Update the formula references on the SUMMARY worksheet (completed curbs)
func (s *ProjectSummary) UpdateSummaryCompletedCurbs(f *excelize.File, sheet string, sheetId int) {
	rowId := 35 - sheetId

	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("E%d", rowId), fmt.Sprintf("='%s'!O8", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("F%d", rowId), fmt.Sprintf("='%s'!P8", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("G%d", rowId), fmt.Sprintf("='%s'!Q8", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("H%d", rowId), fmt.Sprintf("='%s'!R8", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("I%d", rowId), fmt.Sprintf("='%s'!S8", sheet))
}

// Update the formula references on the SUMMARY worksheet (completed sidewalks)
func (s *ProjectSummary) UpdateSummaryCompletedSidewalks(f *excelize.File, sheet string, sheetId int) {
	rowId := 59 - sheetId

	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("A%d", rowId), fmt.Sprintf("='%s'!O5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("B%d", rowId), fmt.Sprintf("='%s'!P5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("C%d", rowId), fmt.Sprintf("='%s'!Q5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("D%d", rowId), fmt.Sprintf("='%s'!R5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("E%d", rowId), fmt.Sprintf("='%s'!S5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("F%d", rowId), fmt.Sprintf("='%s'!T5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("G%d", rowId), fmt.Sprintf("='%s'!U5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("H%d", rowId), fmt.Sprintf("='%s'!V5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("I%d", rowId), fmt.Sprintf("='%s'!W5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("J%d", rowId), fmt.Sprintf("='%s'!X5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("K%d", rowId), fmt.Sprintf("='%s'!Y5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("L%d", rowId), fmt.Sprintf("='%s'!Z5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("M%d", rowId), fmt.Sprintf("='%s'!AA5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("N%d", rowId), fmt.Sprintf("='%s'!AB5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("O%d", rowId), fmt.Sprintf("='%s'!AC5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("P%d", rowId), fmt.Sprintf("='%s'!AD5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("Q%d", rowId), fmt.Sprintf("='%s'!AE5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("R%d", rowId), fmt.Sprintf("='%s'!AF5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("S%d", rowId), fmt.Sprintf("='%s'!AG5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("T%d", rowId), fmt.Sprintf("='%s'!AH5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("U%d", rowId), fmt.Sprintf("='%s'!AI5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("V%d", rowId), fmt.Sprintf("='%s'!AJ5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("W%d", rowId), fmt.Sprintf("='%s'!AK5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("X%d", rowId), fmt.Sprintf("='%s'!AL5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("Y%d", rowId), fmt.Sprintf("='%s'!AM5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("Z%d", rowId), fmt.Sprintf("='%s'!AN5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AA%d", rowId), fmt.Sprintf("='%s'!AO5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AB%d", rowId), fmt.Sprintf("='%s'!AP5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AC%d", rowId), fmt.Sprintf("='%s'!AQ5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AD%d", rowId), fmt.Sprintf("='%s'!AR5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AE%d", rowId), fmt.Sprintf("='%s'!AS5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AF%d", rowId), fmt.Sprintf("='%s'!AT5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AG%d", rowId), fmt.Sprintf("='%s'!AU5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AH%d", rowId), fmt.Sprintf("='%s'!AV5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AI%d", rowId), fmt.Sprintf("='%s'!AW5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AJ%d", rowId), fmt.Sprintf("='%s'!AX5", sheet))
	f.SetCellFormula(WORKSHEET_SUMMARY, fmt.Sprintf("AK%d", rowId), fmt.Sprintf("='%s'!AY5", sheet))
}

// Return the S3 key
func (s *ProjectSummary) Key() string {
	return fmt.Sprintf("project_summaries/%s/%s - Project Summary.xlsm", s.RequestId, s.Project.Name)
}

// Upload the Project Summary Excel file to S3
func (s *ProjectSummary) Upload() {
	f, err := os.Open(s.Filename)

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

	params := s3manager.UploadInput{
		Bucket: aws.String(S3_BUCKET),
		Key:    aws.String(s.Key()),
		Body:   f,
	}

	if _, err := s3manager.NewUploader(sess).Upload(&params); err != nil {
		panic(err)
	}

	os.Remove(s.Filename)
}

// Mark the Project Summary request as complete
func (s *ProjectSummary) Complete() {
	query := `
		UPDATE repairs_projectsummaryrequest SET
			s3_bucket = $1,
			s3_key = $2,
			updated_at = CURRENT_TIMESTAMP
		WHERE request_id = $3
	`

	db, err := GetDatabase()

	if err != nil {
		panic(err)
	}

	defer db.Close(context.Background())

	db.Exec(context.Background(), query, S3_BUCKET, s.Key(), s.RequestId)
}

// Get the database connection
func GetDatabase() (*pgx.Conn, error) {
	host := os.Getenv("DB_HOST")
	user := os.Getenv("DB_USER")
	pass := os.Getenv("DB_PASSWORD")
	name := os.Getenv("DB_NAME")

	uri := fmt.Sprintf("postgres://%s:%s@%s:5432/%s", user, pass, host, name)
	ctx := context.Background()

	return pgx.Connect(ctx, uri)
}

// Project
type Project struct {
	Id               int
	Name             string
	PONumber         string
	BDM              string
	TerritoryName    string
	OrganizationName string
}

// Pricing Sheet
type PricingSheet struct {
	Id                     int
	EstimatedSidewalkMiles int
	ContactName            string
	ContactTitle           string
	ContactPhoneNumber     string
	ContactEmail           string
	ContactAddress         string
}

// Survey Instructions
type SurveyInstructions struct {
	Id         int
	Surveyor   string
	SurveyDate string
}

// Project Instructions
type ProjectInstructions struct {
	Hazards    int
	InchFeet   float64
	CurbLength float64
}

// Measurement
type Measurement struct {
	ObjectId             int
	Length               float64
	Width                float64
	H1                   float64
	H2                   float64
	InchFeet             float64
	CurbLength           float64
	MeasuredHazardLength float64
	Address              string
	Note                 string
	Tech                 string
	TechEmail            string
	WorkDate             time.Time
}
