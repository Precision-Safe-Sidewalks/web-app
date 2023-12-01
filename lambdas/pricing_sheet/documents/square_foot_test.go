package documents

import (
	"testing"

	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/schema"
)

func ImportSquareFootFixture() schema.PricingSheetData {
	var pricing schema.PricingSheetData
	ImportJSONFile("../fixtures/data.square_foot.json", &pricing)
	return pricing
}

func TestSquareFootPricingSheet(t *testing.T) {
	data := ImportSquareFootFixture()
	generator := NewSquareFootPricingSheet(data)

	if _, err := generator.Generate(); err != nil {
		t.Errorf("Error generating inch foot pricing sheet: %v", err)
	}
}
