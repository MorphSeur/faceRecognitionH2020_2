# IAI agent skeleton

This project is a skeleton useful for creating IAI agent used in Analytics 
computation in the framework of E-CORRIDOR.

## Preparation

The IAI agent skeleton is composed by two files:
- server.py : contains the related server code and Analyitcs to implement
- iai_test_client.py : command line program used to invoke the Analytics
as the IAI infrastructure will do.


In order to use the above programs you need to install the required libraries:
```pip install -r requirements.txt```

## Usage

* Prepare a temporary directory used for temporary datalake (eg. /tmp/testiai)
* Put the needed files in that directory 
* Start server ```python server.py``` or via docker (see below)
* Invoke analytics using `iai_test_client.py` command:
```bash
python iai_test_client.py start --datalake /tmp/testiai filename1 filename1...
```


## Developing using docker container

To better simulate running environment, you can run your agent in a docker container.

The following command will create a docker container named `iai_agent`. 
The `/tmp/testiai` directory is the temporary datalake on which your analytics
will found the input files to analyze and where your analytics will put outputs.

```bash
docker run --name iai_agent \
  -v /tmp/testiai/:/tmp/testiai/ \
  -v $(pwd):/app \
  -p 5000:5000  python:3.9 \
  sh /app/docker-entrypoint.sh
```
