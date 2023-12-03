package documents

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

// Convert the ISO 8601 date string to time.Time
func DateStringToTime(date string) time.Time {
	value, _ := time.Parse("2006-01-02", date)
	return value
}
