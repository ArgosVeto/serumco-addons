# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class medical_patient_evaluation(models.Model):
    _name = 'medical.patient.evaluation'
    _rec_name = 'medical_patient_id' 

    patient_id = fields.Many2one('res.partner',string="Patient")
    medical_patient_id = fields.Many2one('medical.patient',string="Medical Patient" ,required=True)
    start_evaluation = fields.Datetime(string="Start Evaluation")
    physicians_id = fields.Many2one('res.partner',string="Doctor",required=True)
    end_evaluation = fields.Datetime(string="End of Evaluation")
    evaluation_type= fields.Selection([
            ('a', 'Ambulatory'),
            ('e', 'Emergency'),
            ('i', 'Inpatient'),
            ('pa', 'Pre-arranged appointment'),
            ('pc', 'Periodic control'),
            ('p', 'Phone call'),
            ('t', 'Telemedicine'),
        ], string='Type')
    chief_complaint = fields.Char('Chief Complaint')
    information_source = fields.Char('Source')
    reliable_info = fields.Boolean('Reliable')
    present_illness = fields.Text(string='Present Illness')
   
    weight = fields.Float(string='Weight (kg)',help='Weight in Kilos')
    height = fields.Float(string='Height (cm)')
    abdominal_circ = fields.Float(string='Abdominal Circumference')
    hip = fields.Float(string='Hip')
    bmi = fields.Float(string='Body Mass Index')
    whr = fields.Float(string='WHR')
    head_circumference = fields.Float(string='Head Circumference')
    malnutrition = fields.Boolean('Malnutrition')
    dehydration = fields.Boolean('Dehydration')
    tag = fields.Integer(
            string='Last TAGs',
            help='Triacylglycerol(triglicerides) level. Can be approximative'
        )
    is_tremor = fields.Boolean(
            string='Tremor',
            help='Check this box is the patient shows signs of tremors',
        )
    mood = fields.Selection([
            ('n', 'Normal'),
            ('s', 'Sad'),
            ('f', 'Fear'),
            ('r', 'Rage'),
            ('h', 'Happy'),
            ('d', 'Disgust'),
            ('e', 'Euphoria'),
            ('fl', 'Flat'),
        ], string='Mood')
    specialty_id = fields.Many2one('medical.speciality',
                                        string='Specialty',)
    glycemia = fields.Float(
            string='Glycemia',
            help='Last blood glucose level. Can be approximative.')
    evaluation_summary = fields.Text(string='Evaluation Summary')
    temperature = fields.Float(string='Temperature (celsius)',
                                    help='Temperature in celcius')
    osat = fields.Integer(string='Oxygen Saturation',
                               help='Oxygen Saturation(arterial).')
    bpm = fields.Integer(string='Heart Rate',
                              help='Heart rate expressed in beats per minute')
    glasgow_eyes = fields.Selection([
            ('1', 'Does not Open Eyes'),
            ('2', 'Opens eyes in response to painful stimuli'),
            ('3', 'Opens eyes in response to voice'),
            ('4', 'Opens eyes spontaneously'),
        ], string='Glasgow - Eyes')
    glasgow_verbal = fields.Selection([
            ('1', 'Make no sounds'),
            ('2', 'Incomprehensible Sounds'),
            ('3', 'Utters inappropriate words'),
            ('4', 'Confused,disoriented'),
            ('5', 'Oriented, converses normally'),
        ], string='Glasgow - Verbal')
    glasgow_motor = fields.Selection([
            ('1', 'Make no movement'),
            ('2', 'Extension to painful stimuli decerebrate response'),
            ('3', 'Abnormal flexion to painful stimuli decerebrate response'),
            ('4', 'Flexion/Withdrawal to painful stimuli '),
            ('5', 'Localizes painful stimuli'),
            ('6', 'Obeys commands'),
        ], string='Glasgow - Motor')
    violent = fields.Boolean('Violent Behaviour')
    orientation = fields.Boolean('Orientation')
    memory = fields.Boolean('Memory')
    knowledge_current_events = fields.Boolean('Knowledge of Current Events')
    judgment = fields.Boolean('Jugdment')
    abstraction = fields.Boolean('Abstraction')
    vocabulary = fields.Boolean('Vocabulary')
    calculation_ability = fields.Boolean('Calculation Ability')
    object_recognition = fields.Boolean('Object Recognition')
    praxis = fields.Boolean('Praxis')
    diagnosis_id = fields.Many2one('medical.pathology','Presumptive Diagnosis')
    ldl = fields.Integer(
            string='Last LDL',
            help='Last LDL Cholesterol reading. Can be approximative'
        )
    visit_type  = fields.Selection([('new','New Health Condition'),('follow','FollowUp'),('chronic','Chronic Condition ChechUp'),('child','Well Child Visit'),('women','Well Woman Visit'),('man','Well Man Visit')],string="Visit")
    urgency  = fields.Selection([('a', 'Normal'), ('b', 'Urgent'), ('c', 'Medical Emergency')],string='Urgency')
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    respiratory_rate = fields.Integer('Respiratory Rate')
    signs_and_symptoms_ids = fields.One2many('medical.signs.and.sympotoms','patient_evaluation_id','Signs and Symptoms')
    hba1c = fields.Float('Glycated Hemoglobin')
    cholesterol_total = fields.Integer('Last Cholesterol')
    last_hdl = fields.Integer('Last HDL')
    last_ldl = fields.Integer('Last LDL')
    last_tags = fields.Integer('Last TAGs')
    last_level_of_consciousness = fields.Integer('Level of Consciousness')
    info_diagnosis = fields.Text(string='Information on Diagnosis')
    directions = fields.Text(string='Treatment Plan')
    user_id = fields.Many2one('res.users','Doctor user ID',readonly=True)
    appointment_date_id = fields.Many2one('medical.appointment','Appointment Date')
    next_appointment_date_id = fields.Many2one('medical.appointment','Next Appointment')
    from_physician_id = fields.Many2one('medical.physician','Derived from Doctor')
    to_physician_id = fields.Many2one('medical.physician','Derived to Doctor')
    secondary_conditions_ids = fields.One2many('medical.secondary_condition','patient_evaluation_id','Secondary Conditions')
    diagnostic_hypothesis_ids = fields.One2many('medical.diagnostic_hypotesis','patient_evaluation_id','Procedures')
    action_ids = fields.One2many('medical.directions','patient_evaluation_id','Procedures')


