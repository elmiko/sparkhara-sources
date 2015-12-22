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

### log count packets

**Request**

    GET /count-packets

**Response**

    200

    {
      "count-packets": {
        "last-received": {
          "count": 0,
          "id": null,
          "service-counts": {
              "<service name>": 0
          }
        },
        "history": [
          {
            "count": 0,
            "ids": [],
            "service-counts": {
                "<service name>": 0
            }
          }
        ]
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

### sorted log lines

**Request**

    GET /sorted-logs?ids={count packet id 1}&...&ids={count packet id n}

**Response**

    200

    {
      "sorted-logs": {
        "lines": []
      }
    }

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

