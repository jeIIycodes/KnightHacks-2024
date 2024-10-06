from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, NumberRange
import pandas as pd

def get_product_choices():
    try:
        df = pd.read_csv('./AiPredictor/data/accelerators.tsv', sep='\t')
        choices = [(row['Product'], row['Product']) for index, row in df.iterrows()]
        return choices
    except FileNotFoundError:
        return []


from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, NumberRange


class CompanyForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])

    implemented_products = SelectMultipleField('Implemented Products', choices=get_product_choices(),
                                               validators=[Optional()])
    unimplemented_products = SelectMultipleField('Unimplemented Products', choices=get_product_choices(),
                                                 validators=[Optional()])

    industry = SelectField(
        'Industry',
        choices=[
            ('finance', 'Finance'),
            ('healthcare', 'Healthcare'),
            ('technology', 'Technology'),
            ('education', 'Education'),
            ('manufacturing', 'Manufacturing'),
            ('energy', 'Energy'),
            ('retail', 'Retail'),
            ('transportation', 'Transportation'),
            ('hospitality', 'Hospitality'),
            ('real_estate', 'Real Estate'),
            ('construction', 'Construction'),
            ('telecommunications', 'Telecommunications'),
            ('entertainment', 'Entertainment'),
            ('government', 'Government'),
            ('non_profit', 'Non-Profit'),
            ('other', 'Other')  # Option to add custom industry
        ],
        validators=[DataRequired()]
    )

    custom_industry = StringField('Custom Industry', validators=[Optional()])

    # Default Program Start Date to today
    program_start_date = DateField('Program Start Date (YYYY-MM-DD)', format='%Y-%m-%d', default=date.today,
                                   validators=[Optional()])

    # Default Company Size to 1
    company_size = IntegerField('Company Size (Number of Employees)', default=1, validators=[Optional(),
                                                                                             NumberRange(min=0,
                                                                                                         message="Company size must be a non-negative integer.")])

    location = StringField('Location', validators=[Optional()])
    company_description = TextAreaField('Company Description', validators=[Optional()])
    current_challenges = TextAreaField('Current Challenges', validators=[Optional()])
    submit = SubmitField('Submit')

