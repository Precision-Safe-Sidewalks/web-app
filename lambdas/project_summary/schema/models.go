package schema

import (
	"fmt"
	"strings"
)

type ProjectSummaryData struct {
	Id           int                `json:"id"`
	Name         string             `json:"name"`
	PONumber     *string            `json:"po_number"`
	Customer     Customer           `json:"customer"`
	Territory    Territory          `json:"territory"`
	BDM          User               `json:"business_development_manager"`
	Surveyor     *User              `json:"surveyor"`
	SurveyDate   *string            `json:"survey_date"`
	Contact      *Contact           `json:"contact"`
	Pricing      Pricing            `json:"pricing"`
	PricingModel string             `json:"pricing_model"`
	Hazards      Hazards            `json:"hazards"`
	Measurements []MeasurementGroup `json:"measurements"`
}

// Return the ordered list of techs in the measurements
func (p ProjectSummaryData) GetTechs() []string {
	index := p.GetTechIndex()
	techs := make([]string, len(index))

	for tech, i := range index {
		techs[i] = tech
	}

	return techs
}

// Return the index of techs
func (p ProjectSummaryData) GetTechIndex() map[string]int {
	index := map[string]int{}

	for _, group := range p.Measurements {
		for _, item := range group.Measurements {
			if _, ok := index[item.Tech]; !ok {
				index[item.Tech] = len(index)
			}
		}
	}

	return index
}

// Return the initials from the tech's email
func (p ProjectSummaryData) GetTechInitials(tech string) string {
	initials := fmt.Sprintf("%s%s", string(tech[0]), string(tech[2]))
	return strings.ToUpper(initials)
}

type User struct {
	Id        int     `json:"id"`
	Email     string  `json:"email"`
	FullName  string  `json:"full_name"`
	Initials  string  `json:"initials"`
	WorkPhone *string `json:"work_phone"`
	CellPhone *string `json:"cell_phone"`
}

type Customer struct {
	Id      int     `json:"id"`
	Name    string  `json:"name"`
	Address *string `json:"address"`
	City    *string `json:"city"`
	State   *string `json:"state"`
}

type Territory struct {
	Id          int     `json:"id"`
	Name        string  `json:"name"`
	Label       string  `json:"label"`
	RoyaltyRate float64 `json:"royalty_rate"`
}

type Hazards struct {
	Count          int     `json:"count"`
	InchFeet       float64 `json:"inch_feet"`
	SquareFeet     float64 `json:"square_feet"`
	LinearFeetCurb float64 `json:"linear_feet_curb"`
}

type Pricing struct {
	Id                     int     `json:"id"`
	EstimatedSidewalkMiles float64 `json:"estimated_sidewalk_miles"`
	SurveyorSpeed          float64 `json:"surveyor_speed"`
	SurveyHazards          int     `json:"survey_hazards"`
	HazardDensity          int     `json:"hazard_density"`
	PanelSize              int     `json:"panel_size"`
	DistanceFromSurveyor   float64 `json:"distance_from_surveyor"`
	DistanceFromOps        float64 `json:"distance_from_ops"`
	CommissionRate         float64 `json:"commission_rate"`
	BaseRate               float64 `json:"base_rate"`
	NumberOfTechnicians    int     `json:"number_of_technicians"`
	CLINS                  []CLIN  `json:"clins"`
}

type CLIN struct {
	Name  string  `json:"name"`
	Value float64 `json:"value"`
}

type Contact struct {
	Name        string  `json:"name"`
	Title       *string `json:"title"`
	Street      *string `json:"street"`
	City        *string `json:"city"`
	State       *string `json:"state"`
	ZipCode     *string `json:"zip_code"`
	Email       *string `json:"email"`
	PhoneNumber *string `json:"phone_number"`
	Address     *string `json:"address"`
}

type MeasurementGroup struct {
	Name         string        `json:"name"`
	Measurements []Measurement `json:"data"`
}

type Measurement struct {
	Id                   int     `json:"id"`
	ObjectId             int     `json:"object_id"`
	Longitude            float64 `json:"longitude"`
	Latitude             float64 `json:"latitude"`
	Length               float64 `json:"length"`
	Width                float64 `json:"width"`
	SpecialCase          *string `json:"special_case"`
	HazardSize           *string `json:"hazard_size"`
	CurbLength           float64 `json:"curb_length"`
	MeasuredHazardLength float64 `json:"measured_hazard_length"`
	InchFeet             float64 `json:"inch_feet"`
	H1                   float64 `json:"h1"`
	H2                   float64 `json:"h2"`
	Area                 float64 `json:"area"`
	Address              *string `json:"geocoded_address"`
	Note                 *string `json:"note"`
	Tech                 string  `json:"tech"`
	TechInitials         string  `json:"tech_initials"`
	WorkDate             string  `json:"work_date"`
}

func (m Measurement) Description() string {
	if m.SpecialCase != nil && m.Note != nil {
		if m.SpecialCase != "None" {
			return fmt.Sprintf("%s. %s.", *m.SpecialCase, *m.Note)
		} else {
			return *m.Note
		}
	}

	if m.SpecialCase != nil {
		return *m.SpecialCase
	}

	if m.Note != nil {
		return *m.Note
	}

	return ""
}
