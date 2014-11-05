1. Copy `config.ini.template` to `config.ini`
2. Edit config.ini and replace YOURTOKEN with the token of the importer user of your HunchLab instance. Change the endpoint too, if necessary.
3. Build the docker image with `sudo docker build -t hunchlab/nola-2014-events .` (requires Docker to be installed)
4. Run your new image: `sudo docker run hunchlab2/nola-2014-events`
