from flask import Flask
from flask_restful import Resource, Api
from command import Commander

app = Flask(__name__)
api = Api(app)

PACKETIX_CONNECT_NAME = "c1"


class Packetix(Resource):
    def get(self):
        c = Commander()
        ok, rd, ed = c.vpn_command(" localhost /CLIENT /CMD AccountStatusGet %s" % PACKETIX_CONNECT_NAME)
        return {'result': ok, 'msg': rd, 'error': ed}

    def put(self):
        c = Commander()
        ok, rd, ed = c.vpn_command(" localhost /CLIENT /CMD AccountConnect %s" % PACKETIX_CONNECT_NAME)
        return {'result': ok, 'msg': rd, 'error': ed}


class PPPoE(Resource):
    def get(self):
        c = Commander()
        rd, ed = c.command2("plog")
        return {'result': True, 'msg': rd, 'error': ed}

    def delete(self):
        c = Commander()
        rd, ed = c.command2("poff -a")
        return {'result': True, 'msg': rd, 'error': ed}

    def put(self):
        c = Commander()
        rd, ed = c.command2("pon dsl-priovde")
        return {'result': True, 'msg': rd, 'error': ed}


api.add_resource(Packetix, '/packetix')
api.add_resource(PPPoE, '/pppoe')

if __name__ == '__main__':
    app.run(debug=True)
