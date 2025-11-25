# Linkedin jobs scrapping

Market tech stack analysis

## Stockholm, Sweden

| Skill	| Number of Job Postings |
| ---------------------|------------------------|
| 	Git	| 129 | 
| 	Java |	99 |
| 	Python |	83 |
| 	AWS |	76 |
| 	CI/CD |	76 |
| 	SQL	| 75 |
| 	React |	71 |
| 	Rust |	68 |
| 	DevOps |	66 |
| 	Azure |	62 |


See more example charts in [doc/charts.md](./doc/charts.md)

## About

This repository contains a Jupyter notebook that collects data on the demand for various programming languages in job postings for a specified job title and location using web scraping techniques. The collected data is then analyzed and visualized to provide insights into the most sought-after programming languages in the job market for the given criteria.

You can modify the job title and location variables in the notebook to analyze different roles and regions. 

You can add more programming languages or skills to the `skills.csv` file to expand the analysis further.


## Usage

> no keys is needed to run this script as it scrapes publicly available job postings.

1. Clone the repository to your local machine.

2. Install the required Python packages using pip:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

3. Open the `collect.ipynb` Jupyter notebook in your preferred environment (e.g., Jupyter Notebook, JupyterLab, VSCode).
were you can collect and explore the data that has been collected.


### cron job for collecting data regularly

You can set up a cron job to run the data collection script at regular intervals. Here's an example of how to set up a cron job that runs the script every day at midnight:

```bash
crontab -e
```

then add the following line to the crontab file: 

```bash
0 0 1 * * /path/to/your/venv/bin/python /path/to/market-tech-stack-analysis/collect.py -t "Software Developer" -l "Sweden" -n 600 
```

you can also execute the notebook if you prefer that way: 

```bash
0 0 1 * * /path/to/your/venv/bin/jupyter nbconvert --execute /path/to/market-tech-stack-analysis/collect.ipynb 
```


you can also make the data into repport by 

```bash 
jupyter nbconvert --to html --no-input ./charts.ipynb
```