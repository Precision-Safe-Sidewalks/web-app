package documents

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"testing"

	"app.bluezoneautomation.com/lambda-project-summary/v2/schema"
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

func ImportInchFootFixture() schema.ProjectSummaryData {
	var pricing schema.ProjectSummaryData
	ImportJSONFile("../fixtures/data.inch_foot.json", &pricing)
	return pricing
}

func TestInchFootProjectSummary(t *testing.T) {
	data := ImportInchFootFixture()
	generator := NewInchFootProjectSummary(data)
	filename, err := generator.Generate()

	if err != nil {
		t.Errorf("Error generating inch foot project summary: %v", err)
	}

	if _, err := os.Stat(filename); err != nil {
		t.Errorf("Error generating inch foot project summary: %v", err)
	}
}
