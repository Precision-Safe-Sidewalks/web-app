package documents

import (
	"os"
	"testing"

	"app.bluezoneautomation.com/lambda-project-summary/v2/schema"
)

func ImportSquareFootFixture() schema.ProjectSummaryData {
	var pricing schema.ProjectSummaryData
	ImportJSONFile("../fixtures/data.square_foot.json", &pricing)
	return pricing
}

func TestSquareFootProjectSummary(t *testing.T) {
	data := ImportSquareFootFixture()
	generator := NewSquareFootProjectSummary(data)
	filename, err := generator.Generate()

	if err != nil {
		t.Errorf("Error generating square foot project summary: %v", err)
	}

	if _, err := os.Stat(filename); err != nil {
		t.Errorf("Error generating square foot project summary: %v", err)
	}
}
