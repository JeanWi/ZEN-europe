# 05-mean_variance: uncertain costs for the mean-variance plugin

Raw data for the input files of the ZEN-garden plugin `mean_variance_optimization`
(ZEN-galaxies). The files are processed by `zen_europe/mean_variance` and
written to `<dataset>/mean_variance/` when the setting
`mean_variance.write_files` is `true`:

```yaml
settings:
  mean_variance:
    write_files: true
    technology_relative_sd_source: trl
```

## Files

| File                                    | Content                                                                                                                                                                                                                                                                                                                                              |
|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `SD calculation.xlsx`                   | Original Excel calculation (documentation only, not read by the code)                                                                                                                                                                                                                                                                                |
| `Technology_classification.csv`         | Sheet `SDs` of the Excel file, one row per technology: IEA technology name, TRL own assessment, Primary technology class |
| `TRL_IEA_technology_classification.csv` | TRL per technology from the IEA ETP Clean Energy Technology Guide (column `trl2024`). Some TRL ranges give a range; the higher TRL is used.                                                                                                                                                                                                          |
| `TRL_SD_translation.csv`                | Relative standard deviation per TRL (AACE cost estimate classification, source in the first line)                                                                                                                                                                                                                                                    |
| `relative_sd_import_price.csv`          | Relative standard deviation of the import price per carrier (hand-set, taken over from the Crystal_Ball dataset)                                                                                                                                                                                                                                     |
| `correlation_import_price.csv`          | Correlation of the import prices (carrier x carrier, taken over from the Crystal_Ball dataset)                                                                                                                                                                                                                                                       |

## Calculation

- **Relative sd of technology capex** (`zen_europe/mean_variance/relative_sd.py`):
  - `trl`: TRL from the IEA guide (or own assessment; incumbents have TRL 9),
    translated with `TRL_SD_translation.csv` (TRL 9 -> 10 %, ..., TRL 0 -> 100 %).
- **Correlation of technology capex** (`zen_europe/mean_variance/correlation.py`):
  cosine similarity of feature vectors with weight 0.9 for the primary
  technology class and 0.3 for every input/output carrier of the technology.

## Changes compared to the Excel file

- `ammonia_pipeline`, `methanol_pipeline` and `olefin_pipeline` were added to
  `Technology_classification.csv` by analogy to `hydrogen_pipeline` (class `Pipelines`, TRL 9).
- `Technology_classification.csv` was converted to UTF-8 (the Excel export mixed cp1252 and UTF-8).
