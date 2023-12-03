package documents

import (
	"app.bluezoneautomation.com/lambda-project-summary/v2/schema"
)

type SquareFootProjectSummary struct {
	Data schema.ProjectSummaryData
}

func NewSquareFootProjectSummary(data schema.ProjectSummaryData) SquareFootProjectSummary {
	return SquareFootProjectSummary{Data: data}
}

func (s SquareFootProjectSummary) Generate() (string, error) {
	return "", nil
}
