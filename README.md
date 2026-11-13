# TrendLens Lite

**TrendLens Lite** is a small interactive Earth-system trend explorer built for the NASA Space Apps Challenge 2026 challenge, *Be An Earth System Trend Detective!*.

It retrieves monthly observations from the public NASA POWER point API and calculates annual means, a Theil–Sen trend slope with a 95% confidence interval, and Kendall's tau with a p-value.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The app needs an internet connection to retrieve NASA POWER data.

## Data source

NASA POWER monthly point API: https://power.larc.nasa.gov/api/temporal/monthly/point

Parameters:
- `T2M`: 2-m air temperature (°C)
- `PRECTOTCORR`: corrected precipitation rate (mm/day)

NASA POWER documentation: https://power.larc.nasa.gov/docs/

## Methods

1. Retrieve monthly values for the selected coordinates and years.
2. Exclude invalid/sentinel values.
3. Calculate the arithmetic mean of available monthly values for each year.
4. Estimate the trend magnitude with the Theil–Sen median slope and 95% confidence interval.
5. Report Kendall's tau and its p-value as evidence about monotonic association.

## Limitations

- The selected locations are point coordinates, not city-wide spatial averages.
- POWER data are gridded/reanalysis-informed estimates, not direct local station measurements.
- Annual means can conceal seasonal patterns.
- The basic Kendall test does not correct for serial autocorrelation or multiple comparisons.
- A statistical trend does not establish causation.

## AI/tool disclosure

If AI tools were used to assist with code, writing, debugging, or presentation, disclose the tools and describe the assistance accurately in the submission, following the event's rules.

## License

MIT License. See `LICENSE`.
