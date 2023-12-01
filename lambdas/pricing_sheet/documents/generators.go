package documents

type PricingSheetGenerator interface {
	Generate() (string, error)
}
