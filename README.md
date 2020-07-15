# COVID-19 Statistical Modelling
An evolving set of Bayesian Hierarchical models being used to model the spread of COVID-19 and its potentially dependent factors. There is an accompanying collection of scripts to collect covid19 and other related data.

# Climate & BCG: Effects on COVID-19 Death Growth Rates
An [Arxiv pre-pint](https://arxiv.org/abs/2007.05542) was submitted on 10 July 2020. The code used to do the analysis of this paper resides in this repository. Currently the repository is a bit messy so a brief explanation is given below to help readers navigate to the important sections.

## Notebooks
All notebooks in this repository reside in the `notebooks` directory. The main notebooks of interest to readers of the paper begin with `4.1.1.xxxx`. The notebooks generally have mostly explanatory names for which model is contained inside. For complete clarity the notebook definitions are given below.

| Model                   | Notebook                                      |
|-------------------------|:---------------------------------------------|
| Time varying growth     | 4.1.1.10 Sigmoid Growth Regression.ipynb      |
| No Factors              | 4.1.1.3 No Params Regression.ipynb            |
| BCG vaccine coverage    | 4.1.1.1 BCG Vaccine Coverage Regression.ipynb |
| Temperature             | 4.1.1.2 Temperature Regression.ipynb          |
| Relative Humidity       | 4.1.1.3 Humidity Regression.ipynb             |
| UV Index                | 4.1.1.3 UVindex Regression.ipynb              |
| Tests per 1000 (testing)| 4.1.1.4 Test Rate Regression.ipynb            |
| Positive Rate (testing) | 4.1.1.5 Positive Test Rate Regression.ipynb   |
| All excluding testing   | 4.1.1.12 BCG and Climate(incl. UV).ipynb |
| All including testing   | 4.1.1.11 BCG, Climate(incl. UV) and Testing.ipynb |

##### A+ Blood Type
| Model                   | Notebook                                      |
|-------------------------|:---------------------------------------------|
| Blood                   | 4.1.1.7 A+ Blood Type Regression.ipynb |
| All including testing and blood | 4.1.1.11 BCG, Climate(incl. UV), Testing and Blood Regression.ipynb |
