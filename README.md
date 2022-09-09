<!-- https://github.com/annguy/customer-sentiment-monitor -->
<!-- https://innerjoin.bit.io/making-a-simple-data-pipeline-part-2-scheduling-etl-and-post-load-transformations-3e8517c59eab -->

# Project charter
1. Problem statement
2. Business case
3. Goals & Objectives
4. Work scope
5. Timeline
6. Responsibilities


# System Design for a Data-Driven and Explainable Customer Sentiment Monitor Using IoT and Enterprise Data

[Problem statement]
[Business case]
Short squeeze 
[Goals & Objectives]
<!-- https://innerjoin.bit.io/making-a-simple-data-pipeline-part-1-the-etl-pattern-7ea52c0f3579 -->
ETL(Extract, Transform, Load)
Extract, Transform, Load (ETL) is the general procedure of copying data from one or more sources into a destination system which represents the data differently from the source(s) or in a different context than the source(s).

Estimates possibilities
[Work scope]
Scrapping Reddit website
[Timeline]
Execution and iteration, monitoring
automation
[Responsibilities]
Solely done

This project was conducted at the Machine Learning and Data Analytics Lab, Friedrich-Alexander-University Erlangen-Nuremberg (FAU) in cooperation with Siemens Healthineers.

The datasets are publicly available for research purposes.

If you would like to get in touch, please contact an.nguyen@fau.de.


## How to install
These instructions will get you a copy of the project up and running on your local machine

### Clone
Clone this repo to your local machine

### Setup
Create environment using the requirements.txt

```
# using pip
pip install -r requirements.txt

# using Conda
conda create --name <env_name> --file requirements.txt
```

Activate environment

```
conda activate customer_sentiment_monitor 
```

Install src in the new environment

```
pip install -e.
```

Register a notebook kernel
```
python -m ipykernel install --user --name=customer_sentiment_monitor
```

upon modification, rebuild with the command
```
docker build --tag [태그명] .
```
you can find the newly created
```
docker images
```

## How to Run
1. To set the configurations, use the config.ini. The model_name, late_fusion_flag and feature_type from config.ini can be used to conduct the experiements. The rest of the configurations are exactly the same as in the paper.

2. To run the weekly analysis, use the command below

```
python main.py
```

After each week the results are saved in ```data/interim/```. If you want to continue training, use cont_week from config.ini.

3. To visualize and evaluate ```data/results/results.pickle``` from weekly analysis, ```notebooks/Visualization.ipynb``` can be used. The pdfs from visualization will be saved in ```data/visualizations/```


## Contributors
[An Nguyen](https://www.mad.tf.fau.de/person/an-nguyen/), 
[Andrey Kurzyukov](https://github.com/SherlockKA), 
[Thomas Kittler](https://www.linkedin.com/in/dr-thomas-kittler-a379aa174/), 
[Stefan Foerstel](https://www.linkedin.com/in/stefan-foerstel/)


## Project Organization
    ├── data
    │   ├── results                      <- The result from weekly analysis.
    │   ├── interim                      <- Intermediate data that has been transformed.
    │   ├── visualizations               <- The visualization of results from weekly analysis.
    │   └── raw                          <- The original, immutable data dump.
    ├── notebooks                        <- Jupyter notebooks. 
    ├── src                              <- Source code for use in this project.
        ├── config_parser.py             <- Script to parse configurations into dict.
        ├── general_helper_functions.py  <- Script with helper functions
        ├── train_Ensemble.py            <- Script to train XGBoost or RandomForest.
        ├── train_LSTM.py                <- Script to train LSTM.
        ├── visualize.py                 <- Script to visualize results from weekly analysis.
    ├── .gitignore                       <- Files that should be ignored.
    ├── README.md                        <- The top-level README for developers using this project.
    ├── config.ini                       <- Configurations.
    ├── requirement.txt                  <- The requirements file for reproducing the analysis environment, e.g.
    ├── main.py                          <- Main code.
    ├── setup.py                         <- makes project pip installable (pip install -e .) so src can be imported
