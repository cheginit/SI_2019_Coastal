# Coastal Group: Roll Models

As part of summer institute 2019 held in National Water Center, Coastal Group works towards systematic analysis of large-scale modeling of coastal areas.

## Project Management
<img src="https://github.com/taataam/SI_2019_Coastal/blob/master/src/gantt/Gantt.png" width="800">

## Objectives

Identify contributions of relevant physical processes to total water prediction by modeling idealized scenarios in coastal transition zones to provide a framework for efficient forecasting.

## Idealized domains

The idealized domains were inspired by rivers and bays geometries over the Gulf and East Coast.

 A few metrics were chosen to compare different rivers and bays and scale the idealized domains.
 
  Bay/Estuary geometry:
- **Wt** Bay width at river end (upstream) - Wt = Wr in triagular geometry
- **Wb** Bay width at ocean end (downstream)
- **Lb** Bay length 
- Parameters:
  * Rbr = Wb / Wr
  * Rbt = Wb / Wt
  * Rlb = Lb / Wb
   
 River geometry:
- **SI**nuosity = Curvilinear Length / Straight Line Length 
- **Wr** River width

Three main **Classes** determined for this analysis:
  1) River discharge directly in the ocean
  2) River discharge in triangular bay
  3) River discharge in trapezoidal/rectangular bay
  
For **Class 1**, two subdivisions were created to evaluate river sinuosity contribution in comparison with a straight line river:
  A) SI = 1
  B) SI = 1.45

For **Classes 2** and **3**, three subdivisions were created to include the analysis of a barrier island between the bay and the ocean.
  A) SI = 1
  B) SI = 1.45
  C) SI = 1 with barrier island

Idealized models domains

<img src="https://github.com/taataam/SI_2019_Coastal/blob/master/docs/Fig_Domains.png" width="600">

## Modeling configuration

A set of scenarios was created to evaluate water levels under tides forcing, storm surge, and discharge and roughness variation.

Simulation Scenarios:
- **R**oughness Manning's (-)
- **D**ischarge (cms)
- **T**ides: **P**redicted, **S**torm Surge

|      | Simulation Name |   R   |   D  |    T    |            status            |
|:----:|:---------------:|:-----:|:----:|:-------:|:----------------------------:|
|  S1  |     **Ref**     | 0.025 |    0 |    P    |   <ul><li>- [x] </li></ul>   |
|  S2  |       R20       | 0.020 |    0 |    P    |   <ul><li>- [x] </li></ul>   |
|  S3  |       R30       | 0.030 |    0 |    P    |   <ul><li>- [x] </li></ul>   |
|  S4  |      D1000      | 0.025 | 1000 |    P    |   <ul><li>- [x] </li></ul>   |
|  S5  |        TS       | 0.025 |    0 |    S    |   <ul><li>- [x] </li></ul>   |

## Results

- Identification of tidal signal in the river upstream for under different geometries and scenarios
- Identification of river and bay geometry contribution, as well as roughness, discharge, tides and storm surge in total water prediction

## Deliverable

- Final Report and Presentation

## Instructions
The following steps should be taken for using the plotting scripts:
1. Install docker.
2. Change directory to `src/docker` and create an image from the `Dockerfile`:
```bash
docker build -t plot .
```
3. Copy the plotting scripts to the folder that contains the D-Flow outputs and run one of the script e.g., `cross_section.py`, as follows:
```bash
docker run -v "$PWD":/home/plot plot python cross_section.py C2_A1_S1_R25_D0_TPG
```


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
