# Coastal Group: Roll Models

As part of summer institute 2019 held in National Water Center, Coastal Group works towards systematic analysis of large-scale modeling of coastal areas.

## Project Management
<img src="https://github.com/taataam/SI_2019_Coastal/blob/master/src/gantt/Gantt.png" width="800">

## Objectives

Simulation Scenarios:
- **R**oughness Manning's (-)
- **D**ischarge (cms)
- **T**ides: Low Range, High Range, w/Surge

| Simulation Name |   R   |   D  |  S  |    T    |            status            |
|:---------------:|:-----:|:----:|:---:|:-------:|:----------------------------:|
|     **Ref**     | 0.025 |  300 |  1  |    L    |   <ul><li>- [x] </li></ul>   |
|       R20       | 0.020 |  300 |  1  |    L    |   <ul><li>- [x] </li></ul>   |
|       R30       | 0.030 |  300 |  1  |    L    |   <ul><li>- [x] </li></ul>   |
|       D0        | 0.025 |    0 |  1  |    L    |   <ul><li>- [x] </li></ul>   |
|      D1000      | 0.025 | 1000 |  1  |    L    |   <ul><li>- [x] </li></ul>   |
|      D2000      | 0.025 | 2000 |  1  |    L    |   <ul><li>- [x] </li></ul>   |
|        TH       | 0.025 |  300 |  1  |    H    |   <ul><li>- [ ] </li></ul>   |
|        TS       | 0.025 |  300 |  1  | w/Surge |   <ul><li>- [x] </li></ul>   |

Domain Parameters:
- Classes:
  1) River discharge directly in the ocean
  2) River discharge in triangular bay
  3) River discharge in trapezoidal/rectangular bay

River geometry:
- **S**inuosity: Curvilinear Length/Straight Line Length
  A) S = 1
  B) S > 1
- **Wr** River width

Bay/Estuary geometry:
- **Wt** Bay width at river end (upstream) - Wt = Wr in triagular geometry
- **Wb** Bay width at ocean end (downstream)
- **Lb** Bay length 
- Parameters:
  * Rbr = Wb / Wr
  * Rbt = Wb / Wt
  * Rlb = Lb / Wb

Barrier Island:
- Opening length

Spit	Bathymetry/Topography	Shipping Channel

Idealized models domains

<img src="https://github.com/taataam/SI_2019_Coastal/blob/master/src/Fig-Domains.png" width="600">

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

The following steps should be taken for using `gantt.py`:
1. Install Anaconda and load it in a command line.
2. Run the following command to create a new environment called `gantt`:
```bash
conda create -n gantt plotly pandas psutil
```
then activate the environment ```conda activate gantt```.

3. Install an extra packages:
```bash
conda install -c plotly plotly-orca
``` 
4. Then go the script's directory and run it:
```bash
cd src/gantt
python gantt_chart.py
```
