manual_imports_BR = {
    "BR": {
        "InjectionKicker": {
            'Monitor': {
                'ChannelNames': ['BR1_____KI_____AM00'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'HWUnits': [],
                'MemberOf': ['Kicker'],
                'Mode': 'Online',
                'Physics2HWParams': 1,
                'PhysicsUnits': [],
                'Units': 'Hardware'
            },
            'Setpoint': {
                'ChannelNames': ['BR1_____KI_____AC00'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'HWUnits': [],
                'MemberOf': ['Kicker'],
                'Mode': 'Online',
                'Physics2HWParams': 1,
                'PhysicsUnits': [],
                'Range': [0.0, 'inf'],
                'Units': 'Hardware'
            },
            'setup': {
                'CommonNames': ['BR Injection Kicker'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['Kicker'],
                'Position': [0],
                'Status': 1
            }
        },
        "ExtractionKicker": {
            'Monitor': {
                'ChannelNames': ['BR2_____KE_____AM00'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'HWUnits': [],
                'MemberOf': ['Kicker'],
                'Mode': 'Online',
                'Physics2HWParams': 1,
                'PhysicsUnits': [],
                'Units': 'Hardware'
            },
            'Setpoint': {
                'ChannelNames': ['BR2_____KE_____AC00'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'HWUnits': [],
                'MemberOf': ['Kicker'],
                'Mode': 'Online',
                'Physics2HWParams': 1,
                'PhysicsUnits': [],
                'Range': [0.0, 'inf'],
                'Units': 'Hardware'
            },
            'setup': {
                'CommonNames': ['BR Extration Kicker'],
                'DeviceList': [[1, 2]],
                'ElementList': [1],
                'MemberOf': ['Kicker'],
                'Position': [20],
                'Status': 1
            }
        },
        'GammaRad': {
            'Dose1Hour': {
                'ChannelNames': ['BRL1:Gamma:Dose:1Hour', 'BRL2:Gamma:Dose:1Hour', 'BRL5:Gamma:Dose:1Hour', 'BRL6:Gamma:Dose:1Hour', 'BRL7:Gamma:Dose:1Hour'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mrem',
                'PhysicsUnits': 'mrem',
                'MemberOf': ['GammaRad'],
                'Mode': 'Online'
            },
            'Dose7Day': {
                'ChannelNames': ['BRL1:Gamma:Dose:7Day', 'BRL2:Gamma:Dose:7Day', 'BRL5:Gamma:Dose:7Day', 'BRL6:Gamma:Dose:7Day', 'BRL7:Gamma:Dose:7Day'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mrem',
                'PhysicsUnits': 'mrem',
                'MemberOf': ['GammaRad'],
                'Mode': 'Online'
            },
            'Dose14Day': {
                'ChannelNames': ['BRL1:Gamma:Dose:14Day', 'BRL2:Gamma:Dose:14Day', 'BRL5:Gamma:Dose:14Day', 'BRL6:Gamma:Dose:14Day', 'BRL7:Gamma:Dose:14Day'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mrem',
                'PhysicsUnits': 'mrem',
                'MemberOf': ['GammaRad'],
                'Mode': 'Online'
            },
            'Dose24Hour': {
                    'ChannelNames': ['BRL1:Gamma:Dose:24Hour', 'BRL2:Gamma:Dose:24Hour', 'BRL5:Gamma:Dose:24Hour', 'BRL6:Gamma:Dose:24Hour', 'BRL7:Gamma:Dose:24Hour'],
                    'DataType': 'Scalar',
                    'HW2PhysicsParams': 1,
                    'Physics2HWParams': 1,
                    'Units': 'Hardware',
                    'HWUnits': 'mrem',
                    'PhysicsUnits': 'mrem',
                    'MemberOf': ['GammaRad'],
                    'Mode': 'Online'
            },
            'DoseRateInstantaneous': {
                'ChannelNames': ['BRL1:Gamma:DoseRate', 'BRL2:Gamma:DoseRate', 'BRL5:Gamma:DoseRate', 'BRL6:Gamma:DoseRate', 'BRL7:Gamma:DoseRate'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mrem/hr',
                'PhysicsUnits': 'mrem/hr',
                'MemberOf': ['GammaRad'],
                'Mode': 'Online'
            },
            'DoseRateHourlySum': {
                'ChannelNames': ['BRL1:Gamma:DoseRate:Hourly', 'BRL2:Gamma:DoseRate:Hourly', 'BRL5:Gamma:DoseRate:Hourly', 'BRL6:Gamma:DoseRate:Hourly', 'BRL7:Gamma:DoseRate:Hourly'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mrem/hr',
                'PhysicsUnits': 'mrem/hr',
                'MemberOf': ['GammaRad'],
                'Mode': 'Online'
            },
            'DoseRateAvg4Seconds': {
                'ChannelNames': ['BRL1:Gamma:DoseRateAvg:4Seconds', 'BRL2:Gamma:DoseRateAvg:4Seconds', 'BRL5:Gamma:DoseRateAvg:4Seconds', 'BRL6:Gamma:DoseRateAvg:4Seconds', 'BRL7:Gamma:DoseRateAvg:4Seconds'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mrem/hr',
                'PhysicsUnits': 'mrem/hr',
                'MemberOf': ['GammaRad'],
                'Mode': 'Online'
            },
            'DoseRateAvg12Seconds': {
                'ChannelNames': ['BRL1:Gamma:DoseRateAvg:12Seconds', 'BRL2:Gamma:DoseRateAvg:12Seconds', 'BRL5:Gamma:DoseRateAvg:12Seconds', 'BRL6:Gamma:DoseRateAvg:12Seconds', 'BRL7:Gamma:DoseRateAvg:12Seconds'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mrem/hr',
                'PhysicsUnits': 'mrem/hr',
                'MemberOf': ['GammaRad'],
                'Mode': 'Online'
            },
            'DoseRateAvg1Minute': {
                'ChannelNames': ['BRL1:Gamma:DoseRateAvg:1Minute', 'BRL2:Gamma:DoseRateAvg:1Minute', 'BRL5:Gamma:DoseRateAvg:1Minute', 'BRL6:Gamma:DoseRateAvg:1Minute', 'BRL7:Gamma:DoseRateAvg:1Minute'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mrem/hr',
                'PhysicsUnits': 'mrem/hr',
                'MemberOf': ['GammaRad'],
                'Mode': 'Online'
            },
            'DoseRateAvg1Hour': {
                'ChannelNames': ['BRL1:Gamma:DoseRateAvg:1Hour', 'BRL2:Gamma:DoseRateAvg:1Hour', 'BRL5:Gamma:DoseRateAvg:1Hour', 'BRL6:Gamma:DoseRateAvg:1Hour', 'BRL7:Gamma:DoseRateAvg:1Hour'],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mrem/hr',
                'PhysicsUnits': 'mrem/hr',
                'MemberOf': ['GammaRad'],
                'Mode': 'Online'
            },
            'DoseRateMax1Hour': {
                    'ChannelNames': ['BRL1:Gamma:DoseRateMax:1Hour', 'BRL2:Gamma:DoseRateMax:1Hour', 'BRL5:Gamma:DoseRateMax:1Hour', 'BRL6:Gamma:DoseRateMax:1Hour', 'BRL7:Gamma:DoseRateMax:1Hour'],
                    'DataType': 'Scalar',
                    'HW2PhysicsParams': 1,
                    'Physics2HWParams': 1,
                    'Units': 'Hardware',
                    'HWUnits': 'mrem/hr',
                    'PhysicsUnits': 'mrem/hr',
                    'MemberOf': ['GammaRad'],
                    'Mode': 'Online'
            },
            'DoseRateMin1Hour': {
                    'ChannelNames': ['BRL1:Gamma:DoseRateMin:1Hour', 'BRL2:Gamma:DoseRateMin:1Hour', 'BRL5:Gamma:DoseRateMin:1Hour', 'BRL6:Gamma:DoseRateMin:1Hour', 'BRL7:Gamma:DoseRateMin:1Hour'],
                    'DataType': 'Scalar',
                    'HW2PhysicsParams': 1,
                    'Physics2HWParams': 1,
                    'Units': 'Hardware',
                    'HWUnits': 'mrem/hr',
                    'PhysicsUnits': 'mrem/hr',
                    'MemberOf': ['GammaRad'],
                    'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Gamma Radiation'] * 5,
                'DeviceList': [
                    [1, 1], [2, 1], [5, 1], [6, 1], [7, 1]
                ],
                'ElementList': list(range(1, 5)),
                'MemberOf': ['GammaRad']
            }
        },
        "SEK": {
            'Setpoint': {
                'ChannelNames': [
                    "BR2_____SEK____AC01"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'V',
                'PhysicsUnits': 'V',
                'MemberOf': ['Septum', 'Setpoint'],
                'Mode': 'Online'
            },
            'Monitor': {
                'ChannelNames': [
                    "BR2_____SEK____AM02"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'V',
                'PhysicsUnits': 'V',
                'MemberOf': ['Septum', 'Monitor'],
                'Mode': 'Online'
            },
            'SlewRate': {
                'ChannelNames': [
                    "BR2_____SEK____AC31"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'V/s',
                'PhysicsUnits': 'V/s',
                'MemberOf': ['Septum', 'Setpoint'],
                'Mode': 'Online'
            },
            'MaxSlewRate': {
                'ChannelNames': [
                    "BR2_____SEK____AC41"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'V/s',
                'PhysicsUnits': 'V/s',
                'MemberOf': ['Septum'],
                'Mode': 'Online'
            },
            'HVControl': {
                'ChannelNames': [
                    "BR2_____SEK____BC21"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Control'],
                'Mode': 'Online'
            },
            'MagCoverOn': {
                'ChannelNames': [
                    "BR2_____SEK____BM07"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'VacuumOK': {
                'ChannelNames': [
                    "BR2_____SEK____BM08"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'CrashOffOK': {
                'ChannelNames': [
                    "BR2_____SEK____BM09"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'HVReady': {
                'ChannelNames': [
                    "BR2_____SEK____BM10"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'RackAirOK': {
                'ChannelNames': [
                    "BR2_____SEK____BM11"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'RemoteOn': {
                'ChannelNames': [
                    "BR2_____SEK____BM12"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'HVOn': {
                'ChannelNames': [
                    "BR2_____SEK____BM13"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['SEK Septum'],
                'DeviceList': [[2, 1]],
                'ElementList': [1],
                'MemberOf': ['Septum']
            }
        },
        "SEN": {
            'Setpoint': {
                'ChannelNames': [
                    "BR2_____SEN____AC00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'A',
                'PhysicsUnits': 'A',
                'MemberOf': ['Septum', 'Setpoint'],
                'Mode': 'Online'
            },
            'Monitor': {
                'ChannelNames': [
                    "BR2_____SEN____AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'A',
                'PhysicsUnits': 'A',
                'MemberOf': ['Septum', 'Monitor'],
                'Mode': 'Online'
            },
            'SlewRate': {
                'ChannelNames': [
                    "BR2_____SEN____AC30"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'A/s',
                'PhysicsUnits': 'A/s',
                'MemberOf': ['Septum', 'Setpoint'],
                'Mode': 'Online'
            },
            'MaxSlewRate': {
                'ChannelNames': [
                    "BR2_____SEN____AC40"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'A/s',
                'PhysicsUnits': 'A/s',
                'MemberOf': ['Septum'],
                'Mode': 'Online'
            },
            'HVControl': {
                'ChannelNames': [
                    "BR2_____SEN____BC20"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Control'],
                'Mode': 'Online'
            },
            'MagCoverOn': {
                'ChannelNames': [
                    "BR2_____SEN____BM00"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'VacuumOK': {
                'ChannelNames': [
                    "BR2_____SEN____BM01"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'CrashOffOK': {
                'ChannelNames': [
                    "BR2_____SEN____BM02"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'HVReady': {
                'ChannelNames': [
                    "BR2_____SEN____BM03"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'OverTempOK': {
                'ChannelNames': [
                    "BR2_____SEN____BM04"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'RemoteOn': {
                'ChannelNames': [
                    "BR2_____SEN____BM05"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'HVOn': {
                'ChannelNames': [
                    "BR2_____SEN____BM06"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Septum', 'Status'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['SEN Septum'],
                'DeviceList': [[2, 1]],
                'ElementList': [1],
                'MemberOf': ['Septum']
            }
        },
        "ICT": {
            'ChargeStart': {
                'ChannelNames': [
                    "BR:ICT:Charge:Start"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'C',
                'PhysicsUnits': 'C',
                'MemberOf': ['ICT', 'Charge'],
                'Mode': 'Online'
            },
            'ChargeMiddle': {
                'ChannelNames': [
                    "BR:ICT:Charge:Middle"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'C',
                'PhysicsUnits': 'C',
                'MemberOf': ['ICT', 'Charge'],
                'Mode': 'Online'
            },
            'ChargeEnd': {
                'ChannelNames': [
                    "BR:ICT:Charge:End"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'C',
                'PhysicsUnits': 'C',
                'MemberOf': ['ICT', 'Charge'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Integrating Current Transformer'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['ICT']
            }
        },
        "Extraction": {
            'Efficiency': {
                'ChannelNames': [
                    "BR:Extraction:Efficiency"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '%',
                'PhysicsUnits': '%',
                'MemberOf': ['Efficiency'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Extraction'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['Efficiency']
            }
        },
        "Injection": {
            'Efficiency': {
                'ChannelNames': [
                    "BR:Injection:Efficiency"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '%',
                'PhysicsUnits': '%',
                'MemberOf': ['Efficiency'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Injection'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['Efficiency']
            }
        }
    }
}
