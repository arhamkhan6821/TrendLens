# TrendLens Lite — 240-second judging script

**0:00–0:25 | The problem**  
Earth-system data are extensive, but it can be difficult to move from raw observations to an understandable trend. We built TrendLens Lite to make a small, transparent investigation reproducible.

**0:25–0:55 | The idea**  
TrendLens Lite lets a user choose a Bangladesh location, an Earth-system variable, and a time period. It retrieves NASA POWER monthly data and turns them into annual summaries.

**0:55–1:45 | Live demonstration**  
Open the app. Select Dhaka, choose air temperature, and fetch the NASA data. Show the annual time-series chart. Point out the annual observations, estimated slope, confidence interval, and Kendall p-value. Switch to precipitation and repeat if the API responds in time.

**1:45–2:35 | Scientific method**  
We aggregate valid monthly observations into annual means. The Theil–Sen estimator gives a robust slope and a confidence interval. Kendall's tau and its p-value summarize monotonic association. The app also exports the annual data as CSV.

**2:35–3:20 | Interpretation and limitations**  
A trend is not the same as a cause. POWER is a gridded/reanalysis-informed data product, not a direct station record. Our first version uses point coordinates, annual averages, and a basic Kendall test that does not correct for serial autocorrelation. Those limits are shown in the app rather than hidden.

**3:20–4:00 | Why it matters / next steps**  
TrendLens Lite is a transparent starting point for exploring environmental change. Next, we would add seasonal tests, autocorrelation-aware inference, spatial sampling, and validation against independent station or reference datasets. Thank you.
