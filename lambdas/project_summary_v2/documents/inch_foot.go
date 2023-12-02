package documents

import (
	"app.bluezoneautomation.com/lambda-project-summary/v2/schema"
)

type InchFootProjectSummary struct {
	Data schema.ProjectSummaryData
}

func NewInchFootProjectSummary(data schema.ProjectSummaryData) InchFootProjectSummary {
	return InchFootProjectSummary{Data: data}
}

func (s InchFootProjectSummary) Generate() (string, error) {
	return "", nil
}
