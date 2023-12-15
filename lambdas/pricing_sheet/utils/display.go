package utils

import (
	"time"
)

// Convert the boolean to an integer (0/1)
func BoolToInt(state bool) int {
	if state {
		return 1
	}

	return 0
}

// Safely derefence a string pointer
func SafeString(text *string) string {
	if text == nil {
		return ""
	}

	return *text
}

// Safely dereference a date string pointer and format
func SafeDateString(text *string) string {
	if text == nil {
		return ""
	}

	date, err := time.Parse("2006-01-02", *text)
	if err != nil {
		return ""
	}

	return date.Format("1/2/2006")
}
