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

### log count packets

**Request**

    GET /count-packets

**Response**

    200

    {
      "count-packets": {
        "last-received": {
          "count": 0,
          "id": null
        }
      }
    }

**Request**

    POST /count-packets

    {
      "id": null,
      "count": 0
    }

**Response**

    201

    {
      "count-packets": {
        "last-received": {
          "count": 0,
          "id": null
        }
        "since-last-get": {
          "count": 0,
          "ids": []
        }
      }
    }

**Request**

    GET /count-packets/{packet_id}

**Response**

    200

    {
      "count-packet": {
        "id": null,
        "logs": []
      }
    }
