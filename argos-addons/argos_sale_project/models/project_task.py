# -*- coding: utf-8 -*-

import logging
import re
import io
from odoo import api, fields, models, _
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from xml.dom import minidom
from odoo.exceptions import Warning, ValidationError

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    type = fields.Selection([('internal', 'Internal'), ('external', 'External'), ('outsourcing', 'Outsourcing')],
                            'Analysis Type', default='internal')
    task_type = fields.Selection([('analysis', 'Analysis'), ('imagery', 'Imagery')], 'Exam Type')
    order_id = fields.Many2one('sale.order', 'Order')
    patient_id = fields.Many2one(related='order_id.patient_id')
    species_id = fields.Many2one(related='patient_id.species_id')
    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment')
    note = fields.Char('Note')
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting'), ('done', 'Done')],
                             default='draft', string='Exam State')
    task_id = fields.Many2one('project.task', 'Analysis Request')
    result_ids = fields.One2many('project.task', 'task_id', 'Result')
    result_line_ids = fields.One2many('project.task.line', 'task_id', 'Result Lines')
    result_date = fields.Datetime('Result Date', default=lambda self: fields.Datetime.now())
    comments = fields.Char('Comments')
    imagery = fields.Binary('Imagery')

    def action_open_result(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_id': self.result_ids.id,
            'res_model': 'project.task',
            'views': [[self.env.ref('argos_sale_project.project_task_result_view_form').id, 'form']],
            'context': {'create': False},
        }

    @api.model
    def format_filename(self, filename=''):
        new_filename = re.sub('[^\w ]+', '', filename)
        return new_filename

    def send_xml_file(self):
        self.ensure_one()
        xml = Element('lab-request', device=self.equipment_id.name)
        order = SubElement(xml, 'order-no')
        species = SubElement(xml, 'species-id')
        description = SubElement(xml, 'description')
        params = SubElement(xml, 'params')
        order.text = str(self.id)
        species.text = str(self.species_id.scil_species_id)
        description.text = '{}'.format(self.note if self.note else '')
        for param in self.tag_ids:
            name = SubElement(params, 'name')
            name.text = param.name
        rough_string = ET.tostring(xml, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        xml_data = io.StringIO()
        reparsed.writexml(xml_data, addindent='\t', newl='\n')
        ftp = self.env.ref('argos_sale_project.server_ftp_request_scil', raise_if_not_found=False)
        equipment = self.format_filename(self.equipment_id.name)
        filename = '%s/%s_%s.xml' % (ftp.filename, equipment, self.id)
        ftp.store_data(filename, xml_data)

    def button_launch_analysis(self):
        self.ensure_one()
        if self.type in ['outsourcing', 'external']:
            action = self.env.ref('purchase.purchase_rfq').read()[0]
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            return action
        if self.equipment_id:
            try:
                _logger.info(_('Sending request ...'))
                if self.task_type == 'analysis':
                    self.send_xml_file()
                self.write({'state': 'waiting'})
                _logger.info(_('Request successfully sent ...'))
            except Exception as e:
                raise Warning(repr(e))
        return True

    def extract_file(self, content):
        self.ensure_one()
        tree = ET.fromstring(content)
        if tree.tag == 'lab-result':
            for child in tree:
                if child.tag == 'order-no':
                    result_id = int(child.text)
                    if result_id == self.id:
                        self.set_result(tree)
                        return True
                    break
        return False

    def set_result(self, tree):
        self.ensure_one()
        value = {
            'name': _('Result - ') + self.name,
            'task_id': self.id,
            'task_type': self.task_type,
            'order_id': self.order_id.id,
            'equipment_id': self.equipment_id.id,
        }
        task = self.create(value)
        for child in tree:
            if child.tag == 'date':
                task.result_date = child.text.replace('T', ' ')
            elif child.tag == 'results':
                for result in child:
                    line_vals = {}
                    for param in result:
                        if param.tag in ['name', 'value', 'min', 'max', 'unit']:
                            line_vals[param.tag] = param.text
                    self.env['project.task.line'].create_result_line(task.id, line_vals)
        self.write({'state': 'done'})

    def button_get_result(self):
        self.ensure_one()
        _logger.info(_('Recovering result ...'))
        ftp_server = self.env.ref('argos_sale_project.server_ftp_result_scil', raise_if_not_found=False)
        ftp = ftp_server.connect()
        ftp.cwd('%s' %(ftp_server.filename))
        file_list = ftp.nlst()
        for file in file_list:
            try:
                if file.endswith('.xml'):
                    path = '%s/%s' %(ftp_server.filename, file)
                    content = ftp_server.retrieve_file_data(path).decode('utf-8')
                    result = self.extract_file(content)
                    if result:
                        break
            except Exception as e:
                raise Warning(repr(e))
        ftp.close()
        if not result:
            raise ValidationError(_('Result not yet available.'))
