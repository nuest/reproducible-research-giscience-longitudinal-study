# Data Sheet

Columns of the `all-data.csv` file

| Column name    | Description | Values |
| -------- | ------- |------- |
| `conf`  |   Conference series  | "agile", "giscience" |
| `paper` | Unique paper identifier as `conf` + `_` + `year` + `_` + `000` (paper_id in 3 digits)     | String |
| `year`    | Year of the conference (4 digits)    | Integer |
| `title` | Title of the paper | String |
| `link` | Link to paper (DOI or publisher link) | URL |
| `oa` | If proceedings are Open Access | True/False |
| `dasa` | If DASA section (or similar info) exists | True/False |
| `rev1` | Id of assessor 1 (A1)  | String |
| `rev2` | Id of assessor 2 (A2)  | String
| `rev1_cp` | If paper is a conceptual paper (A1) | True/False |
| `rev2_cp` | If paper is a conceptual paper (A2) | True/False |
| `rev1_data` | Reproducibility level of **Input Data** criterion according to A1 | "U", "D", "A", "O", "NA" |
| `rev2_data`| Reproducibility level of **Input Data** criterion according to A2 |  "U", "D", "A", "O", "NA" |
| `rev1_methods` | Reproducibility level of **Methods,...** criterion according to A1 | "U", "D", "A", "O", "NA" |
| `rev2_methods` | Reproducibility level of **Methods,...** criterion according to A2 | "U", "D", "A", "O", "NA" |
| `rev1_results` | Reproducibility level of **Results** criterion according to A1 | "U", "D", "A", "O", "NA" |
| `rev2_results` | Reproducibility level of **Results** criterion according to A2 | "U", "D", "A", "O", "NA" |
| `rev1_ce` | If **Computational Environment** is clearly described in the paper according to A1 | True/False |
| `rev2_ce`| If **Computational Environment** is clearly described in the paper according to A2 | True/False |
| `rev1_notes` | Assessment notes taken by A1 | String |
| `rev2_notes` | Assessment notes taken by A2 | String |
| `consolidated_cp` | Final value agreed between `rev1_cp` and `rev2_cp` | True/False |
| `consolidated_data` | Final value agreed between `rev1_data` and `rev2_data` | "U", "D", "A", "O", NA" |
| `consolidated_methods` | Final value agreed between `rev1_methods` and `rev2_methods` | "U", "D", "A", "O", NA" |
| `consolidated_results` | Final value agreed between `rev1_results` and `rev2_results` | "U", "D", "A", "O", NA" |
| `consolidated_ce` | Final value agreed between `rev1_ce` and `rev2_ce` | True/False |
| `consolidated_notes` | Notes related to the discussion to reach a consensus on `consolidated_*` | String |
| `disagr_type` | Categories of disagreement between A1 and A2 | "no disagreement", "borderline conceptual paper", "annotation inconsistencies", "uncertain assessment", "significant disagreement" |
| `disagr_id` | Numeric values associated to `disagr_type` | 0, 1, 2, 3, 4 | 
| `agile_badge`| If an AGILE paper earned a Reprocucibility badge | True/False |
| `agile_reproreport` | Link to AGILE Reproducibility Report | URL, `NA` | 
