import logging
import argparse
from flask import Flask, render_template, Blueprint
from datetime import datetime

from qanary_helpers.configuration import Configuration
from qanary_helpers.registration import Registration
from qanary_helpers.registrator import Registrator

class app:
  def __init__(self, configfile, aboutendpoint, healthendpoint, blueprint):
    base = Blueprint('base', __name__, template_folder='templates')

    @base.route(healthendpoint, methods=['GET'])
    def health():
        """required health endpoint for callback of Spring Boot Admin server"""
        return "alive"
  
    self.app = Flask(__name__)
    self.app.register_blueprint(blueprint)
    self.app.register_blueprint(base)
 
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    # allow configuration of the configfile via command line parameters
    argparser = argparse.ArgumentParser(
        description='You might provide a configuration file, otherwise "%s" is used.' % (configfile))
    argparser.add_argument('-c', '--configfile', action='store', dest='configfile', default=configfile,
                           help='overwrite the default configfile "%s"' % (configfile))
    configfile = argparser.parse_args().configfile
    configuration = Configuration(configfile, [
        'springbootadminserverurl',
        'springbootadminserveruser',
        'springbootadminserverpassword',
        'servicehost',
        'serviceport',
        'servicename',
        'servicedescription',
        'serviceversion'
    ])

    try:
        configuration.serviceport = int(configuration.serviceport)  # ensure an int value for the server port
    except Exception as e:
        logging.error(
            "in configfile '%s': serviceport '%s' is not valid (%s)" % (configfile, configuration.serviceport, e))

    # define metadata that will be shown in the Spring Boot Admin server UI
    metadata = {
        "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": configuration.servicedescription,
        "about": "%s:%d%s" % (configuration.servicehost, configuration.serviceport, aboutendpoint),
        "written in": "Python"
    }

    # initialize the registation object, to be send to the Spring Boot Admin server
    myRegistration = Registration(
        name=configuration.servicename,
        serviceUrl="%s:%d" % (configuration.servicehost, configuration.serviceport), # 
        healthUrl="%s:%d%s" % (configuration.servicehost, configuration.serviceport, healthendpoint), # 
        metadata=metadata
    )

    # start a thread that will contact iteratively the Spring Boot Admin server
    registratorThread = Registrator(
        configuration.springbootadminserverurl,
        configuration.springbootadminserveruser,
        configuration.springbootadminserverpassword,
        myRegistration
    )
    registratorThread.start()

    # start the web service
    self.app.run(host='0.0.0.0', debug=True, threaded=True, port=configuration.serviceport)

  

if __name__ == "__main__":
  configfile = "app.conf"
  aboutendpoint = "/about"
  healthendpoint = "/health"
  from classifier import relation_clf
  blueprint = relation_clf
  app(configfile, aboutendpoint, healthendpoint, blueprint)




  
