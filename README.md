# Coastal Group: Roll Models

As part of summer institute 2019 held in National Water Center, Coastal Group works towards systematic analysis of large-scale modeling of coastal areas.

## Project Management
<img src="https://github.com/taataam/SI_2019_Coastal/blob/master/src/gantt/Gantt.png" width="800">

## Objectives
Metrics:
- **R**oughness Manning's (-)
- **D**ischarge (cms)
- **S**inuosity: Curvilinear Length/Straight Line Length)
- **T**ides: Low Range, High Range, w/Surge

| Physical Parameters | (R)oughness | (D)ischarge | (S)inuosity | (T)ides   |
|---------------------|-------------|-------------|-------------|-----------|
| Default Values      | 0.025       | 300         | 1           | Low Range |

| Simulation Name |   R   |   D  |  S  |    T    |            status            |
|:---------------:|:-----:|:----:|:---:|:-------:|:----------------------------:|
|       R20       |  0.02 |  300 |  1  |    L    |   <ul><li>- [ ] </li></ul>   |
|       R30       |  0.03 |  300 |  1  |    L    |   <ul><li>- [ ] </li></ul>   |
|       D100      | 0.025 |  100 |  1  |    L    |   <ul><li>- [ ] </li></ul>   |
|      D2000      | 0.025 | 2000 |  1  |    L    |   <ul><li>- [ ] </li></ul>   |
|       S150      | 0.025 |  300 | 1.5 |    L    |   <ul><li>- [ ] </li></ul>   |
|       S300      | 0.025 |  300 |  3  |    L    |   <ul><li>- [ ] </li></ul>   |
|        TH       | 0.025 |  300 |  1  |    H    |   <ul><li>- [ ] </li></ul>   |
|        TS       | 0.025 |  300 |  1  | w/Surge |   <ul><li>- [ ] </li></ul>   |

Domain Parameters:
- Estuary Dimensions/Shape	River Width(s)
- Barrier Island/Spit	Bathymetry/Topography	Shipping Channel
- Dominant Tidal Constituents

## Deliverable

## Instructions
The following steps should be taken for using `tide_constituents.py`:
1. Install Anaconda and load it in a command line.
2. Run the following command to create a new environment called `tides`:
```bash
conda create -n tides pip requests shapely beautifulsoup4 pandas scipy
```
then activate the environment ```conda activate tides```.

3. Install some extra packages with `pip`:
```bash
pip install py_noaa baker astronomia filelike pyparsing
```
4. Clone the tappy repository to a location and install it:
```bash
git clone -b py3 https://github.com/taataam/tappy.git
cd tappy
python setup.py install
```

An example showing how to use the code is provided in `src/tide_constituents/mobile_bay.py` 
