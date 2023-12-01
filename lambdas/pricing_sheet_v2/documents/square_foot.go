package documents

type SquareFootPricingSheet struct {
}

func NewSquareFootPricingSheet() SquareFootPricingSheet {
	return SquareFootPricingSheet{}
}

func (p SquareFootPricingSheet) Generate() (string, error) {
	return "", nil
}
