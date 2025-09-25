manual_imports_BTS = {
    "BTS": {
        "TV": {
            "RawImage": {
                "MemberOf": ['TV'],
                "DataType": 'Waveform',
                "ChannelNames": [
                    "BTS1:image1:ArrayData",
                    "BTS2:image1:ArrayData",
                    "BTS3:image1:ArrayData",
                    "BTS4:image1:ArrayData",
                    "BTS5:image1:ArrayData",
                    "BTS6:image1:ArrayData",
                    "                     ",
                ]
            }
        },
        "Transfer": {
            'Efficiency': {
                'ChannelNames': [
                    "BTS:Transfer:Efficiency"
                ],
                'DataType': 'Scalar',
                'HW2PhysicsParams': 1,
                'Physics2HWParams': 1,
                'Units': 'Hardware',
                'HWUnits': '%',
                'PhysicsUnits': '%',
                'MemberOf': ['Transfer', 'Efficiency'],
                'Mode': 'Online'
            },
            'setup': {
                'CommonNames': ['Transfer'],
                'DeviceList': [[1, 1]],
                'ElementList': [1],
                'MemberOf': ['Transfer']
            }
        }
    }
}
