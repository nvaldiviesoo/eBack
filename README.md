# eBack

## Commands

- Makemigrations
````
docker compose run --rm app sh -c 'python manage.py makemigrations'
````

- Coverage

````
docker-compose run app sh -c "coverage run --source='.' manage.py test && coverage html"
````

Eso genera el reporte en el contenedor

````
docker cp <container_id>:/app/htmlcov /path/to/local/directory
````

Eso copia la carpeta de coverage al computador local. <containes_id> es el id del contenedor docker que ejecuto la instruccion