#!./env/bin/python3
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import logging
from tqdm import tqdm
import time
import datetime
import argparse
import sys
import os
from collections import defaultdict


def get_relevant_skills():
    prg_skills = pd.read_csv("./skills.csv")["skills"].to_list()
    prg_skills = set(prg_skills)

    users_of_languages = defaultdict(int)
    for l in prg_skills:
        users_of_languages[l] = 0
    return dict(users_of_languages)


def search_linkedin_jobs(title: str, location: str, num_jobs: int, output_path:str):
    users_of_languages = get_relevant_skills()
    prg_skills = set(users_of_languages.keys())
    job_list = []
    one_hot_skills = {s : [] for s in prg_skills}

    for start in tqdm(range(0, num_jobs, 25)):
        list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&distance=25&f_TPR=&f_WT=1&start={start}"

        response = requests.get(list_url)

        list_data = response.text
        list_soup = BeautifulSoup(list_data, "html.parser")
        page_jobs = list_soup.find_all("li")

        id_list = []

        for job in page_jobs:
            base_card_div = job.find("div", {"class": "base-card"})
            if base_card_div == None:
                continue
            job_id = base_card_div.get("data-entity-urn").split(":")[3]
            id_list.append(job_id)

        for job_id in id_list:
            job_url = (
                f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
            )

            job_response = requests.get(job_url)
            if job_response.status_code != 200:
                logging.warning(
                    f"Failed to retrieve job posting {job_id}: Status code {job_response.status_code}"
                )
                continue
            job_soup = BeautifulSoup(job_response.text, "html.parser")

            job_post = {}

            try:
                job_post["job_title"] = job_soup.find(
                    "h2",
                    {
                        "class": "top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"
                    },
                ).text.strip()
            except:
                job_post["job_title"] = None

            try:
                job_post["company_name"] = job_soup.find(
                    "a", {"class": "topcard__org-name-link topcard__flavor--black-link"}
                ).text.strip()
            except:
                job_post["company_name"] = None

            try:
                job_post["location"] = (
                    job_soup.find(
                        "span", {"class": "topcard__flavor topcard__flavor--bullet"}
                    )
                    .text.strip()
                    .split(",")[0]
                    .strip()
                )
            except:
                job_post["location"] = None

            try:
                job_post["time_posted"] = job_soup.find(
                    "span", {"class": "posted-time-ago__text topcard__flavor--metadata"}
                ).text.strip()
            except:
                job_post["time_posted"] = None

            try:
                job_post["num_applicants"] = (
                    job_soup.find(
                        "span",
                        {
                            "class": "num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet"
                        },
                    )
                    .text.strip()
                    .replace(" applicants", "")
                )
            except:
                job_post["num_applicants"] = 0

            for lang in prg_skills:
                if (
                    f"{lang.lower()}"
                    in job_soup.find(
                        "div",
                        {
                            "class": "show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden"
                        },
                    ).text.lower()
                ):
                    users_of_languages[lang] += 1
                    one_hot_skills[lang].append(job_post["company_name"])
            job_list.append(job_post)
            time.sleep(
                random.uniform(1, 3)
            )  # Sleep between requests to avoid rate limiting

    jobs_df = pd.DataFrame(job_list)
    jobs_df.to_csv(
        f'./results/jobs_{title}_{location}_{datetime.datetime.now().strftime("%Y-%m-%d")}.csv',
        index=False,
    )

    skill_usage = (
        pd.DataFrame.from_dict(
            users_of_languages, orient="index", columns=["Number of Job Postings"]
        )
        .reset_index()
        .rename(columns={"index": "Programming Skill"})
    )
    skill_usage.drop(
        skill_usage[skill_usage["Number of Job Postings"] == 0].index, inplace=True
    )
    skill_usage.to_csv(
        f'./results/skills_{title}_{location}_{datetime.datetime.now().strftime("%Y-%m-%d")}.csv',
        index=False,
    )

    one_hot_df = pd.DataFrame.from_dict(one_hot_skills, orient='index').transpose()
    one_hot_df.to_csv(f'{output_path}one_hot_skills_{title}_{location}_{datetime.datetime.now().strftime("%Y-%m-%d")}.csv', index=False)

    companies_used_skill = {}
    for skill, companies in one_hot_skills.items():
        companies_used_skill[skill] = [len(set([c for c in companies if c is not None]))]

    companies_used_skill_df = pd.DataFrame.from_dict(companies_used_skill, orient='index', columns=['Number of Companies']).reset_index()
    companies_used_skill_df = companies_used_skill_df.sort_values(by='Number of Companies', ascending=False).reset_index(drop=True)
    companies_used_skill_df.to_csv(f'{output_path}skill_usage_{title}_{location}_{datetime.datetime.now().strftime("%Y-%m-%d")}.csv', index=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect job postings data from Linkedin."
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default="Software Developer",
        help="Job title to search for.",
    )
    parser.add_argument(
        "-l", "--location", type=str, required=True, help="Location to search in."
    )

    parser.add_argument(
            "--output", 
            default="./results/",
            type=str, help="output path (defualt: ./results/)"
    )
    parser.add_argument(
        "-n",
        "--num_jobs",
        type=int,
        default=600,
        help="Number of job postings to fetch.",
    )

    args = parser.parse_args()
    title = args.title
    location = args.location
    NUMBER_OF_JOBS_TO_FETCH = args.num_jobs
    output_path = args.output

    os.makedirs(output_path, exist_ok=True)  # will dump results here

    search_linkedin_jobs(title, location, NUMBER_OF_JOBS_TO_FETCH, output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
