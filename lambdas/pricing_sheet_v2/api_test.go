package main

import (
	"os"
	"testing"
)

func TestPricingSheetAPIGetData(t *testing.T) {
	os.Setenv("API_BASE_URL", "http://localhost:8000")

	api := NewPricingSheetAPI()
	_, err := api.GetData(1)

	if err != nil {
		t.Errorf("PricingSheetAPI.GetData() error: %v", err)
	}
}
