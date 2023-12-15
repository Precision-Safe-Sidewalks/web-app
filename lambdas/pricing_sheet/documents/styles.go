package documents

import (
	"strings"

	"github.com/xuri/excelize/v2"
)

// Highlight a cell by copying it's current style and replacing the fill. Force
// the font color to black.
func HighlightCell(f *excelize.File, sheet string, cell string, center bool) error {
	style, err := CopyCellStyle(f, sheet, cell)
	if err != nil {
		return err
	}

	style.Fill.Type = "pattern"
	style.Fill.Color = []string{"#FFFF00"}
	style.Fill.Pattern = 1

	if style.Font != nil {
		style.Font.Color = "#000000"
	}

	styleId, err := f.NewStyle(style)
	if err != nil {
		return err
	}

	return f.SetCellStyle(sheet, cell, cell, styleId)
}

// Copy the style from a cell
func CopyCellStyle(f *excelize.File, sheet string, cell string) (*excelize.Style, error) {
	idx, err := f.GetCellStyle(sheet, cell)
	if err != nil {
		return nil, err
	}

	style, err := f.GetStyle(idx)
	if err != nil {
		return nil, err
	}

	newStyle := &excelize.Style{}
	newStyle.Border = make([]excelize.Border, len(style.Border))
	newStyle.Fill = style.Fill
	newStyle.NumFmt = style.NumFmt
	newStyle.DecimalPlaces = style.DecimalPlaces
	newStyle.NegRed = style.NegRed

	copy(newStyle.Border, style.Border)
	copy(newStyle.Fill.Color, style.Fill.Color)

	if style.Font != nil {
		newStyle.Font = &excelize.Font{}
		*newStyle.Font = *style.Font

		if style.Font.ColorTheme != nil {
			*newStyle.Font.ColorTheme = *style.Font.ColorTheme
		}
	}

	if style.Alignment != nil {
		newStyle.Alignment = &excelize.Alignment{}
		*newStyle.Alignment = *style.Alignment
	}

	if style.Protection != nil {
		newStyle.Protection = &excelize.Protection{}
		*newStyle.Protection = *style.Protection
	}

	if style.CustomNumFmt != nil {
		customNumFmt := strings.Clone(*style.CustomNumFmt)
		newStyle.CustomNumFmt = &customNumFmt
	}

	return newStyle, nil
}
