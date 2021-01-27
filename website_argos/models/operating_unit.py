# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

from odoo import api, fields, models
from datetime import datetime,date
import pytz

class OperatingUnitservic(models.Model):
    _inherit = 'operating.unit.service'

    service_image = fields.Binary("Service Banner")
    url = fields.Char(string="Url")

class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    contact_questions_id = fields.Many2one('contact.questions',string="Contact Question")
    service_ids = fields.Many2many("operating.unit.service",string="Services")
    clinic_banner = fields.Binary("Clinic Banner")
    clinic_description = fields.Html(string="Clinic Description",default=lambda self:self.get_clinic_description())
    visible_in_contact = fields.Boolean(string="Visible In Contact")
    clinic_image_ids = fields.One2many('clinic.image', 'operating_unit_id', string="Extra image", copy=True)
    practical_service_ids = fields.Many2many("practical.service",string="Practical Service")
    # payment_method_ids = fields.Many2many("payment.acquirer",string="Payment Methods")
    last_name = fields.Char(string="Last Name")
    mrdv_id = fields.Char(string="Remote")
    facebook = fields.Char(string="Facebook")
    google_map_link = fields.Char (string="Google Map Link")
    show_in_footer = fields.Boolean(string="Show In Footer")

    def  clinic_working_status(self):
        not_working_time = False
        if self.calendar_id:
            attendance_ids = self.calendar_id.attendance_ids
            if attendance_ids:
                for day_week in range(0,6):
                    now_time = datetime.now()
                    date_today = date.today()
                    date_today = date_today.weekday()
                    if date_today == day_week:
                        now_time =  pytz.timezone('UTC').localize(now_time).astimezone(pytz.timezone(self.env.user.tz  or 'UTC')).time()
                        now_time = now_time.hour + now_time.minute/60.0 + now_time.second/3600
                    day_timimg = attendance_ids.filtered(lambda x:x.dayofweek == str(day_week))
                    if day_timimg:
                        if len(day_timimg) == 2:
                            t1 = day_timimg[0].hour_from
                            t2 = day_timimg[0].hour_to
                            t3 = day_timimg[1].hour_from
                            t4 = day_timimg[1].hour_to
                            if (date_today == day_week):
                                if (now_time >= t1) and (now_time <= t2):
                                    not_working_time = True
                                if (now_time >= t3) and (now_time <= t4):
                                    not_working_time = True
                            elif len(day_timimg) == 1:
                                t1 = day_timimg[0].hour_from
                                t2 = day_timimg[0].hour_to
                                if (date_today == day_week):
                                    if (now_time >= t1) and (now_time <= t2):
                                        not_working_time = True
                            elif len(day_timimg) > 2:
                                t1 = day_timimg[0].hour_from
                                t2 = day_timimg[0].hour_to
                                t3 = day_timimg[1].hour_from
                                t4 = day_timimg[1].hour_to
                                if (date_today == day_week):                            
                                    if ((now_time >= t1) and (now_time <= t2)) or ((now_time >= t3) and (now_time <= t4)):
                                        not_working_time = True
                            else:
                                if (date_today == day_week):
                                    not_working_time = True
        return not_working_time



    def get_clinic_description(self):
        content = '''
            <p>Le cabinet vétérinaire Le Haillan du réseau Argos est situé au 284 avenue Pasteur. 
            Facilement accessible, vous pouvez vous y rendre en voiture comme en transport en commun. Le cabinet dispose d’un parking avec plusieurs places et une borne de recharge GREEN’UP pour les véhicules électriques.
             L’arrêt de bus Sainte Christine, situé devant le parking du cabinet, est desservi par la ligne de bus 3. </p>
            <p>Notre cabinet vétérinaire est à la fois calme et chaleureux pour accueillir au mieux vos compagnons à quatre pattes. Equipé avec du matériel performant et de qualité, nous assurons les consultations courantes dans une salle de consultation lumineuse et moderne.</p>
        '''
        return content


class OperatingUnitTesting(models.Model):
    _name = 'operating.unit'
    _inherit = ['operating.unit','portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin','rating.mixin']