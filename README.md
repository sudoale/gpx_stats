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

### Performance


# Project setup

1. Clone the repository to your computer: ```git clone https://github.com/sudoale/gpx_stats.git```
2. Install the required python packages: ```conda install requirements.txt``` or ```pip install -r requirements.txt```
3. Run the webservice: ```python app.py```
