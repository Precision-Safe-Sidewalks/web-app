package documents

import (
	"github.com/xuri/excelize/v2"
)

func HighlightCell(f *excelize.File, sheet string, cell string, center bool) {
	horizontalAlign := "left"

	if center {
		horizontalAlign = "center"
	}

	style, _ := f.NewStyle(&excelize.Style{
		Fill: excelize.Fill{
			Type:    "pattern",
			Color:   []string{"#FFFF00"},
			Pattern: 1,
		},
		Alignment: &excelize.Alignment{
			Horizontal: horizontalAlign,
		},
		Font: &excelize.Font{
			Size: 10,
		},
	})

	f.SetCellStyle(sheet, cell, cell, style)
}
