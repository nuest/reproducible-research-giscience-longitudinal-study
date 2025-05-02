# Data Sheet

Columns of the `all-data.csv` file

 - `conf`: "agile"" or "giscience"
 - `paper`: Unique paper identifier as `conf` + `_` + `year` + `_` + `000` (paper_id in 3 digits)
 - `year`: Year of the conference
 - `title`: Title of the paper
 - `link`: Link to paper
 - `oa`: True/False
 - `dasa`: True/False
 - `rev1`: reviewer1 id
 - `rev2`: reviewer2 id
 - `rev1_cp`: True/False
 - `rev2_cp`: True/False
 - `rev1_data`: Values factored to UDAI naming scheme
 - `rev2_data`: Values factored to UDAI naming scheme
 - `rev1_methods`. Values factored to UDAI naming scheme
 - `rev2_methods`: Values factored to UDAI naming scheme
 - `rev1_results`: Values factored to UDAI naming scheme
 - `rev2_results`: Values factored to UDAI naming scheme
 - `rev1_ce`: True/False
 - `rev2_ce`: True/False
 - `rev1_notes`
 - `rev2_notes`
 - `consolidated_cp`: True/False
 - `consolidated_data`: Values factored to UDAI naming scheme
 - `consolidated_methods`: Values factored to UDAI naming scheme
 - `consolidated_results`: Values factored to UDAI naming scheme
 - `consolidated_ce`: True/False
 - `consolidated_notes`
 - `disagr_type`: Values: "no disagreement", "borderline conceptual paper", "annotation inconsistencies", "uncertain assessment", "major disagreement".
 - `disagr_id`. Numeric values associated to `disagr_type`. Values: 0, 1, 2, 3, 4. 
 - `agile_badge`: True/False
 - `agile_reproreport`: Link to AGILE Reproducibility Report. `False` otherwise
