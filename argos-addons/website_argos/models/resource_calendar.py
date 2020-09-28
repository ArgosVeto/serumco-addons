# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime,date
import pytz


class ResourceCalendar(models.Model):
	_inherit = 'resource.calendar'

	def convert_to_time(self,seconds): 
		min, sec = divmod(seconds, 60) 
		hour, min = divmod(min, 60)
		date_time = str(int(hour)) + "h" + str(int(min))
		return date_time

	# def  get_employee_slot(self,date_today,calendar_id):
	# 	final_vals = {}
	# 	vals = {}
	# 	to_date = date_today
	# 	for date_range in range(0,4):
	# 		to_find_date = to_date + relativedelta(days=date_range)
	# 		date_week_day = to_find_date.weekday()
	# 		day_timimg = calendar_id.attendance_ids.filtered(lambda x:x.dayofweek == str(date_week_day))
	# 		if day_timimg:
	# 			date_content = []
	# 			dt = day_timimg[0].hour_from
	# 			for dc in range(0,3):
	# 				start_hour = dt
	# 				start_hour = self.convert_to_time(start_hour*3600)
	# 				date_content.append(start_hour)
	# 				dt += 0.5
	# 		else:
	# 			date_content = []
	# 			for dc in range(0,3):
	# 				date_content.append('fermé')
	# 		vals.update({to_find_date.strftime("%b %d"):date_content})
	# 	return vals

	def  get_short_employee_slot(self,calendar_id):
		week_slot = {'0':'Lun.','1':'Mar.','2':'Mer','3':'Jeu','4':'Ven.','5':'Sam.','6':'Dim.'}
		working_timing = {}
		date_today = date.today()
		working_day = {}
		count = 0
		not_working_time = False
		if calendar_id:
			attendance_ids = calendar_id.attendance_ids
			if attendance_ids:
				for day_week in range(0,7):
					start_time = 'fermé' 
					end_time = 'fermé'
					day_timimg = attendance_ids.filtered(lambda x:x.dayofweek == str(day_week))
					if day_timimg:
						if len(day_timimg) == 2:
							start_time = self.convert_to_time(day_timimg[0].hour_from * 3600) +' - ' + self.convert_to_time(day_timimg[0].hour_to * 3600)
							end_time = self.convert_to_time(day_timimg[1].hour_from * 3600) +' - ' + self.convert_to_time(day_timimg[1].hour_to * 3600)

						elif len(day_timimg) == 1:
							start_time = self.convert_to_time(day_timimg[0].hour_from * 3600) +' - ' + self.convert_to_time(day_timimg[0].hour_to * 3600)

						elif len(day_timimg) > 2:
							start_time = self.convert_to_time(day_timimg[0].hour_from * 3600) +' - ' + self.convert_to_time(day_timimg[0].hour_to * 3600)
							end_time = self.convert_to_time(day_timimg[1].hour_from * 3600) +' - ' + self.convert_to_time(day_timimg[1].hour_to * 3600)
					time_range = {'start_time':start_time,'end_time':end_time}
					last_value = list(working_timing.values())
					last_key = list(working_timing.keys())
					if last_value and last_key:
						last_value = last_value[-1]
						last_key = last_key[-1]
					if not last_value:
						working_timing.update({week_slot[str(day_week)]:time_range})					
					elif last_value and time_range != last_value:
						working_timing.update({week_slot[str(day_week)]:time_range})
					elif last_value and time_range == last_value:
						store_key = last_key
						working_timing.pop(last_key)
						main_key = store_key.split(' - ')
						working_timing.update({main_key[0] + ' - ' + week_slot[str(day_week)]:time_range})
		return working_timing

	def  get_employee_slot(self,calendar_id):
		week_slot = {'0':'Lun.','1':'Mar.','2':'Mer','3':'Jeu','4':'Ven.','5':'Sam.','6':'Dim.'}
		working_timing = {}
		date_today = date.today()

		not_working_time = False
		if calendar_id:
			attendance_ids = calendar_id.attendance_ids
			if attendance_ids:
				for day_week in range(0,6):
					date_today = date.today()
					now_time = datetime.now()
					date_today = date_today.weekday()
					if date_today == day_week:
						now_time =  pytz.timezone('UTC').localize(now_time).astimezone(pytz.timezone(self.env.user.tz  or 'UTC')).time()
						now_time = now_time.hour + now_time.minute/60.0 + now_time.second/3600
					start_time = 'fermé' 
					end_time = 'fermé'
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
							start_time = self.convert_to_time(day_timimg[0].hour_from * 3600) +' - ' + self.convert_to_time(day_timimg[0].hour_to * 3600)
							end_time = self.convert_to_time(day_timimg[1].hour_from * 3600) +' - ' + self.convert_to_time(day_timimg[1].hour_to * 3600)

						elif len(day_timimg) == 1:
							t1 = day_timimg[0].hour_from
							t2 = day_timimg[0].hour_to
							if (date_today == day_week):
								if (now_time >= t1) and (now_time <= t2):
									not_working_time = True
							start_time = self.convert_to_time(day_timimg[0].hour_from * 3600) +' - ' + self.convert_to_time(day_timimg[0].hour_to * 3600)

						elif len(day_timimg) > 2 and (date_today == day_week):
							t1 = day_timimg[0].hour_from
							t2 = day_timimg[0].hour_to
							t3 = day_timimg[1].hour_from
							t4 = day_timimg[1].hour_to
							if (date_today == day_week):							
								if ((now_time >= t1) and (now_time <= t2)) or ((now_time >= t3) and (now_time <= t4)):
									not_working_time = True
							start_time = self.convert_to_time(day_timimg[0].hour_from * 3600) +' - ' + self.convert_to_time(day_timimg[0].hour_to * 3600)
							end_time = self.convert_to_time(day_timimg[1].hour_from * 3600) +' - ' + self.convert_to_time(day_timimg[1].hour_to * 3600)
						else:
							if (date_today == day_week):
								not_working_time = True
					time_range = {'start_time':start_time,'end_time':end_time}
					working_timing.update({week_slot[str(day_week)]:time_range})
		return working_timing