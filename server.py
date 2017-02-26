import cherrypy
import json
import os, os.path
import requests
import redis

from jinja2 import Environment, FileSystemLoader


def get_data():
    response = requests.get("https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/niftyGainers1.json")
    return response


def update_results():
    try:
        response = get_data()

        # Store in redis cache indefinitely
        r.set('results', response.text)

        print("Results Updated! at {}".format(json.loads(response.text)['time']))

    except Exception as er:
        print('Error updating results: {}'.format(er))


class IndexGenerator(object):
    @cherrypy.expose
    def index(self):

        input_data = r.get('results')

        if not input_data:
            response = get_data()

            input_data = json.loads(response.text)

            # Store in redis cache for 5 min
            r.set('results', response.text, 600)
        else:
            input_data = json.loads(str(input_data, 'utf-8'))

        data = {
            'data': input_data['data'],
            'time': input_data['time']
        }

        template = env.get_template('index.html')

        return template.render(**data)


if __name__ == '__main__':
    # Set Jinja template file paths
    env = Environment(loader=FileSystemLoader(os.path.abspath(os.getcwd())))

    # connect to redis
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Get results every 3minutes
    cherrypy.engine.housekeeper = cherrypy.process.plugins.BackgroundTask(3*60, update_results)
    cherrypy.engine.housekeeper.start()

    conf = {
        'global': {
            'server.socket_port': 8080,
        },
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'public'
        }
    }
    cherrypy.quickstart(IndexGenerator(), '/', conf)