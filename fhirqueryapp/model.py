from wtforms import Form,SelectField,IntegerField,TextField, validators
RESOURCE_TYPES= [
    ('Patient', 'Patient'),
    ('Observation', 'Observation'),
    ('Encounter', 'Encounter'),
    ]
class InputForm(Form):
    patientId = TextField(
        label='ResourceId',
        validators=[validators.InputRequired()])
    resourceType  = SelectField(
        label='ResourceType', choices=RESOURCE_TYPES,
        validators=[validators.InputRequired()])
