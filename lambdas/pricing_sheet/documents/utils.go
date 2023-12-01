package documents

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
