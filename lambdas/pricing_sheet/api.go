package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/google/uuid"

	"app.bluezoneautomation.com/lambda-pricing-sheet/v2/schema"
)

const (
	ENV_API_KEY      = "API_KEY"
	ENV_API_BASE_URL = "API_BASE_URL"
	S3_BUCKET        = "precision-safe-sidewalks"
)

type PricingSheetAPI struct {
	url string
	key string
}

// Construct a new pricing sheet API
func NewPricingSheetAPI() PricingSheetAPI {
	return PricingSheetAPI{
		url: os.Getenv(ENV_API_BASE_URL),
		key: os.Getenv(ENV_API_KEY),
	}
}

// Perform an HTTP request for the API with authentication
func (p PricingSheetAPI) performRequest(req *http.Request) (*http.Response, error) {
	client := &http.Client{}
	req.Header.Set("Authorization", fmt.Sprintf("Token %s", p.key))
	req.Header.Set("Content-Type", "application/json")
	return client.Do(req)
}

// Retrieve the pricing sheet data for a project
func (p PricingSheetAPI) GetData(projectId int) (schema.PricingSheetData, error) {
	var data schema.PricingSheetData

	url := fmt.Sprintf("%s/api/pricing_sheet/%d/data/", p.url, projectId)
	req, err := http.NewRequest("GET", url, nil)

	if err != nil {
		return data, err
	}

	resp, err := p.performRequest(req)

	if err != nil {
		return data, err
	}

	defer resp.Body.Close()

	err = json.NewDecoder(resp.Body).Decode(&data)
	return data, err
}

// Mark a pricing sheet request as complete by updating the S3 key for the
// generated document
func (p PricingSheetAPI) MarkComplete(requestId uuid.UUID, projectId int, key string) error {
	data := map[string]string{
		"request_id": requestId.String(),
		"s3_bucket":  S3_BUCKET,
		"s3_key":     key,
	}

	body, _ := json.Marshal(data)
	bodyReader := bytes.NewReader(body)

	url := fmt.Sprintf("%s/api/pricing_sheet/%d/complete/", p.url, projectId)
	req, err := http.NewRequest("POST", url, bodyReader)

	if err != nil {
		return err
	}

	_, err = p.performRequest(req)

	return err
}
