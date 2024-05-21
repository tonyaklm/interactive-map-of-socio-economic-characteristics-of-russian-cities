sqlalchemy_type = {
    23: 'Integer',
    701: 'Float',
    1043: 'String'
}

matching_columns = ['id', 'oktmo']

unupdateable_columns = {'id', 'oktmo', 'region_id', 'latitude_dms', 'longitude_dms', 'latitude_dd', 'longitude_dd'}

technical_columns = {'id', 'region', 'region_id', 'municipality', 'settlement', 'type', 'latitude_dms', 'longitude_dms',
                     'latitude_dd', 'longitude_dd', 'oktmo', 'dadata', 'rosstat'}
