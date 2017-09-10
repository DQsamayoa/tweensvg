%.svg: %.dot
	dot -Tsvg $< -o $@

dotfiles=$(wildcard *.dot)
svgfiles=$(dotfiles:.dot=.svg)

testfiles: $(svgfiles)

clean:
	rm -f $(svgfiles)

.PHONY: testfiles clean
