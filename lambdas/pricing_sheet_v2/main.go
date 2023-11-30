package main

import (
	"fmt"
)

func main() {
	data, err := FetchPricingSheetData(1)

	if err != nil {
		panic(err)
	}

	fmt.Println(data)
}
