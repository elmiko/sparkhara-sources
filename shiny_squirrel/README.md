# shiny squirrel

this is a flask application for displaying some log data

to run this application simply install the requirements and run:

    $ python shiny_squirrel.py

## api

the routes available

### index

**Request**

    GET /

**Response**

a web page with the graph of counts

### totals

**Request**

    GET /totals

**Response**

    200

    {
      "totals": {
        "all": 0
      }
    }

**Request**

    POST /totals

    {
      "totals": {
        "all": 100
      }
    }

**Response**

    200

    {
      "totals": {
        "all": 100
      }
    }
