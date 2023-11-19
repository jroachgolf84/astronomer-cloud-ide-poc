# Astro Cloud IDE POC

- Author: Jake Roach
- Date: 2023-11-18


## Summary

To illustrates the power of the Astro Cloud IDE, I created a POC using the Astro Cloud IDE to pull a basket of stocks (using the Polygon API), storing these stocks as a DataFrame, and writing them to an RDS endpoint in AWS. This POC leverages a few tools (native to Astro), that I haven’t used in the past:

- Astro Cloud IDE
- Astro Python SDK

This document outlines the steps that I took to build out the project and the pipeline in the Astro Cloud IDE. Enjoy!

## Building out the Pipeline

To create this POC, I used a free trial of Astro Cloud, as well as a free-tier AWS account. I had already had the AWS account spun up, but I don’t think that it took more than 60 seconds get set up in Astro Cloud (impressive). For reference (and I know that the services are different in nature), it took hours for Delaware North to spin up our Databricks workspaces earlier this year…

 It was a little bit weird not using a dedicated deployment, but I created a project that included sample pipelines, so I could get a feel for the experience. Already, I could tell that the use-cases where going to be numerous. This is EXACTLY the kind of tool that Data Scientists and skilled Data Analysts would be drooling over. I thought it was smart to call the processes created and defined in the Cloud IDE “pipelines”, rather than “DAGs”. All data professionals know what a data pipeline. DAGs add an additional layer of complexity that isn’t needed for this type of product.

One of the things that was really easy and neat was storing environment variables. I created a Polygon API token, which I wanted to store as a masked Airflow variable. 30 second later, I was done. I then typed the following code:

```python
import os

POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY")
```

Boom - environment variable securely store. No need to configure AWS Secrets Manager, or another secrets backend.

While I was fishing around in this part of the UI, I also noticed the “Requirements” and “Connection” section - very cool “lite” versions of the same tooling in a traditional Airflow deployment. I added `requests` to the requirements section, and then almost opened a tab to find the version to “pin” the requirement. Before I could, I noticed this was already populated in a drop-down by in the UI. Come on, that’s awesome. When I later added a Postgres cell, the "Requirements" section was updated without a single click. Awesome functionality for non-data engineers looking to build production-grade data pipelines.

I took an ELT approach, so I could use the “Warehouse SQL” and “SQL” cells to transform my data in an RDS endpoint. These were incredibly easy to use, and saved me from having to create custom connectors, which is something that I’ve had to do in the past. Once I had built and tested the SQL cells, I connected a GitHub repo to my project, and committed the work that I had done. The process was easy as it gets, and from end-to-end, the entire project only took about 3 hours. Once the code was committed to GitHub, I paused - one thing thing that I was lucky enough to do with Delaware North was spin up deployments and configure CI/CD (using AWS CodeBuild) for each.

## Lessons Learned

Working in the Astro Cloud IDE was a completely different experience than working in a traditional, managed-Airflow setting. I loved the data science-esque workflow, and the ease of working in an Airflow-lite environment. The coolest part was the process after I had created my pipeline in the IDE; with just a few clicks of a button, I was basically ready to ship my pipeline into an Astronomer deployment. Pretty darn nifty!

One thing that I struggled on was using some of the variables that I rely on when building DAGs in the traditional Airflow environment. For example, I wanted to use the `ds` variable when building URLs for my calls to the Polygon API. However, I couldn’t quite figure this out, even after about an hour on Google.

Once I had wrapped up my `pull_market_data` project, I wanted to remove the “example” pipeline that had been created when I my project. I stumbled around on this, and eventually did it a “backdoor” way. I cloned the repo locally, and removed the DAG-file that had been created in the `dags/` directory. However, while this removed the DAG from my Airflow project, it was still showing in my Astronomer project.