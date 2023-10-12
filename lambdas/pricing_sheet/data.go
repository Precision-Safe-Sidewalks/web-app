package main

import (
	"context"
	"fmt"
	"os"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
)

// Get the database connection
func GetDatabase() *pgx.Conn {
	host := os.Getenv("DB_HOST")
	user := os.Getenv("DB_USER")
	pass := os.Getenv("DB_PASSWORD")
	name := os.Getenv("DB_NAME")

	uri := fmt.Sprintf("postgres://%s:%s@%s:5432/%s", user, pass, host, name)
	ctx := context.Background()

	db, err := pgx.Connect(ctx, uri)
	if err != nil {
		panic(err)
	}

	return db
}

// Pricing sheet data
type PricingSheetData struct {
	RequestId              uuid.UUID
	ProjectId              int
	ProjectName            string
	PricingModel           int
	OrganizationName       string
	BDM                    string
	Surveyor               string
	ContactName            string
	ContactTitle           string
	ContactEmail           string
	ContactPhoneNumber     string
	ContactAddress         string
	EstimatedSidewalkMiles int
	SurveyorSpeed          int
	SurveyHazards          int
	HazardDensity          int
	PanelSize              int
	DistanceFromSurveyor   int
	DistanceFromOps        int
	CommissionRate         float64
	BaseRate               float64
	TerritoryRate          float64
	NumberOfTechnicians    int
	SurveyData             []SurveyRecord
}

// Construct a new Pricing Sheet Data
func NewPricingSheetData(requestId uuid.UUID) *PricingSheetData {
	return &PricingSheetData{RequestId: requestId}
}

// Fetch the data for the Pricing Sheet
func (d *PricingSheetData) Fetch() {
	db := GetDatabase()
	defer db.Close(context.Background())

	d.FetchProject(db)
	d.FetchContact(db)
	d.FetchSurveyData(db)
}

// Fetch the project data
func (d *PricingSheetData) FetchProject(db *pgx.Conn) {
	query := `
		SELECT
			p.id,
			p.name,
			p.pricing_model,
			o.name AS organization_name,
			COALESCE(up.initials, '') AS bdm,
			COALESCE(ui.initials, '') AS surveyor,
			ps.estimated_sidewalk_miles,
			ps.surveyor_speed,
			ps.survey_hazards,
			ps.hazard_density,
			ps.panel_size,
			ps.distance_from_surveyor,
			ps.distance_from_ops,
			ps.commission_rate,
			ps.base_rate,
			ps.number_of_technicians,
			COALESCE(t.royalty_rate, 0) AS royalty_rate
		FROM repairs_project p
			JOIN repairs_pricingsheet ps ON p.id = ps.project_id
			JOIN repairs_pricingsheetrequest pr ON ps.id = pr.pricing_sheet_id
			JOIN repairs_instruction i ON p.id = i.project_id AND i.stage = 'SURVEY'
			JOIN customers_customer o ON p.customer_id = o.id
			JOIN core_territory t ON p.territory_id = t.id
			LEFT JOIN accounts_user up ON p.business_development_manager_id = up.id
			LEFT JOIN accounts_user ui ON i.surveyed_by_id = ui.id
		WHERE pr.request_id = $1
	`

	ctx := context.Background()
	err := db.QueryRow(ctx, query, d.RequestId).Scan(
		&d.ProjectId,
		&d.ProjectName,
		&d.PricingModel,
		&d.OrganizationName,
		&d.BDM,
		&d.Surveyor,
		&d.EstimatedSidewalkMiles,
		&d.SurveyorSpeed,
		&d.SurveyHazards,
		&d.HazardDensity,
		&d.PanelSize,
		&d.DistanceFromSurveyor,
		&d.DistanceFromOps,
		&d.CommissionRate,
		&d.BaseRate,
		&d.NumberOfTechnicians,
		&d.TerritoryRate,
	)

	if err != nil {
		panic(err)
	}
}

// Fetch the contacts
func (d *PricingSheetData) FetchContact(db *pgx.Conn) {
	query := `
		SELECT
			c.name,
			COALESCE(c.title, ''),
			COALESCE(c.email, ''),
			COALESCE(c.phone_number, ''),
			COALESCE(c.address, '')
		FROM repairs_pricingsheetcontact c
			JOIN repairs_pricingsheet ps ON c.pricing_sheet_id = ps.id
		WHERE ps.project_id = $1
	`

	ctx := context.Background()
	err := db.QueryRow(ctx, query, d.ProjectId).Scan(
		&d.ContactName,
		&d.ContactTitle,
		&d.ContactEmail,
		&d.ContactPhoneNumber,
		&d.ContactAddress,
	)

	if err != nil {
		panic(err)
	}
}

// Fetch the survey data
func (d *PricingSheetData) FetchSurveyData(db *pgx.Conn) {
	query := `
		SELECT
			m.object_id,
			COALESCE(m.survey_group, ''),
			COALESCE(m.size, '') AS size,
			COALESCE(m.curb_length, 0) AS curb_length,
			COALESCE(m.geocoded_address, '') AS geocoded_address,
			COALESCE(m.length, 0) AS length,
			COALESCE(m.width, 0) AS width,
			COALESCE(m.measured_hazard_length, 0) AS measured_hazard_length,
			COALESCE(m.inch_feet, 0) AS inch_feet
		FROM repairs_measurement m
		WHERE m.project_id = $1
			AND m.stage = 'SURVEY'
		ORDER BY m.survey_group, m.object_id
	`

	ctx := context.Background()
	rows, err := db.Query(ctx, query, d.ProjectId)

	if err != nil {
		panic(err)
	}

	defer rows.Close()

	for rows.Next() {
		var r SurveyRecord

		err = rows.Scan(
			&r.ObjectId,
			&r.SurveyGroup,
			&r.Size,
			&r.CurbLength,
			&r.Address,
			&r.Length,
			&r.Width,
			&r.MeasuredHazardLength,
			&r.InchFeet,
		)

		if err != nil {
			panic(err)
		}

		d.SurveyData = append(d.SurveyData, r)
	}
}

// SurveyRecord data
type SurveyRecord struct {
	ObjectId             int
	SurveyGroup          string
	Size                 string
	CurbLength           float64
	Address              string
	Length               float64
	Width                float64
	MeasuredHazardLength float64
	InchFeet             float64
}
