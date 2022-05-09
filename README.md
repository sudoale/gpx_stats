# GPX Stats

This project emerged by the interest of analyzing an upcoming running course or past running performances. 

# Analysis

## Course

This analysis offers you a visualization of the course profile of the choosen course. It calculates several statistical measures in order to get first insights about the course.

![Course Analysis](https://github.com/sudoale/gpx_stats/blob/main/docs/images/course_analysis.png?raw=true)

The statistical indicators include **per kilometer**:
- Ascent
- Descent
- Steepness (ascent + descent)

## Performance

This analysis provides several statistical insights about a past performance and can be analyzed either by time or distance (valuable for the analysis of an intervall training).

![Performance Analysis](https://github.com/sudoale/gpx_stats/blob/main/docs/images/performance_analysis.png?raw=true)

The statistical indicators include **per segment**:
- Distance
- Ascent
- Descent
- Average HR
- Gradual Adjusted Pace (GAP)
- Performance
- Vertical Ascent Meters

### GAP calculation

The Gradual Adjusted Pace indicator tries to estimate the required time on the flat on the basis of an uphill/downhill section. 
So running uphill a 10% at 10 km/h would translate to a much higher speed on the flat. More information on GAP can be gathered [here](https://medium.com/strava-engineering/an-improved-gap-model-8b07ae8886c3).
In this project, I developed an own formula for calculation a GAP for uphills. The formula considers a "reduction factor" which is multiplied with the elevation gain.

The first 50m elevation gain have a reduction factor of 0.9 which results in a max reduction of 45 seconds.
The remaining elevatain gain up to 100 have a reduction factor of 1.2.
The remaining elevatain gain up to 150 have a reduction factor of 1.5.
The remaining elevatain gain up to 200 have a reduction factor of 1.8.
The remaining elevatain gain above 200 reduces the gap for every meter of gain by 0.5 %.


### Performance


# Project setup

1. Clone the repository to your computer: ```git clone https://github.com/sudoale/gpx_stats.git```
2. Install the required python packages: ```conda install --file requirements.txt``` or ```pip install -r requirements.txt```
3. Run the webservice: ```python app.py```
