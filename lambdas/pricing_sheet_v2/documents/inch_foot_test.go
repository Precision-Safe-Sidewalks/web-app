package documents

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"testing"

	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/schema"
)

func ImportJSONFile(filename string, data interface{}) {
	file, err := os.Open(filename)
	if err != nil {
		panic(err)
	}
	defer file.Close()

	bytes, err := ioutil.ReadAll(file)
	if err != nil {
		panic(err)
	}

	if err := json.Unmarshal(bytes, &data); err != nil {
		panic(err)
	}
}

func ImportInchFootFixture() schema.PricingSheetData {
	var pricing schema.PricingSheetData
	ImportJSONFile("../fixtures/data.inch_foot.json", &pricing)
	return pricing
}

func TestInchFootPricingSheet(t *testing.T) {
	data := ImportInchFootFixture()
	generator := NewInchFootPricingSheet(data)

	if _, err := generator.Generate(); err != nil {
		t.Errorf("Error generating inch foot pricing sheet: %v", err)
	}
}
