sqlalchemy_type = {
    23: 'Integer',
    701: 'Float',
    1043: 'String'
}

matching_columns = ['id', 'oktmo', 'dadata']

unupdateable_columns = {'id', 'oktmo', 'region_id', 'latitude_dms', 'longitude_dms', 'latitude_dd', 'longitude_dd',
                        'dadata'}
