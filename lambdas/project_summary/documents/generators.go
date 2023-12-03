package documents

type ProjectSummaryGenerator interface {
	Generate() (string, error)
}
