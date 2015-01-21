# cloudify-byon-service
BYON service, used with the Cloudify BYON plugin

To run service use gunicorn:

    $<virtualenv>/bin/gunicorn -w 2 app:app

To get data by rest API use:

       curl http://localhost:8000/servers/list
       curl http://localhost:8000/servers/list/in_use
       curl http://localhost:8000/servers/list/active

