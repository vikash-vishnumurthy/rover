from datas import Datas
from flask import Flask, g
from flask_restful import Api, Resource, reqparse, abort

ROWS = [0,1,2,3]
COLUMNS = [0,1,2,3]
COUNT = [i for i in range(1,11)]

app = Flask(__name__)
api = Api(app)

## args validation ##
rover_move_agrs = reqparse.RequestParser()
rover_move_agrs.add_argument('direction',type=str, help='Direction is required',required=True)

patch_args = reqparse.RequestParser()
patch_args.add_argument('solar-flare',type=str, help='True or False')
patch_args.add_argument('storm',type=str, help = 'True or False')
patch_args.add_argument('humidity', type=int, help= 'Humidity Value')
patch_args.add_argument('temperature',type=int, help='Temperature Value')

env_args = reqparse.RequestParser()
env_args.add_argument('solar-flare',type=str, help='True or False required',required=True)
env_args.add_argument('storm',type=str, help = 'True or False required',required=True)
env_args.add_argument('humidity', type=int, help= 'Humidity Value required',required=True)
env_args.add_argument('temperature',type=int, help='Temperature Value required',required=True)

battery_args = reqparse.RequestParser()
battery_args.add_argument('value',type=int,help='Battery value required', required=True)
battery_args.add_argument(
    'operator',type=str, 
    help='Operator value required, valid values are lte, gte, lt, gt, ne, eq', 
    required=True,
    choices= ('lte','gte','lt','gt', 'ne','eq')
    )

action_args = reqparse.RequestParser()
action_args.add_argument(
    'name',
    type=str,
    required = True,
    help='Value required. Valid values are water-sample, dust-sample, strom-encounter',
    choices = ('water-sample','dust-sample', 'strom-encounter')
    )


DATA = Datas(x=0,y=0)

## Abort Methods ##

def out_of_map_abort(move,index):
    x_axis = DATA.status['rover']['location']['row']
    y_axis = DATA.status['rover']['location']['column']
    message = f'Your move was out of the map \n Current Location is {x_axis},{y_axis}'

    if move == 'right' or move == 'left':
        if index not in COLUMNS:
            abort(428,message=message)

    if move == 'up' or move == 'down':
        if index not in ROWS:
            abort(428,message=message)

    return True


## Resources ##

class Status (Resource):

    def get(self):
        return DATA.status

class Move (Resource):

    def post(self):
        direction = dict(rover_move_agrs.parse_args())

        if DATA.battery['value'] < 3:
            abort(428,message='Warning low battery!!, Wait for the solar-flare to recharge. Allowed Actions : collect-sample')

        if not DATA.status['environment']['storm']:

            if len(COUNT)==0:
                DATA.battery['value'] = 10
                DATA.update_battery_status()
                COUNT.extend([i for i in range(1,11)])

            if direction['direction'] == 'right':
                out_of_map_abort(direction['direction'], DATA.status['rover']['location']['column']+1)
                DATA.status['rover']['location']['column']+=1
                COUNT.pop()
            elif direction['direction'] == 'left':
                out_of_map_abort(direction['direction'], DATA.status['rover']['location']['column']-1)
                DATA.status['rover']['location']['column']-=1
                COUNT.pop()
            elif direction['direction'] == 'up':
                out_of_map_abort(direction['direction'], DATA.status['rover']['location']['row']-1)
                DATA.status['rover']['location']['row']-=1
                COUNT.pop()
            elif direction['direction'] == 'down':
                out_of_map_abort(direction['direction'], DATA.status['rover']['location']['row']+1)
                DATA.status['rover']['location']['row']+=1
                COUNT.pop()
            else:
                abort('Invalid directions \n Valid directions are right, left, up, down')

        else:
            abort(428,message='Cannot move during a storm')
        
        DATA.battery['value'] -=1
        DATA.update_battery_status()
        return DATA.status

class Environment(Resource):

    def patch(self):
        patch_vars = dict(patch_args.parse_args())

        for var in patch_vars:
            if patch_vars[var] !=None:
                if str(patch_vars[var]).lower() == 'true':
                    DATA.environment[var] = True
                elif str(patch_vars[var]).lower() == 'false':
                    DATA.environment[var] = False
                else:
                    DATA.environment[var] = patch_vars[var]
        if DATA.environment['solar-flare'] == True:
            DATA.battery['value'] = 10
            DATA.update_battery_status()
            COUNT.clear()
            COUNT.extend([i for i in range(1,11)])

        DATA.update_environment_status()

        return {
            'message' : 'Environment Status updated'
        }

class EnvironmentConfigure(Resource):
    
    def post(self):

        env_vars = dict(env_args.parse_args())

        for var in env_vars:
            if env_vars[var] !=None:
                if str(env_vars[var]).lower() == 'true':
                    DATA.environment[var] = True
                elif str(env_vars[var]).lower() == 'false':
                    DATA.environment[var] = False
                else:
                    DATA.environment[var] = env_vars[var]

        DATA.update_environment_status()

        return {
            'message' : 'Environment Status updated'
        }
class RoverConfigure_battery(Resource):

    def post(self):

        battery_vars = dict(battery_args.parse_args())

        for var in battery_vars:
            DATA.battery[var]= battery_vars[var]

        DATA.update_battery_status()

        return {
            'message' : 'Battery Status Updates'
        }

class RoverAction(Resource):

    def post(self):
        action_vars = dict(action_args.parse_args())
        actions = [ name['type'] for name in DATA.status['rover']['inventory'] ]

        if action_vars['name'] == 'water-sample':
            if action_vars['name'] not in actions:
                new_name = {
                    'type' : 'water-sample',
                    'quantity': 1,
                    'priority': 2
                }
                DATA.status['rover']['inventory'].append(new_name)
            else:
                for i in DATA.status['rover']['inventory']:
                    if i['type'] == 'water-sample':
                        i['quantity']+=1

        if action_vars['name'] == 'dust-sample':
            if action_vars['name'] not in actions:
                new_name = {
                    'type' : 'dust-sample',
                    'quantity': 1,
                    'priority': 2
                }
                DATA.status['rover']['inventory'].append(new_name)
            else:
                for i in DATA.status['rover']['inventory']:
                    if i['type'] == 'dust-sample':
                        i['quantity']+=1

        if action_vars['name'] == 'strom-encounter':
          
            for i in DATA.status['rover']['inventory']:
                if i['type'] == 'storm-shield':
                    if i['quantity'] >0:
                        i['quantity']-=1
                    else:
                        abort(428,message='No strom shields to protect from strom')

        return {
            'message' : 'Action done'
        }
            

api.add_resource(Status,'/api/rover/status')
api.add_resource(Move,'/api/rover/move')
api.add_resource(Environment,'/api/environment')
api.add_resource(EnvironmentConfigure,'/api/environment/configure')
api.add_resource(RoverConfigure_battery,'/api/rover/configure/battery')
api.add_resource(RoverAction,'/api/rover/action')

if __name__ == "__main__":
    app.run(debug = True)