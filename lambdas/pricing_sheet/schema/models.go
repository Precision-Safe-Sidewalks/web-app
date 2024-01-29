package schema

import (
	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/constants"
	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/utils"
)

type PricingSheetData struct {
	Id           int                `json:"id"`
	Name         string             `json:"name"`
	Customer     Customer           `json:"customer"`
	Territory    Territory          `json:"territory"`
	Pricing      Pricing            `json:"pricing"`
	Contact      *Contact           `json:"contact"`
	SurveyDate   *string            `json:"survey_date"`
	PricingModel string             `json:"pricing_model"`
	BDM          User               `json:"business_development_manager"`
	Surveyor     *User              `json:"surveyor"`
	Measurements []MeasurementGroup `json:"measurements"`
}

// Calculate the total area sureyed
func (p PricingSheetData) TotalSurveyArea() float64 {
	var area float64

	for _, group := range p.Measurements {
		for _, measurement := range group.Measurements {
			area += measurement.Area
		}
	}

	return area
}

// Calculate the total area (square feet) for all Replace
// special cases from the survey data
func (p PricingSheetData) TotalReplaceArea() float64 {
	var area float64

	for _, group := range p.Measurements {
		for _, measurement := range group.Measurements {
			if measurement.HazardSize != nil && *measurement.HazardSize == "Replace" {
				area += measurement.Area
			}
		}
	}

	return area
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
	Area                 float64 `json:"area"`
	Address              *string `json:"geocoded_address"`
	Note                 *string `json:"note"`
	Description          string  `json:"description"`
}

func (m Measurement) GetHighlightColor() string {
	specialCase := utils.SafeString(m.SpecialCase)
	hazardSize := utils.SafeString(m.HazardSize)

	// If curb, highlight if the either:
	// - Panel length or width are non-zero [Yellow]
	// - Hazard size is not Other [Yellow]
	if specialCase == "Curb" {
		if m.Width+m.Length > 0 || hazardSize != "Other" {
			return constants.COLOR_YELLOW
		}
	}

	// If recuts, highlight if:
	// - Hazard size is not Large [Pink]
	if specialCase == "Recuts" {
		if hazardSize != "Large" {
			return constants.COLOR_PINK
		}
	}

	// If replace, highlight if:
	// - Hazard size is Small, Medium, or Large [Green]
	// FIXME: determine if rule is necessary
	if hazardSize == "Replace" {
		if hazardSize == "Small" || hazardSize == "Medium" || hazardSize == "Large" {
			return constants.COLOR_GREEN
		}
	}

	return ""
}
