# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta 

class medical_patient(models.Model):
    
    _name = 'medical.patient'
    _rec_name = 'patient_id'

        
    @api.onchange('patient_id')
    def _onchange_patient(self):
        address_id = self.patient_id.owner_id
        self.partner_address_id = address_id 
        

    @api.depends('date_of_birth')
    def onchange_age(self):
        if self.date_of_birth:
            dt = self.date_of_birth
            d1 = dt
            d2 = datetime.today()
            rd = relativedelta(d2, d1)
            self.age = str(rd.years) + "y" +" "+ str(rd.months) + "m" +" "+ str(rd.days) + "d"
        else:
            self.age = "No date_of_birth!!"

    patient_id = fields.Many2one('res.partner',string="Patient", required= True)
    name = fields.Char(string='ID',readonly= True)
    last_name = fields.Char('Last Name')
    date_of_birth = fields.Date(string="Date of Birth")
    sex = fields.Selection([('m', 'Male'),('f', 'Female')], string ="Sex")
    age = fields.Char(compute=onchange_age,string="Patient Age")
    critical_info = fields.Text(string="Patient Critical Information")
    photo = fields.Binary(string="Picture")
    height = fields.Float(string="Height")
    weight = fields.Float(string="Width")
    color = fields.Char(string="Color")
    breed_id = fields.Many2one('pet.breed',string="Breed")
    blood_type = fields.Selection([('A', 'A'),('B', 'B'),('AB', 'AB'),('O', 'O')], string ="Blood Type")
    rh = fields.Selection([('-+', '+'),('--', '-')], string ="Rh")
    pet_type_id = fields.Many2one('pet.type',string="Type Of Pet")
    family_code_id = fields.Many2one('medical.family_code',string="Family")
    receivable = fields.Float(string="Receivable", readonly=True)
    current_insurance_id = fields.Many2one('medical.insurance',string="Insurance")
    partner_address_id = fields.Many2one('res.partner', string="Address", )
    doctor_id = fields.Many2one('medical.physician', string="Primary Care Doctor")
    patient_status = fields.Char(string="Hospitalization Status")
    diseases_ids = fields.One2many('medical.patient.disease','patient_id')
    patient_psc_ids = fields.One2many('medical.patient.psc','patient_id')
    evaluation_ids = fields.One2many('medical.patient.evaluation','medical_patient_id')
    excercise = fields.Boolean(string='Excercise')
    excercise_minutes_day = fields.Integer(string="Minutes/Day")
    sleep_hours = fields.Integer(string="Hours of sleep")
    sleep_during_daytime = fields.Boolean(string="Sleep at daytime")
    number_of_meals = fields.Integer(string="Meals per day")
    eats_alone = fields.Boolean(string="Eats alone")
    soft_drinks = fields.Boolean(string="Soft drinks(sugar)")
    salt = fields.Boolean(string="Salt")
    lifestyle_info = fields.Text('Lifestyle Information')
    smoking = fields.Boolean(string="Smokes")
    smoking_number = fields.Integer(string="Cigarretes a day")
    ex_smoker = fields.Boolean(string="Ex-smoker")
    second_hand_smoker = fields.Boolean(string="Passive smoker")
    age_start_smoking = fields.Integer(string="Age started to smoke")
    age_quit_smoking = fields.Integer(string="Age of quitting")
    drug_usage = fields.Boolean(string='Drug Habits')
    drug_iv = fields.Boolean(string='IV drug user')
    ex_drug_addict = fields.Boolean(string='Ex drug addict')
    age_start_drugs = fields.Integer(string='Age started drugs')
    age_quit_drugs = fields.Integer(string="Age quit drugs")
    alcohol = fields.Boolean(string="Drinks Alcohol")
    ex_alcohol = fields.Boolean(string="Ex alcoholic")
    age_start_drinking = fields.Integer(string="Age started to drink")
    age_quit_drinking = fields.Integer(string="Age quit drinking")
    alcohol_beer_number = fields.Integer(string="Beer / day")
    alcohol_wine_number = fields.Integer(string="Wine / day")
    alcohol_liquor_number = fields.Integer(string="Liquor / day")
    cage_ids = fields.One2many('medical.patient.cage','patient_id')
    drugs_ids = fields.Many2many('medical.drugs_recreational', string="Drugs")
    sexual_preferences = fields.Selection([
            ('h', 'Heterosexual'),
            ('g', 'Homosexual'),
            ('b', 'Bisexual'),
            ('t', 'Transexual'),
        ], 'Sexual Orientation', sort=False)
    sexual_practices = fields.Selection([
            ('s', 'Safe / Protected sex'),
            ('r', 'Risky / Unprotected sex'),
        ], 'Sexual Practices', sort=False)
    sexual_partners = fields.Selection([
            ('m', 'Monogamous'),
            ('t', 'Polygamous'),
        ], 'Sexual Partners', sort=False)
    sexual_partners_number = fields.Integer('Number of sexual partners')
    first_sexual_encounter = fields.Integer('Age first sexual encounter')
    anticonceptive = fields.Selection([
            ('0', 'None'),
            ('1', 'Pill / Minipill'),
            ('2', 'Male condom'),
            ('3', 'Vasectomy'),
            ('4', 'Female sterilisation'),
            ('5', 'Intra-uterine device'),
            ('6', 'Withdrawal method'),
            ('7', 'Fertility cycle awareness'),
            ('8', 'Contraceptive injection'),
            ('9', 'Skin Patch'),
            ('10', 'Female condom'),
        ], 'Anticonceptive Method', sort=False)
    sexuality_info = fields.Text('Extra Information')
    motorcycle_rider = fields.Boolean('Motorcycle Rider', help="The patient rides motorcycles")
    helmet = fields.Boolean('Uses helmet', help="The patient uses the proper motorcycle helmet")
    traffic_laws = fields.Boolean('Obeys Traffic Laws', help="Check if the patient is a safe driver")
    car_revision = fields.Boolean('Car Revision', help="Maintain the vehicle. Do periodical checks - tires,breaks ...")
    car_seat_belt = fields.Boolean('Seat belt', help="Safety measures when driving : safety belt")
    car_child_safety = fields.Boolean('Car Child Safety', help="Safety measures when driving : child seats, proper seat belting, not seating on the front seat, ....")
    home_safety = fields.Boolean('Home safety', help="Keep safety measures for kids in the kitchen, correct storage of chemicals, ...")
    fertile = fields.Boolean('Fertile')
    menarche = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    menopause = fields.Integer('Menopause age')
    menstrual_history_ids = fields.One2many('medical.patient.menstrual.history','patient_id')
    breast_self_examination = fields.Boolean('Breast self-examination')
    mammography = fields.Boolean('Mammography')
    pap_test = fields.Boolean('PAP test')
    last_pap_test_date = fields.Date('Last PAP test')
    colposcopy = fields.Boolean('Colposcopy')
    mammography_history_ids = fields.One2many('medical.patient.mammography.history','patient_id')
    pap_history_ids = fields.One2many('medical.patient.pap.history','patient_id')
    colposcopy_history_ids = fields.One2many('medical.patient.colposcopy.history','patient_id')
    pregnancies = fields.Integer('Pregnancies')
    premature = fields.Integer('Premature')
    stillbirths = fields.Integer('Stillbirths')
    abortions = fields.Integer('Abortions')
    pregnancy_history_ids = fields.One2many('medical.patient.pregnency','patient_id')
    genetic_risks_ids = fields.Many2many('medical.genetic.risk')
    family_history_ids = fields.Many2many('medical.family.disease')
    surgery_ids = fields.One2many('medical.surgery','patient_id')
    socionomics = fields.Selection([
            ('None', ''),
            ('0', 'Lower'),
            ('1', 'Lower-middle'),
            ('2', 'Middle'),
            ('3', 'Middle-upper'),
            ('4', 'Higher'),
        ], string='Socioeconomics', help="SES - Socioeconomic Status", sort=False)
    education = fields.Selection([('o','None'),('1','Incomplete Primary School'),
                                  ('2','Primary School'),
                                  ('3','Incomplete Secondary School'),
                                  ('4','Secondary School'),
                                  ('5','University')],string='Education Level')
    housing = fields.Selection([
            ('None', ''),
            ('0', 'Shanty, deficient sanitary conditions'),
            ('1', 'Small, crowded but with good sanitary conditions'),
            ('2', 'Comfortable and good sanitary conditions'),
            ('3', 'Roomy and excellent sanitary conditions'),
            ('4', 'Luxury and excellent sanitary conditions'),
        ], 'Housing conditions', help="Housing and sanitary living conditions", sort=False)
    works = fields.Boolean('Works')
    hours_outside = fields.Integer('Hours outside home', help="Number of hours a day the patient spend outside the house")
    hostile_area = fields.Boolean('Hostile Area')
    notes = fields.Text(string="Extra info")
    sewers = fields.Boolean('Sanitary Sewers')
    water = fields.Boolean('Running Water')
    trash = fields.Boolean('Trash recollection')
    electricity = fields.Boolean('Electrical supply')
    gas = fields.Boolean('Gas supply')
    telephone = fields.Boolean('Telephone')
    television = fields.Boolean('Television')
    internet = fields.Boolean('Internet')
    single_parent= fields.Boolean('Single parent family')
    domestic_violence = fields.Boolean('Domestic violence')
    working_children = fields.Boolean('Working children')
    teenage_pregnancy = fields.Boolean('Teenage pregnancy')
    sexual_abuse = fields.Boolean('Sexual abuse')
    drug_addiction = fields.Boolean('Drug addiction')
    school_withdrawal = fields.Boolean('School withdrawal')
    prison_past = fields.Boolean('Has been in prison')
    prison_current = fields.Boolean('Is currently in prison')
    relative_in_prison = fields.Boolean('Relative in prison', help="Check if someone from the nuclear family - parents sibblings  is or has been in prison")
    fam_apgar_help = fields.Selection([
            ('None', ''),
            ('0', 'None'),
            ('1', 'Moderately'),
            ('2', 'Very much'),
        ], 'Help from family',
            help="Is the patient satisfied with the level of help coming from the family when there is a problem ?", sort=False)
    fam_apgar_discussion = fields.Selection([
            ('None', ''),
            ('0', 'None'),
            ('1', 'Moderately'),
            ('2', 'Very much'),
        ], 'Problems discussion',
            help="Is the patient satisfied with the level talking over the problems as family ?", sort=False)
    fam_apgar_decisions = fields.Selection([
            ('None', ''),
            ('0', 'None'),
            ('1', 'Moderately'),
            ('2', 'Very much'),
        ], 'Decision making',
            help="Is the patient satisfied with the level of making important decisions as a group ?", sort=False)
    fam_apgar_timesharing = fields.Selection([
            ('None', ''),
            ('0', 'None'),
            ('1', 'Moderately'),
            ('2', 'Very much'),
        ], 'Time sharing',
            help="Is the patient satisfied with the level of time that they spend together ?", sort=False)
    fam_apgar_affection = fields.Selection([
            ('None', ''),
            ('0', 'None'),
            ('1', 'Moderately'),
            ('2', 'Very much'),
        ], 'Family affection',
            help="Is the patient satisfied with the level of affection coming from the family ?", sort=False)
    fam_apgar_score = fields.Integer('Score', help="Total Family APGAR 7 - 10 : Functional Family 4 - 6  : Some level of disfunction \n"
                                          "0 - 3  : Severe disfunctional family \n")
    lab_test_ids = fields.One2many('medical.patient.lab.test','patient_id')
    fertile = fields.Boolean('Fertile')
    menarche_age  = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    pap_test_last_date = fields.Date('Last PAP Test')
    colposcopy = fields.Boolean('Colpscopy')
    gravida = fields.Integer('Pregnancies')
    medical_vaccination_ids = fields.One2many('medical.vaccination','medical_patient_vaccines_id')
    medical_appointments_ids = fields.One2many('medical.appointment','patient_id',string='Appointments')
    lastname = fields.Char('Last Name')
    report_date = fields.Date('Date',default = fields.Date.context_today)
    medication_ids = fields.One2many('medical.patient.medication1','medical_patient_medication_id')


    @api.model
    def create(self,val):
        val['name'] = self.env['ir.sequence'].next_by_code('medical.patient')
        result = super(medical_patient, self).create(val)
        return result
# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: