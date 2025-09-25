manual_imports_SR = {
    "SR": {
        "Injection": {
            'Efficiency': {
                'ChannelNames': [
                    "SR:Injection:Efficiency",
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '%',
                'PhysicsUnits': '%',
                'MemberOf': ['NA'],
                'Mode': 'Online'
            },
            'Charge': {
                'ChannelNames': [
                    "SR:Injection:Charge",
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'C',
                'PhysicsUnits': 'C',
                'MemberOf': ['NA'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Injection'],
                'DeviceList': [[1, 1]],
                'ElementList': list(range(1, 1)),
                'MemberOf': ['NA']
            }
        },
        "TunnelAirTemperature": {
            'Monitor': {
                'ChannelNames': [
                    "SR01C___T______AM00",
                    "SR03C___T______AM00",
                    "SR04C___T______AM00", 
                    "SR06C___T______AM00",
                    "SR07C___T______AM00",
                    "SR08C___T______AM00", 
                    "SR09C___T______AM00",
                    "SR11C___T______AM00", 
                    "SR12C___T______AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'C',
                'PhysicsUnits': 'C',
                'MemberOf': ['NA'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Tunnel Temperature'],
                'DeviceList': [[1, 1], [3, 1], [4, 1], [6, 1], [7, 1], [8, 1], [9, 1], [11, 1], [12, 1]],
                'ElementList': list(range(1, 10)),
                'MemberOf': ['TunnelAirTemperature']
            }
        },
        "AirHandlingUnit": {
            'ChilledWaterValve': {
                'ChannelNames': [
                    "SR01C___AH6WV__AM00",  # AHU21 SR02
                    "SR03C___AH7WV__AM00",  # AHU22 SR04
                    "SR04C___AH8WV__AM00",  # AHU23 SR05
                    "SR06C___AH9WV__AM00",  # AHU24 SR06
                    "SR12C___AH5WV__AM00"   # AHU20 SR01
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '%',
                'PhysicsUnits': '%',
                'MemberOf': ['NA'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Air Handling Unit'],
                'DeviceList': [[1, 1], [3, 1], [4, 1], [6, 1], [12, 1]],
                'ElementList': list(range(1, 6)),
                'MemberOf': ['AHU']
            }
        },
        "BuildingUtilities": {
            'ChilledWaterSupplyB34': {
                'ChannelNames': [
                    "34______CHWS___AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'C',
                'PhysicsUnits': 'C',
                'MemberOf': ['NA'],
                'Mode': 'Online'
            },
            'TowerWaterFlow': {
                'ChannelNames': [
                    "B37_CW_FLWT____AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'L/min',
                'PhysicsUnits': 'L/min',
                'MemberOf': ['NA'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Building Utilities'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['BuildingUtilities']
            }
        },
        "TUNE": {
            "X_TransverseFeedBack": {
                "ChannelNames": [
                    "IGPF:TFBX:SRAM:PEAKTUNE1",
                ]
            },
            "Y_TransverseFeedBack": {
                "ChannelNames": [
                    "IGPF:TFBY:SRAM:PEAKTUNE1",
                ]
            },
            "X_TurnByTurn": {
                "ChannelNames": [
                    "Topoff_nux_AM",
                ]
            },
            "Y_TurnByTurn": {
                "ChannelNames": [
                    "Topoff_nuy_AM",
                ]
            },
            "X_FeedbackDelta": {
                "ChannelNames": [
                    "SR:Tune:FB:dNuX"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '',
                'PhysicsUnits': '',
                'MemberOf': ['TUNE', 'Feedback', 'Delta', 'Monitor'],
                'Mode': 'Online'
            },
            "Y_FeedbackDelta": {
                "ChannelNames": [
                    "SR:Tune:FB:dNuY"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '',
                'PhysicsUnits': '',
                'MemberOf': ['TUNE', 'Feedback', 'Delta', 'Monitor'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Tune System'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['TUNE']
            }
        },
        "BeamSize": {
            'X_10Hz_Beamline31': {
                'ChannelNames': ['beamline31:XRMSAve'],
                'DataType': 'Scalar',
                'MemberOf': ['PlotFamily'],
                'Mode': 'Online',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'HWUnits': [],
                'PhysicsUnits': 'um',
                'Units': 'Hardware'
            },
            'X_1HZ_Beamline31': {
                'ChannelNames': ['beamline31:XRMSAve_1HZ'],
                'DataType': 'Scalar',
                'MemberOf': ['PlotFamily'],
                'Mode': 'Online',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'HWUnits': [],
                'PhysicsUnits': 'um',
                'Units': 'Hardware'
            },
            'Y_10Hz_Beamline31': {
                'ChannelNames': ['beamline31:YRMSAve'],
                'DataType': 'Scalar',
                'MemberOf': ['PlotFamily'],
                'Mode': 'Online',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'HWUnits': [],
                'PhysicsUnits': 'um',
                'Units': 'Hardware'
            },
            'Y_1HZ_Beamline31': {
                'ChannelNames': ['beamline31:YRMSAve_1HZ'],
                'DataType': 'Scalar',
                'MemberOf': ['PlotFamily'],
                'Mode': 'Online',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'HWUnits': [],
                'PhysicsUnits': 'um',
                'Units': 'Hardware'
            },
            'X_10Hz_Beamline72': {
                'ChannelNames': ['bl72:XRMSAve'],
                'DataType': 'Scalar',
                'MemberOf': ['PlotFamily'],
                'Mode': 'Online',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'HWUnits': [],
                'PhysicsUnits': 'um',
                'Units': 'Hardware'
            },
            'Y_10Hz_Beamline72': {
                'ChannelNames': ['bl72:YRMSAve'],
                'DataType': 'Scalar',
                'MemberOf': ['PlotFamily'],
                'Mode': 'Online',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'HWUnits': [],
                'PhysicsUnits': 'um',
                'Units': 'Hardware'
            },
        },
        'DCCT': {
            'Monitor': {
                'MemberOf': ['DCCT', 'Beam Current', 'Monitor', 'Archive'],
                'Mode': 'Online',
                'DataType': 'Scalar',
                'ChannelNames': 'SR:DCCT',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mA',
                'PhysicsUnits': 'mA'
            }
        },

        'EPBI_TC_UP': {
            'Monitor': {
                'ChannelNames': [
                    "SR02S___TCUP0__AM", "SR02S___TCUP1__AM", "SR02S___TCUP2__AM", "SR02S___TCUP3__AM", "SR02S___TCUP4__AM",
                    "SR02S___TCUP5__AM", "SR02S___TCUP6__AM", "SR02S___TCUP7__AM", "SR02S___TCUP8__AM", "SR02S___TCUP9__AM",
                    "SR04S___TCUP9__AM", "SR05W___TCUP0__AM", "SR05W___TCUP1__AM", "SR05W___TCUP2__AM", "SR05W___TCUP3__AM",
                    "SR05W___TCUP4__AM", "SR05W___TCUP5__AM", "SR05W___TCUP6__AM", "SR05W___TCUP7__AM", "SR05W___TCUP8__AM",
                    "SR05W___TCUP9__AM", "SR06S___TCUP0__AM", "SR06S___TCUP1__AM", "SR06S___TCUP2__AM", "SR06S___TCUP3__AM",
                    "SR06S___TCUP4__AM", "SR06S___TCUP5__AM", "SR06S___TCUP6__AM", "SR06S___TCUP7__AM", "SR06S___TCUP8__AM",
                    "SR06S___TCUP9__AM", "SR07S___TCUP0__AM", "SR07S___TCUP1__AM", "SR07S___TCUP2__AM", "SR07S___TCUP3__AM",
                    "SR07S___TCUP4__AM", "SR07S___TCUP5__AM", "SR07S___TCUP6__AM", "SR07S___TCUP7__AM", "SR07S___TCUP8__AM",
                    "SR07S___TCUP9__AM", "SR08S___TCUP0__AM", "SR08S___TCUP1__AM", "SR08S___TCUP2__AM", "SR08S___TCUP3__AM",
                    "SR08S___TCUP4__AM", "SR08S___TCUP5__AM", "SR08S___TCUP6__AM", "SR08S___TCUP7__AM", "SR08S___TCUP8__AM",
                    "SR08S___TCUP9__AM", "SR09S___TCUP0__AM", "SR09S___TCUP1__AM", "SR09S___TCUP2__AM", "SR09S___TCUP3__AM",
                    "SR09S___TCUP4__AM", "SR09S___TCUP5__AM", "SR09S___TCUP6__AM", "SR09S___TCUP7__AM", "SR09S___TCUP8__AM",
                    "SR09S___TCUP9__AM", "SR10S___TCUP0__AM", "SR10S___TCUP1__AM", "SR10S___TCUP2__AM", "SR10S___TCUP3__AM",
                    "SR10S___TCUP4__AM", "SR10S___TCUP5__AM", "SR10S___TCUP6__AM", "SR10S___TCUP7__AM", "SR10S___TCUP8__AM",
                    "SR10S___TCUP9__AM", "SR11S___TCUP0__AM", "SR11S___TCUP1__AM", "SR11S___TCUP2__AM", "SR11S___TCUP3__AM",
                    "SR11S___TCUP4__AM", "SR11S___TCUP5__AM", "SR11S___TCUP6__AM", "SR11S___TCUP7__AM", "SR11S___TCUP8__AM",
                    "SR11S___TCUP9__AM", "SR12S___TCUP0__AM", "SR12S___TCUP1__AM", "SR12S___TCUP2__AM", "SR12S___TCUP3__AM",
                    "SR12S___TCUP4__AM", "SR12S___TCUP5__AM", "SR12S___TCUP6__AM", "SR12S___TCUP7__AM", "SR12S___TCUP8__AM",
                    "SR12S___TCUP9__AM"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '°C',
                'PhysicsUnits': '°C',
                'MemberOf': ['Thermocouples', 'Temperature', 'Monitor'],
                'Mode': 'Online'
            },
            'Limit': {
                'ChannelNames': [
                    "SR02S___TCUP0__limit", "SR02S___TCUP1__limit", "SR02S___TCUP2__limit", "SR02S___TCUP3__limit", "SR02S___TCUP4__limit",
                    "SR02S___TCUP5__limit", "SR02S___TCUP6__limit", "SR02S___TCUP7__limit", "SR02S___TCUP8__limit", "SR02S___TCUP9__limit",
                    "SR04S___TCUP9__limit", "SR05W___TCUP0__limit", "SR05W___TCUP1__limit", "SR05W___TCUP2__limit", "SR05W___TCUP3__limit",
                    "SR05W___TCUP4__limit", "SR05W___TCUP5__limit", "SR05W___TCUP6__limit", "SR05W___TCUP7__limit", "SR05W___TCUP8__limit",
                    "SR05W___TCUP9__limit", "SR06S___TCUP0__limit", "SR06S___TCUP1__limit", "SR06S___TCUP2__limit", "SR06S___TCUP3__limit",
                    "SR06S___TCUP4__limit", "SR06S___TCUP5__limit", "SR06S___TCUP6__limit", "SR06S___TCUP7__limit", "SR06S___TCUP8__limit",
                    "SR06S___TCUP9__limit", "SR07S___TCUP0__limit", "SR07S___TCUP1__limit", "SR07S___TCUP2__limit", "SR07S___TCUP3__limit",
                    "SR07S___TCUP4__limit", "SR07S___TCUP5__limit", "SR07S___TCUP6__limit", "SR07S___TCUP7__limit", "SR07S___TCUP8__limit",
                    "SR07S___TCUP9__limit", "SR08S___TCUP0__limit", "SR08S___TCUP1__limit", "SR08S___TCUP2__limit", "SR08S___TCUP3__limit",
                    "SR08S___TCUP4__limit", "SR08S___TCUP5__limit", "SR08S___TCUP6__limit", "SR08S___TCUP7__limit", "SR08S___TCUP8__limit",
                    "SR08S___TCUP9__limit", "SR09S___TCUP0__limit", "SR09S___TCUP1__limit", "SR09S___TCUP2__limit", "SR09S___TCUP3__limit",
                    "SR09S___TCUP4__limit", "SR09S___TCUP5__limit", "SR09S___TCUP6__limit", "SR09S___TCUP7__limit", "SR09S___TCUP8__limit",
                    "SR09S___TCUP9__limit", "SR10S___TCUP0__limit", "SR10S___TCUP1__limit", "SR10S___TCUP2__limit", "SR10S___TCUP3__limit",
                    "SR10S___TCUP4__limit", "SR10S___TCUP5__limit", "SR10S___TCUP6__limit", "SR10S___TCUP7__limit", "SR10S___TCUP8__limit",
                    "SR10S___TCUP9__limit", "SR11S___TCUP0__limit", "SR11S___TCUP1__limit", "SR11S___TCUP2__limit", "SR11S___TCUP3__limit",
                    "SR11S___TCUP4__limit", "SR11S___TCUP5__limit", "SR11S___TCUP6__limit", "SR11S___TCUP7__limit", "SR11S___TCUP8__limit",
                    "SR11S___TCUP9__limit", "SR12S___TCUP0__limit", "SR12S___TCUP1__limit", "SR12S___TCUP2__limit", "SR12S___TCUP3__limit",
                    "SR12S___TCUP4__limit", "SR12S___TCUP5__limit", "SR12S___TCUP6__limit", "SR12S___TCUP7__limit", "SR12S___TCUP8__limit",
                    "SR12S___TCUP9__limit"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '°C',
                'PhysicsUnits': '°C',
                'MemberOf': ['Thermocouples', 'Temperature'],
                'Mode': 'Online'
            },
            'Overtemp_flag': {
                'ChannelNames': [
                    "SR02S___TCUP0__BM", "SR02S___TCUP1__BM", "SR02S___TCUP2__BM", "SR02S___TCUP3__BM", "SR02S___TCUP4__BM",
                    "SR02S___TCUP5__BM", "SR02S___TCUP6__BM", "SR02S___TCUP7__BM", "SR02S___TCUP8__BM", "SR02S___TCUP9__BM",
                    "SR04S___TCUP9__BM", "SR05W___TCUP0__BM", "SR05W___TCUP1__BM", "SR05W___TCUP2__BM", "SR05W___TCUP3__BM",
                    "SR05W___TCUP4__BM", "SR05W___TCUP5__BM", "SR05W___TCUP6__BM", "SR05W___TCUP7__BM", "SR05W___TCUP8__BM",
                    "SR05W___TCUP9__BM", "SR06S___TCUP0__BM", "SR06S___TCUP1__BM", "SR06S___TCUP2__BM", "SR06S___TCUP3__BM",
                    "SR06S___TCUP4__BM", "SR06S___TCUP5__BM", "SR06S___TCUP6__BM", "SR06S___TCUP7__BM", "SR06S___TCUP8__BM",
                    "SR06S___TCUP9__BM", "SR07S___TCUP0__BM", "SR07S___TCUP1__BM", "SR07S___TCUP2__BM", "SR07S___TCUP3__BM",
                    "SR07S___TCUP4__BM", "SR07S___TCUP5__BM", "SR07S___TCUP6__BM", "SR07S___TCUP7__BM", "SR07S___TCUP8__BM",
                    "SR07S___TCUP9__BM", "SR08S___TCUP0__BM", "SR08S___TCUP1__BM", "SR08S___TCUP2__BM", "SR08S___TCUP3__BM",
                    "SR08S___TCUP4__BM", "SR08S___TCUP5__BM", "SR08S___TCUP6__BM", "SR08S___TCUP7__BM", "SR08S___TCUP8__BM",
                    "SR08S___TCUP9__BM", "SR09S___TCUP0__BM", "SR09S___TCUP1__BM", "SR09S___TCUP2__BM", "SR09S___TCUP3__BM",
                    "SR09S___TCUP4__BM", "SR09S___TCUP5__BM", "SR09S___TCUP6__BM", "SR09S___TCUP7__BM", "SR09S___TCUP8__BM",
                    "SR09S___TCUP9__BM", "SR10S___TCUP0__BM", "SR10S___TCUP1__BM", "SR10S___TCUP2__BM", "SR10S___TCUP3__BM",
                    "SR10S___TCUP4__BM", "SR10S___TCUP5__BM", "SR10S___TCUP6__BM", "SR10S___TCUP7__BM", "SR10S___TCUP8__BM",
                    "SR10S___TCUP9__BM", "SR11S___TCUP0__BM", "SR11S___TCUP1__BM", "SR11S___TCUP2__BM", "SR11S___TCUP3__BM",
                    "SR11S___TCUP4__BM", "SR11S___TCUP5__BM", "SR11S___TCUP6__BM", "SR11S___TCUP7__BM", "SR11S___TCUP8__BM",
                    "SR11S___TCUP9__BM", "SR12S___TCUP0__BM", "SR12S___TCUP1__BM", "SR12S___TCUP2__BM", "SR12S___TCUP3__BM",
                    "SR12S___TCUP4__BM", "SR12S___TCUP5__BM", "SR12S___TCUP6__BM", "SR12S___TCUP7__BM", "SR12S___TCUP8__BM",
                    "SR12S___TCUP9__BM"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Thermocouples'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['TC Upper'] * 91,
                'DeviceList': [
                    [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8], [2, 9], [2, 10],
                    [4, 10], [5, 1], [5, 2], [5, 3], [5, 4], [5, 5], [5, 6], [5, 7], [5, 8], [5, 9],
                    [5, 10], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6], [6, 7], [6, 8], [6, 9],
                    [6, 10], [7, 1], [7, 2], [7, 3], [7, 4], [7, 5], [7, 6], [7, 7], [7, 8], [7, 9],
                    [7, 10], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [8, 7], [8, 8], [8, 9],
                    [8, 10], [9, 1], [9, 2], [9, 3], [9, 4], [9, 5], [9, 6], [9, 7], [9, 8], [9, 9],
                    [9, 10], [10, 1], [10, 2], [10, 3], [10, 4], [10, 5], [10, 6], [10, 7], [10, 8], [10, 9],
                    [10, 10], [11, 1], [11, 2], [11, 3], [11, 4], [11, 5], [11, 6], [11, 7], [11, 8], [11, 9],
                    [11, 10], [12, 1], [12, 2], [12, 3], [12, 4], [12, 5], [12, 6], [12, 7], [12, 8], [12, 9],
                    [12, 10]
                ],
                'ElementList': list(range(1, 92)),
                'MemberOf': ['Thermocouples']
            },
        },
        'EPBI_TC_DOWN': {
            'Monitor': {
                'ChannelNames': [
                    "SR02S___TCDN0__AM", "SR02S___TCDN1__AM", "SR02S___TCDN2__AM", "SR02S___TCDN3__AM", "SR02S___TCDN4__AM",
                    "SR02S___TCDN5__AM", "SR02S___TCDN6__AM", "SR02S___TCDN7__AM", "SR02S___TCDN8__AM", "SR02S___TCDN9__AM",
                    "SR05W___TCDN0__AM", "SR05W___TCDN1__AM", "SR05W___TCDN2__AM", "SR05W___TCDN3__AM", "SR05W___TCDN4__AM",
                    "SR05W___TCDN5__AM", "SR05W___TCDN6__AM", "SR05W___TCDN7__AM", "SR05W___TCDN8__AM", "SR05W___TCDN9__AM",
                    "SR06S___TCDN0__AM", "SR06S___TCDN1__AM", "SR06S___TCDN2__AM", "SR06S___TCDN3__AM", "SR06S___TCDN4__AM",
                    "SR06S___TCDN5__AM", "SR06S___TCDN6__AM", "SR06S___TCDN7__AM", "SR06S___TCDN8__AM", "SR06S___TCDN9__AM",
                    "SR07S___TCDN0__AM", "SR07S___TCDN1__AM", "SR07S___TCDN2__AM", "SR07S___TCDN3__AM", "SR07S___TCDN4__AM",
                    "SR07S___TCDN5__AM", "SR07S___TCDN6__AM", "SR07S___TCDN7__AM", "SR07S___TCDN8__AM", "SR07S___TCDN9__AM",
                    "SR08S___TCDN0__AM", "SR08S___TCDN1__AM", "SR08S___TCDN2__AM", "SR08S___TCDN3__AM", "SR08S___TCDN4__AM",
                    "SR08S___TCDN5__AM", "SR08S___TCDN6__AM", "SR08S___TCDN7__AM", "SR08S___TCDN8__AM", "SR08S___TCDN9__AM",
                    "SR09S___TCDN0__AM", "SR09S___TCDN1__AM", "SR09S___TCDN2__AM", "SR09S___TCDN3__AM", "SR09S___TCDN4__AM",
                    "SR09S___TCDN5__AM", "SR09S___TCDN6__AM", "SR09S___TCDN7__AM", "SR09S___TCDN8__AM", "SR09S___TCDN9__AM",
                    "SR10S___TCDN0__AM", "SR10S___TCDN1__AM", "SR10S___TCDN2__AM", "SR10S___TCDN3__AM", "SR10S___TCDN4__AM",
                    "SR10S___TCDN5__AM", "SR10S___TCDN6__AM", "SR10S___TCDN7__AM", "SR10S___TCDN8__AM", "SR10S___TCDN9__AM",
                    "SR11S___TCDN0__AM", "SR11S___TCDN1__AM", "SR11S___TCDN2__AM", "SR11S___TCDN3__AM", "SR11S___TCDN4__AM",
                    "SR11S___TCDN5__AM", "SR11S___TCDN6__AM", "SR11S___TCDN7__AM", "SR11S___TCDN8__AM", "SR11S___TCDN9__AM",
                    "SR12S___TCDN0__AM", "SR12S___TCDN1__AM", "SR12S___TCDN2__AM", "SR12S___TCDN3__AM", "SR12S___TCDN4__AM",
                    "SR12S___TCDN5__AM", "SR12S___TCDN6__AM", "SR12S___TCDN7__AM", "SR12S___TCDN8__AM", "SR12S___TCDN9__AM"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '°C',
                'PhysicsUnits': '°C',
                'MemberOf': ['Thermocouples', 'Temperature', 'Monitor'],
                'Mode': 'Online'
            },
            'Limit': {
                'ChannelNames': [
                    "SR02S___TCDN0__limit", "SR02S___TCDN1__limit", "SR02S___TCDN2__limit", "SR02S___TCDN3__limit", "SR02S___TCDN4__limit",
                    "SR02S___TCDN5__limit", "SR02S___TCDN6__limit", "SR02S___TCDN7__limit", "SR02S___TCDN8__limit", "SR02S___TCDN9__limit",
                    "SR05W___TCDN0__limit", "SR05W___TCDN1__limit", "SR05W___TCDN2__limit", "SR05W___TCDN3__limit", "SR05W___TCDN4__limit",
                    "SR05W___TCDN5__limit", "SR05W___TCDN6__limit", "SR05W___TCDN7__limit", "SR05W___TCDN8__limit", "SR05W___TCDN9__limit",
                    "SR06S___TCDN0__limit", "SR06S___TCDN1__limit", "SR06S___TCDN2__limit", "SR06S___TCDN3__limit", "SR06S___TCDN4__limit",
                    "SR06S___TCDN5__limit", "SR06S___TCDN6__limit", "SR06S___TCDN7__limit", "SR06S___TCDN8__limit", "SR06S___TCDN9__limit",
                    "SR07S___TCDN0__limit", "SR07S___TCDN1__limit", "SR07S___TCDN2__limit", "SR07S___TCDN3__limit", "SR07S___TCDN4__limit",
                    "SR07S___TCDN5__limit", "SR07S___TCDN6__limit", "SR07S___TCDN7__limit", "SR07S___TCDN8__limit", "SR07S___TCDN9__limit",
                    "SR08S___TCDN0__limit", "SR08S___TCDN1__limit", "SR08S___TCDN2__limit", "SR08S___TCDN3__limit", "SR08S___TCDN4__limit",
                    "SR08S___TCDN5__limit", "SR08S___TCDN6__limit", "SR08S___TCDN7__limit", "SR08S___TCDN8__limit", "SR08S___TCDN9__limit",
                    "SR09S___TCDN0__limit", "SR09S___TCDN1__limit", "SR09S___TCDN2__limit", "SR09S___TCDN3__limit", "SR09S___TCDN4__limit",
                    "SR09S___TCDN5__limit", "SR09S___TCDN6__limit", "SR09S___TCDN7__limit", "SR09S___TCDN8__limit", "SR09S___TCDN9__limit",
                    "SR10S___TCDN0__limit", "SR10S___TCDN1__limit", "SR10S___TCDN2__limit", "SR10S___TCDN3__limit", "SR10S___TCDN4__limit",
                    "SR10S___TCDN5__limit", "SR10S___TCDN6__limit", "SR10S___TCDN7__limit", "SR10S___TCDN8__limit", "SR10S___TCDN9__limit",
                    "SR11S___TCDN0__limit", "SR11S___TCDN1__limit", "SR11S___TCDN2__limit", "SR11S___TCDN3__limit", "SR11S___TCDN4__limit",
                    "SR11S___TCDN5__limit", "SR11S___TCDN6__limit", "SR11S___TCDN7__limit", "SR11S___TCDN8__limit", "SR11S___TCDN9__limit",
                    "SR12S___TCDN0__limit", "SR12S___TCDN1__limit", "SR12S___TCDN2__limit", "SR12S___TCDN3__limit", "SR12S___TCDN4__limit",
                    "SR12S___TCDN5__limit", "SR12S___TCDN6__limit", "SR12S___TCDN7__limit", "SR12S___TCDN8__limit", "SR12S___TCDN9__limit"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '°C',
                'PhysicsUnits': '°C',
                'MemberOf': ['Thermocouples', 'Temperature', 'Monitor'],
                'Mode': 'Online'
            },
            'Overtemp_flag': {
                'ChannelNames': [
                    "SR02S___TCDN0__BM", "SR02S___TCDN1__BM", "SR02S___TCDN2__BM", "SR02S___TCDN3__BM", "SR02S___TCDN4__BM",
                    "SR02S___TCDN5__BM", "SR02S___TCDN6__BM", "SR02S___TCDN7__BM", "SR02S___TCDN8__BM", "SR02S___TCDN9__BM",
                    "SR05W___TCDN0__BM", "SR05W___TCDN1__BM", "SR05W___TCDN2__BM", "SR05W___TCDN3__BM", "SR05W___TCDN4__BM",
                    "SR05W___TCDN5__BM", "SR05W___TCDN6__BM", "SR05W___TCDN7__BM", "SR05W___TCDN8__BM", "SR05W___TCDN9__BM",
                    "SR06S___TCDN0__BM", "SR06S___TCDN1__BM", "SR06S___TCDN2__BM", "SR06S___TCDN3__BM", "SR06S___TCDN4__BM",
                    "SR06S___TCDN5__BM", "SR06S___TCDN6__BM", "SR06S___TCDN7__BM", "SR06S___TCDN8__BM", "SR06S___TCDN9__BM",
                    "SR07S___TCDN0__BM", "SR07S___TCDN1__BM", "SR07S___TCDN2__BM", "SR07S___TCDN3__BM", "SR07S___TCDN4__BM",
                    "SR07S___TCDN5__BM", "SR07S___TCDN6__BM", "SR07S___TCDN7__BM", "SR07S___TCDN8__BM", "SR07S___TCDN9__BM",
                    "SR08S___TCDN0__BM", "SR08S___TCDN1__BM", "SR08S___TCDN2__BM", "SR08S___TCDN3__BM", "SR08S___TCDN4__BM",
                    "SR08S___TCDN5__BM", "SR08S___TCDN6__BM", "SR08S___TCDN7__BM", "SR08S___TCDN8__BM", "SR08S___TCDN9__BM",
                    "SR09S___TCDN0__BM", "SR09S___TCDN1__BM", "SR09S___TCDN2__BM", "SR09S___TCDN3__BM", "SR09S___TCDN4__BM",
                    "SR09S___TCDN5__BM", "SR09S___TCDN6__BM", "SR09S___TCDN7__BM", "SR09S___TCDN8__BM", "SR09S___TCDN9__BM",
                    "SR10S___TCDN0__BM", "SR10S___TCDN1__BM", "SR10S___TCDN2__BM", "SR10S___TCDN3__BM", "SR10S___TCDN4__BM",
                    "SR10S___TCDN5__BM", "SR10S___TCDN6__BM", "SR10S___TCDN7__BM", "SR10S___TCDN8__BM", "SR10S___TCDN9__BM",
                    "SR11S___TCDN0__BM", "SR11S___TCDN1__BM", "SR11S___TCDN2__BM", "SR11S___TCDN3__BM", "SR11S___TCDN4__BM",
                    "SR11S___TCDN5__BM", "SR11S___TCDN6__BM", "SR11S___TCDN7__BM", "SR11S___TCDN8__BM", "SR11S___TCDN9__BM",
                    "SR12S___TCDN0__BM", "SR12S___TCDN1__BM", "SR12S___TCDN2__BM", "SR12S___TCDN3__BM", "SR12S___TCDN4__BM",
                    "SR12S___TCDN5__BM", "SR12S___TCDN6__BM", "SR12S___TCDN7__BM", "SR12S___TCDN8__BM", "SR12S___TCDN9__BM"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Thermocouples'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['TC Lower'] * 90,
                'DeviceList': [
                    [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8], [2, 9], [2, 10],
                    [5, 1], [5, 2], [5, 3], [5, 4], [5, 5], [5, 6], [5, 7], [5, 8], [5, 9], [5, 10],
                    [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6], [6, 7], [6, 8], [6, 9], [6, 10],
                    [7, 1], [7, 2], [7, 3], [7, 4], [7, 5], [7, 6], [7, 7], [7, 8], [7, 9], [7, 10],
                    [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [8, 7], [8, 8], [8, 9], [8, 10],
                    [9, 1], [9, 2], [9, 3], [9, 4], [9, 5], [9, 6], [9, 7], [9, 8], [9, 9], [9, 10],
                    [10, 1], [10, 2], [10, 3], [10, 4], [10, 5], [10, 6], [10, 7], [10, 8], [10, 9], [10, 10],
                    [11, 1], [11, 2], [11, 3], [11, 4], [11, 5], [11, 6], [11, 7], [11, 8], [11, 9], [11, 10],
                    [12, 1], [12, 2], [12, 3], [12, 4], [12, 5], [12, 6], [12, 7], [12, 8], [12, 9], [12, 10]
                ],
                'ElementList': list(range(1, 91)),
                'MemberOf': ['Thermocouples']
            }
        },
        "SEN": {
            'Setpoint': {
                'ChannelNames': [
                    "SR01S___SEN____AC00"
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
                    "SR01S___SEN____AM00"
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
                    "SR01S___SEN____AC30"
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
                    "SR01S___SEN____AC40"
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
                    "SR01S___SEN____BC20"
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
            'CrashOffOK': {
                'ChannelNames': [
                    "SR01S___SEN____BM00"
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
                    "SR01S___SEN____BM01"
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
            'HVCoverOK': {
                'ChannelNames': [
                    "SR01S___SEN____BM02"
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
                    "SR01S___SEN____BM03"
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
                    "SR01S___SEN____BM04"
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
            'RemoteLocal': {
                'ChannelNames': [
                    "SR01S___SEN____BM05"
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
                    "SR01S___SEN____BM06"
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
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['Septum']
            }
        },
        "SEK": {
            'Setpoint': {
                'ChannelNames': [
                    "SR01S___SEK____AC01"
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
                    "SR01S___SEK____AM02"
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
            'HVControl': {
                'ChannelNames': [
                    "SR01S___SEK____BC21"
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
            'CrashOffOK': {
                'ChannelNames': [
                    "SR01S___SEK____BM07"
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
                    "SR01S___SEK____BM08"
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
            'HVCoverOn': {
                'ChannelNames': [
                    "SR01S___SEK____BM09"
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
                    "SR01S___SEK____BM10"
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
            'CrashOffOK2': {
                'ChannelNames': [
                    "SR01S___SEK____BM12"
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
                    "SR01S___SEK____BM13"
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
            'AirflowOK': {
                'ChannelNames': [
                    "SR01S___SEK____BM14"
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
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['Septum']
            }
        },
    'PSS': {
        'FrontendShutterIsOpen': {
            'ChannelNames': [
                'BL020:PSS101:IsOpen', 'BL020:PSS111:IsOpen', 
                'BL0402:PSS201:IsOpen', 'BL0403:PSS301:IsOpen', 
                'BL050:PSS001:IsOpen', 'BL050:PSS101:IsOpen', 'BL050:PSS111:IsOpen', 'BL050:PSS201:IsOpen', 'BL050:PSS211:IsOpen', 'BL050:PSS301:IsOpen', 'BL050:PSS311:IsOpen', 'BL053:PSS101:IsOpen', 'BL053:PSS201:IsOpen', 'BL053:PSS211:IsOpen', 'BL053:PSS221:IsOpen', 
                'BL0601:PSS101:IsOpen', 'BL0601:PSS131:IsOpen', 'BL0602:PSS201:IsOpen', 'BL0612:PSS001:IsOpen', 'BL0631:PSS101:IsOpen', 'BL0632:PSS201:IsOpen', 
                'BL0701:PSS101:IsOpen', 'BL0701:PSS121:IsOpen', 'BL0702:PSS201:IsOpen', 'BL073:PSS001:IsOpen', 'BL073:PSS111:IsOpen', 'BL073:PSS301:IsOpen', 
                'BL0801:PSS001:IsOpen', 'BL0801:PSS121:IsOpen', 'BL082:PSS101:IsOpen', 'BL082:PSS111:IsOpen', 'BL082:PSS201:IsOpen', 'BL082:PSS211:IsOpen', 'BL083:PSS101:IsOpen', 'BL083:PSS111:IsOpen', 'BL083:PSS201:IsOpen', 'BL083:PSS211:IsOpen', 
                'BL0901:PSS001:IsOpen', 'BL0931:PSS101:IsOpen', 'BL0931:PSS102:IsOpen', 'BL0932:PSS221:IsOpen', 
                'BL100:PSS001:IsOpen', 'BL1031:PSS101:IsOpen', 'BL1032:PSS201:IsOpen', 
                'BL1101:PSS101:IsOpen', 'BL1102:PSS201:IsOpen', 'BL1102:PSS211:IsOpen', 'BL1102:PSS212:IsOpen', 'BL1102:PSS221:IsOpen', 'BL1132:PSS201:IsOpen', 
                'BL1201:PSS001:IsOpen', 'BL1202:PSS001:IsOpen', 'BL122:PSS101:IsOpen', 'BL122:PSS111:IsOpen', 'BL122:PSS201:IsOpen', 'BL122:PSS211:IsOpen'
            ],
            'DataType': 'Boolean',
            'HW2PhysicsParams': 1,
            'Physics2HWParams': 1,
            'Units': 'Hardware',
            'HWUnits': [],
            'PhysicsUnits': [],
            'MemberOf': ['Thermocouples'],
            'Mode': 'Online'
        },
        'setup': {
            'DeviceList': [
                [2, 1], [2, 2],
                [4, 1], [4, 2],
                [5, 1], [5, 2], [5, 3], [5, 4], [5, 5], [5, 6], [5, 7], [5, 8], [5, 9], [5, 10], [5, 11],
                [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6],
                [7, 1], [7, 2], [7, 3], [7, 4], [7, 5], [7, 6],
                [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [8, 7], [8, 8], [8, 9], [8, 10],
                [9, 1], [9, 2], [9, 3], [9, 4],
                [10, 1], [10, 2], [10, 3],
                [11, 1], [11, 2], [11, 3], [11, 4], [11, 5], [11, 6],
                [12, 1], [12, 2], [12, 3], [12, 4], [12, 5], [12, 6]
            ],
            'ElementList': list(range(1, 56)),
            'MemberOf': ['PSS']
            }
        },
        "BunchCurrentMonitor": {
            'BunchCurrent': {
                'ChannelNames': [
                    "SR:BCM:BunchCurrent"
                ],
                'DataType': 'Waveform',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mA',
                'PhysicsUnits': 'mA',
                'MemberOf': ['BCM', 'BunchCurrent', 'Monitor'],
                'Mode': 'Online'
            },
            'BunchPhase': {
                'ChannelNames': [
                    "SR:BCM:BunchPhase"
                ],
                'DataType': 'Waveform',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'deg',
                'PhysicsUnits': 'deg',
                'MemberOf': ['BCM', 'BunchPhase', 'Monitor'],
                'Mode': 'Online'
            },
            'AvgPhase': {
                'ChannelNames': [
                    "SR:BCM:AvgPhase"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'deg',
                'PhysicsUnits': 'deg',
                'MemberOf': ['BCM', 'AvgPhase', 'Monitor'],
                'Mode': 'Online'
            },
            'CamBunchCurrent': {
                'ChannelNames': [
                    "SR:BCM:Cam2:Current"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mA',
                'PhysicsUnits': 'mA',
                'MemberOf': ['BCM', 'CamBunch', 'Current', 'Monitor'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Bunch Current Monitor'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['BCM']
            }
        },
        "Lifetime": {
            'SlowAverage': {
                'ChannelNames': [
                    "Topoff_lifetime_AM"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'hours',
                'PhysicsUnits': 'hours',
                'MemberOf': ['Lifetime', 'Monitor'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Beam Lifetime'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['Lifetime']
            }
        },
        "RF": {
            'PhaseSetpoint': {
                'ChannelNames': [
                    "SRRF:LLRF1:Loop1:PhsSetpRBV"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'deg',
                'PhysicsUnits': 'deg',
                'MemberOf': ['RF', 'Phase', 'Setpoint'],
                'Mode': 'Online'
            },
            'Klystron1ForwardPower': {
                'ChannelNames': [
                    "SRRF:RFMON1:Kly1OutFwd:Pwr"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'kW',
                'PhysicsUnits': 'kW',
                'MemberOf': ['RF', 'Klystron', 'Power', 'Monitor'],
                'Mode': 'Online'
            },
            'Klystron2ForwardPower': {
                'ChannelNames': [
                    "SRRF:RFMON1:Kly2OutFwd:Pwr"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'kW',
                'PhysicsUnits': 'kW',
                'MemberOf': ['RF', 'Klystron', 'Power', 'Monitor'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['RF System'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['RF']
            }
        },
        "Operations": {
            'UserBeamAvailable': {
                'ChannelNames': [
                    "sr:user_beam"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['Operations', 'UserBeam', 'Status'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Operations Status'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['Operations']
            }
        },
        "HarmonicCavity": {
            'PowerMonitor': {
                'ChannelNames': [
                    "SR02C___C1PWR__AM00",
                    "SR02C___C2PWR__AM00",
                    "SR02C___C3PWR__AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'W',
                'PhysicsUnits': 'W',
                'MemberOf': ['HarmonicCavity', 'Power', 'Monitor'],
                'Mode': 'Online'
            },
            'MainTunerTempOk': {
                'ChannelNames': [
                    "SR02C___C1TEMP_BM00",
                    "SR02C___C2TEMP_BM00",
                    "SR02C___C3TEMP_BM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['HarmonicCavity', 'Temperature', 'Interlock'],
                'Mode': 'Online'
            },
            'RtnTempOk': {
                'ChannelNames': [
                    "SR02C___C1TEMP_BM01",
                    "SR02C___C2TEMP_BM01",
                    "SR02C___C3TEMP_BM01"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['HarmonicCavity', 'Temperature', 'Interlock'],
                'Mode': 'Online'
            },
            'VerHOMDamperTempOk': {
                'ChannelNames': [
                    "SR02C___C1TEMP_BM02",
                    "SR02C___C2TEMP_BM02",
                    "SR02C___C3TEMP_BM02"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['HarmonicCavity', 'Temperature', 'Interlock'],
                'Mode': 'Online'
            },
            'HorHOMDamperTempOk': {
                'ChannelNames': [
                    "SR02C___C1TEMP_BM03",
                    "SR02C___C2TEMP_BM03",
                    "SR02C___C3TEMP_BM03"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['HarmonicCavity', 'Temperature', 'Interlock'],
                'Mode': 'Online'
            },
            'MainTunerPositionSetpoint': {
                'ChannelNames': [
                    "SR02C___C1MPOS_AC00",
                    "SR02C___C2MPOS_AC00",
                    "SR02C___C3MPOS_AC00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mm',
                'PhysicsUnits': 'mm',
                'MemberOf': ['HarmonicCavity', 'MainTuner', 'Position', 'Setpoint'],
                'Mode': 'Online'
            },
            'MainTunerPositionMonitor': {
                'ChannelNames': [
                    "SR02C___C1MPOS_AM00",
                    "SR02C___C2MPOS_AM00",
                    "SR02C___C3MPOS_AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mm',
                'PhysicsUnits': 'mm',
                'MemberOf': ['HarmonicCavity', 'MainTuner', 'Position', 'Monitor'],
                'Mode': 'Online'
            },
            'AuxTunerPositionSetpoint': {
                'ChannelNames': [
                    "SR02C___C1APOS_AC00",
                    "SR02C___C2APOS_AC00",
                    "SR02C___C3APOS_AC00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mm',
                'PhysicsUnits': 'mm',
                'MemberOf': ['HarmonicCavity', 'AuxTuner', 'Position', 'Setpoint'],
                'Mode': 'Online'
            },
            'AuxTunerPositionMonitor': {
                'ChannelNames': [
                    "SR02C___C1APOS_AM00",
                    "SR02C___C2APOS_AM00",
                    "SR02C___C3APOS_AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'mm',
                'PhysicsUnits': 'mm',
                'MemberOf': ['HarmonicCavity', 'AuxTuner', 'Position', 'Monitor'],
                'Mode': 'Online'
            },
            'BodyReturnTemperature': {
                'ChannelNames': [
                    "SR02C___C1BRTP_AM00",
                    "SR02C___C2BRTP_AM00",
                    "SR02C___C3BRTP_AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '°C',
                'PhysicsUnits': '°C',
                'MemberOf': ['HarmonicCavity', 'Temperature', 'Monitor'],
                'Mode': 'Online'
            },
            'ExternalBodyTemperature': {
                'ChannelNames': [
                    "SR02C___C1EBST_AM00",
                    "SR02C___C2EBST_AM00",
                    "SR02C___C3EBST_AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '°C',
                'PhysicsUnits': '°C',
                'MemberOf': ['HarmonicCavity', 'Temperature', 'Monitor'],
                'Mode': 'Online'
            },
            'WaterFlow': {
                'ChannelNames': [
                    "SR02C___C1BFLW_AM00",
                    "SR02C___C2BFLW_AM00",
                    "SR02C___C3BFLW_AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'L/min',
                'PhysicsUnits': 'L/min',
                'MemberOf': ['HarmonicCavity', 'Flow', 'Monitor'],
                'Mode': 'Online'
            },
            'HOMFlow': {
                'ChannelNames': [
                    "SR02C___C1HFLW_AM00",
                    "SR02C___C2HFLW_AM00",
                    "SR02C___C3HFLW_AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': 'L/min',
                'PhysicsUnits': 'L/min',
                'MemberOf': ['HarmonicCavity', 'HOM', 'Flow', 'Monitor'],
                'Mode': 'Online'
            },
            'MainTunerError': {
                'ChannelNames': [
                    "SR02C___C1MERR_AM00",
                    "SR02C___C2MERR_AM00",
                    "SR02C___C3MERR_AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '',
                'PhysicsUnits': '',
                'MemberOf': ['HarmonicCavity', 'MainTuner', 'Error', 'Monitor'],
                'Mode': 'Online'
            },
            'AuxTunerError': {
                'ChannelNames': [
                    "SR02C___C1AERR_AM00",
                    "SR02C___C2AERR_AM00",
                    "SR02C___C3AERR_AM00"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '',
                'PhysicsUnits': '',
                'MemberOf': ['HarmonicCavity', 'AuxTuner', 'Error', 'Monitor'],
                'Mode': 'Online'
            },
            'LoopClosed': {
                'ChannelNames': [
                    "SR02C___C1ALOP_BM02",
                    "SR02C___C2ALOP_BM02",
                    "SR02C___C3ALOP_BM02"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['HarmonicCavity', 'Loop', 'Status'],
                'Mode': 'Online'
            },
            'LoopOpen': {
                'ChannelNames': [
                    "SR02C___C1ALOP_BM03",
                    "SR02C___C2ALOP_BM03",
                    "SR02C___C3ALOP_BM03"
                ],
                'DataType': 'Boolean',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': [],
                'PhysicsUnits': [],
                'MemberOf': ['HarmonicCavity', 'Loop', 'Status'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': [
                    'Harmonic Cavity 1',
                    'Harmonic Cavity 2', 
                    'Harmonic Cavity 3'
                ],
                'DeviceList': [[2, 1], [2, 2], [2, 3]],
                'ElementList': [1, 2, 3],
                'MemberOf': ['HarmonicCavity']
            }
        }
    }
}
