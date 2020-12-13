class Datas():

    def __init__(self,x,y):

        self.environment = {
            'temperature' : 60,
            'humidity' : 65,
            'solar-flare': False,
            'storm' : False,
            'area-map': [
                ['dirt','water','dirt','water'],
                ['dirt','water','dirt','water'],
                ['dirt','water','dirt','water'],
                ['dirt','water','dirt','water']
            ] 
        }

        self.battery = {
            'operator' : 'lte',
            'value' : 11
        }
      
        self.status = {
            'rover' : {
                'location': {
                    'row' : x,
                    'column': y
                },
            
                'battery' : self.battery['value'],
                'inventory' : [
                    {
                        'type' : 'storm-shield',
                        'quantity': 10,
                        'priority':1
                    }
                ] 
            },
            'environment' : {
                'temperature' : self.environment['temperature'],
                'humidity' : self.environment['humidity'],
                'solar-flare' : self.environment['solar-flare'],
                'storm' : self.environment['storm'],
                'terrain' : 'dirt'
            }
        }
    def update_environment_status(self):
            self.status['environment']['temperature'] = self.environment['temperature']
            self.status['environment']['humidity'] = self.environment['humidity']
            self.status['environment']['solar-flare'] = self.environment['solar-flare']
            self.status['environment']['storm'] = self.environment['storm']

    def update_battery_status(self):
        self.status['rover']['battery'] = self.battery['value']