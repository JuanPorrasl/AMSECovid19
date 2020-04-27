AMSECovid19
==============================

The project "Covid: JHU augmented dataset" consists in creating a dashboard to follow the daily evolution of covid-19 around the world, with the help of graphs, automatically updated and available online. A detailed analysis for some countries such as France and the United States will be proposed taking into account the demographic data by department. The set is developed on Python, which is a strength for data processing.

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    │
    ├── confidential        <- Secret folder NOT ON GITHUB 
    │   └── secrets.py      <- Secret script where ID and password are saved. Please, create your file         │                          with following elements: DASHBOARD_ACCESS = {'USERNAME': 'PASSWORD'}
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── dash               <- Main folder of the dashboard
    │   ├── app.py                 <- Tool script to allow dashboard in multiple files with callbacks.
    │   ├── assets                  
    │   │   └── favicon.ico        <- Junior Data Analysts Favicon
    │   ├── cleaning_data.py       <- Cleaning datas for the index page
    │   ├── cleaning_data_br.py    <- Cleaning datas for the brazil page
    │   ├── cleaning_data_fr.py    <- Cleaning datas for the france page
    │   │
    │   ├── data                  
    │   │   ├── external           <- Data from third party sources.
    │   │   ├── processed          <- The final, canonical data sets for modeling.
    │   │   ├── raw                <- The original, immutable data dump.
    │   │   └── working            <- Temporary folder for working datas. Supose to be empty at the end
    │   │
    │   ├── pages                 
    │   │   ├── page_analysis.py    <- Content of the page "Global Analysis"
    │   │   ├── page_brazil.py      <- Content of the page "brazil"
    │   │   ├── page_france.py      <- Content of the page "france"
    │   │   ├── page_legalnotice.py <- Content of the page "legal"
    │   │   └── page_worldwide.py   <- Content of the main page
    │   │
    │   └── index.py               <- Inital script to run for displaying Dashboad.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="http://git.equancy.io/tools/cookiecutter-data-science-project/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
