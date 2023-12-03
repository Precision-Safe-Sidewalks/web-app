package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/google/uuid"

	"app.bluezoneautomation.com/lambda-project-summary/v2/schema"
)

const (
	ENV_API_KEY      = "API_KEY"
	ENV_API_BASE_URL = "API_BASE_URL"
	S3_BUCKET        = "precision-safe-sidewalks"
)

type ProjectSummaryAPI struct {
	url string
	key string
}

// Construct a new project summary API
func NewProjectSummaryAPI() ProjectSummaryAPI {
	return ProjectSummaryAPI{
		url: os.Getenv(ENV_API_BASE_URL),
		key: os.Getenv(ENV_API_KEY),
	}
}

// Perform an HTTP request for the API with authentication
func (p ProjectSummaryAPI) performRequest(req *http.Request) (*http.Response, error) {
	client := &http.Client{}
	req.Header.Set("Authorization", fmt.Sprintf("Token %s", p.key))
	req.Header.Set("Content-Type", "application/json")
	return client.Do(req)
}

// Retrieve the project summary data for a project
func (p ProjectSummaryAPI) GetData(projectId int) (schema.ProjectSummaryData, error) {
	var data schema.ProjectSummaryData

	url := fmt.Sprintf("%s/api/project_summary/%d/data/", p.url, projectId)
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

// Mark a project summary request as complete by updating the S3 key for the
// generated document
func (p ProjectSummaryAPI) MarkComplete(requestId uuid.UUID, projectId int, key string) error {
	data := map[string]string{
		"request_id": requestId.String(),
		"s3_bucket":  S3_BUCKET,
		"s3_key":     key,
	}

	body, _ := json.Marshal(data)
	bodyReader := bytes.NewReader(body)

	url := fmt.Sprintf("%s/api/project_summary/%d/complete/", p.url, projectId)
	req, err := http.NewRequest("POST", url, bodyReader)

	if err != nil {
		return err
	}

	_, err = p.performRequest(req)

	return err
}
