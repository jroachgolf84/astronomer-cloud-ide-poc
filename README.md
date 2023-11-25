# Astro Cloud IDE POC

- Author: Jake Roach
- Date: 2023-11-18


## Summary

To illustrates the power of the Astro Cloud IDE, I created a POC using the Astro Cloud IDE to pull a basket of stocks 
 (using the Polygon API), store the resulting payload for each stock as a DataFrame, and update a presentation-grade
 table in an RDS endpoint (running in AWS). This POC leverages a few tools (native to Astro), that I haven’t used much 
 in the past:

- Astro Cloud IDE
- Astro Python SDK

This document outlines the requirements for this POC, and the steps that I took to build out the project and the 
 pipeline in the Astro Cloud IDE. Enjoy!

## Requirements
To help shape the scope of this POC, I set the following requirements for this project:

- Must use the Astro Cloud IDE *exclusively* to create a data pipeline
- When buiding the pipeline, a "Python", "Warehouse SQL", and "PostgresOperator" cell will be used 
- The resulting data pipeline must be idempotent and deterministic
- Credentials must be securely stored, without configuring a secrets backend

## Building out the Pipeline

To create this POC, I used a free trial of Astro Cloud, as well as my personal AWS account. After logging in to 
 Astronomer, I don’t think that it took more than 60 seconds get set up in Astro Cloud (impressive). For reference (and
 I know that the services are different in nature), it took more than four hours for Delaware North to spin up our
 Databricks workspaces earlier this year.

It was a little bit weird not having to spin up a deployment, but I created a "Project" that included sample pipelines, 
 so I could get a feel for the Astro Cloud IDE development experience. This is EXACTLY the kind of tool that Data 
 Scientists and skilled Data Analysts would be drooling over. I thought it was smart to call the processes created and 
 defined in the Cloud IDE “pipelines”, rather than “DAGs”. All data professionals know what a data pipeline, while using
 the term "DAGs" adds an additional layer of complexity that isn’t needed for this type of product.

One of the things that was really easy was storing environment variables. I created a Polygon API token, which I wanted 
 to store as a masked Airflow variable. 30 seconds later, I was done. I then typed the following code in a Python cell:

```python
POLYGON_API_KEY: str = Variable.get("POLYGON_API_KEY")
```

Just like that, Airflow variable stored and masked. No need to configure AWS Secrets Manager, or another secrets 
 backend.

While I was fishing around in this part of the UI, I also noticed the “Requirements” and “Connection” section - very 
 cool “lite” versions of the same tooling in a traditional Airflow deployment. I added `requests` to the requirements 
 section, and then almost opened a web-browser tab to find the version to “pin” the requirement. Before I could, I 
 noticed this was already populated in a drop-down by in the UI. Come on, that’s awesome. When I later added a Postgres 
 cell, the "Requirements" section was updated without a single click. Awesome functionality for non-data engineers 
 looking to build production-grade data pipelines.

For this basic POC, I took an ELT approach, so I could use both a “Warehouse SQL” and “PostgresOperator” cells to store 
 and transform my data in an RDS endpoint. These were incredibly easy to use, and the mix of the Astro Python SDK
 tooling and traditional operators was seamless. Once I had built and tested the SQL cells, I connected a GitHub repo to
 my project, and committed the work that I had done. The process was easy as it gets, and from end-to-end, the entire
 project only took about 3 hours.

## Lessons Learned

Working in the Astro Cloud IDE was a completely different experience than working in a traditional, managed-Airflow
 setting. I loved the data science-esque workflow, and the ease of working in an Airflow-lite environment. One of my
 favorite parts was the "porting" of the Cloud IDE notebook to a DAG definition; with just a few clicks of a button, I
 was basically ready to ship my pipeline into an Astronomer deployment. Pretty darn nifty!

One thing that I struggled on was using some of the templated fields that I rely on when building DAGs in the
 traditional Airflow environment. For example, I wanted to use the templated `ds` field when building URLs for my calls 
 to the Polygon API. However, I couldn’t quite figure out how to retrieve this field using tools *exclusively in the
 Cloud IDE using a "Python" cell*, which was one of the requirements I set early in this POC. Instead, I mocked this
 value using an Airflow variable, with name `DS`. I then referenced this variable throughout the pipeline. I'd like to
 take a closer look at this, and maybe even contribute to Astronomer's documentation once a solution is implemented.

Once I had wrapped up my `pull_market_data` project, I wanted to remove the example pipeline that had been created when
 I instantiated my project. I stumbled around on this, and eventually did it in a “backdoor” manner. I cloned the repo
 locally, and removed the DAG-file that had been created in the `dags/` directory. However, while this removed the DAG
 from my Airflow project, it was still showing in my Astronomer project.

## Updates

Once the Astro Cloud IDE has been used to create the initial `.py` file to instantiate the DAG, I went ahead and created
 a deployment. I cloned the repo locally (and, since the Astro CLI was already installed), I went ahead and got my
 environment running locally. There were a few changes that I needed to make before I could deploy this repo to Astro:

- Update the Variables and Connections in my local development environment
- Refactor my DAG definitions to properly use the `ds` templated field
- Configure and create an Astro deployment
- Deploy my repo using the Astro CLI
- Update the Variables and Connection in my Astro deployment
- Configure CI/CD with GitHub Actions

In this section, I'll outline the steps that I took and the commands that ran to accomplish each step listed above.

### Update the Variables and Connections in my local development environment
There are two variables that initially needed to be created to get my DAGs up and running locally. The first is the
 `POlYGON_API_KEY`, Variable which is a masked field. The other is the `DS` Variable which "mocks" the `ds` templated
 field (this Variable will eventually be replaced when the DAGs are refactored to use the templated field in the
 appropriate manner). This was done, locally, with the following commands:

```commandline
astro dev run variables list
astro dev run variables set POLYGON_API_KEY *****
astro dev run variables get POLYGON_API_KEY
```

```commandline
astro dev run variables list
astro dev run variables set DS 2023-11-17
astro dev run variables get DS
```

To create the connection to the RDS (Postgres instance) used throughout the DAG, the following CLI commands where run:

```commandline
astro dev run connections list
astro dev run connections add \
    --conn-type postgres \
    --conn-host jroachgolf84-sandbox-postgres.ciz3ssohle2n.us-east-1.rds.amazonaws.com \
    --conn-login jroachgolf84 \
    --conn-password 'Jr355641!!' \
    --conn-port 5432 \
    --conn-schema postgres \
    jroachgolf84-sandbox-postgres
astro dev run connections list -o plain
```


