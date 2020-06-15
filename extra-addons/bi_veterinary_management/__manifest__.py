# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Veterinary Practice Management System in Odoo ',
    'version' : '13.0.0.0',
    'summary': 'App for Medical Veterinary Appointment Laboratory Pet information Healthcare unit animal healthcare pet healthcare animal clinics vet hospital Veterinary Practice Management veterinary practice clinic veterinary clinic veterinary hospital vet dispensary',
    'category': 'Industries',
    'description': """This module is used to manage Veterinary with Pet information Management, Appointment Management, Laboratory Management, ICU Management, Invoices Management (Invoice in Pet Owners name ), Pediatrics Management, Stock Management.
This module is used to manage Hospital Mangement.
    Also use for manage the healthcare management, Clinic management, Medical Management
    Doctor's Clinic. Clinic software health-care.
    medical Veterinary pet Veterinary management medical pet Veterinary system Veterinary medical management system 
    vet manager veterinary practice animal clinic management 

veterinary practice Hospital Management System
    Healthcare Management System
    Clinic Management System
    Appointment Management System
     animal clinics
     animal clinic
     vet hospital 
     veterinary practice
    Veterinary Practice Management
     animal clinics
     veterinary practice clinic
     veterinary clinic
     veterinary hospital 
    vet dispencary
    Vet clinic
    Animal Hospital
    health care
""" ,
    'data': [
                'security/veterinary_groups.xml',
                'data/ir_sequence_data.xml',
                'views/main_menu_file.xml',
                'views/medical_appointment.xml',
                'wizard/medical_imaging_test_request_wizard.xml',
                'wizard/multiple_test_request_wizard.xml',
                'wizard/appointment_start_end_wizard.xml',
                'wizard/appointment_wizard.xml',
                'wizard/medical_appointments_invoice_wizard.xml',
                'wizard/medical_bed_transfer_wizard.xml',
                'wizard/create_prescription_invoice_wizard.xml',
                'wizard/create_prescription_shipment_wizard.xml',
                'views/medical_medicament.xml',
                'views/medical_dose_unit.xml',
                'views/medical_drug_form.xml',
                'views/medical_drug_route.xml',
                'views/medical_speciality.xml',
                'views/medical_drugs_recreational.xml',
                'views/medical_ethnicity.xml',
                'views/medical_family_code.xml',
                'views/medical_family_disease.xml',
                'views/medical_domiciliary_unit.xml',
                'views/medical_genetic_risk.xml',
                'wizard/medical_health_service_invoice_wizard.xml',
                'views/medical_health_service_line.xml',
                'views/medical_health_service.xml',
                'views/medical_hospital_bed.xml',
                'views/medical_hospital_building.xml',
                'views/medical_hospital_operating_room.xml',
                'views/medical_hospital_unit.xml',
                'views/medical_hospital_ward.xml',
                'views/medical_inpatient_registration.xml',
                'views/medical_inpatient_icu.xml',
                'views/medical_icu_apache2.xml',
                'views/medical_icu_ecg.xml',
                'views/medical_icu_glasgow.xml',
                'views/medical_imaging_test_request.xml',
                'views/medical_imaging_test_result.xml',
                'views/medical_imaging_test_type.xml',
                'views/medical_imaging_test.xml',
                'views/medical_insurance_plan.xml',
                'views/medical_insurance.xml',
                'wizard/medical_lab_test_create_wizard.xml',
                'wizard/medical_lab_test_invoice_wizard.xml',
                'views/medical_lab_test_units.xml',
                'views/medical_lab.xml',
                'views/medical_newborn.xml',
                'views/medical_occupation.xml',
                'views/medical_operation.xml',
                'views/medical_operational_area.xml',
                'views/medical_operational_sector.xml',
                'views/medical_paper_archive.xml',
                'views/medical_pathology_category.xml',
                'views/medical_pathology_group.xml',
                'views/medical_pathology.xml',
                'views/medical_patient_ambulatory_care.xml',
                'views/medical_patient_disease.xml',
                'views/medical_patient_evaluation.xml',
                'views/medical_patient_lab_test.xml',
                'views/medical_patient_medication.xml',
                'views/medical_patient_pregnency.xml',
                'views/medical_patient_prental_evolution.xml',
                'views/medical_patient_psc.xml',
                'views/medical_patient_rounding.xml',
                'views/medical_patient.xml',
                'views/medical_physician.xml',
                'views/medical_preinatal.xml',
                'views/medical_prescription_line.xml',
                'views/medical_prescription_order.xml',
                'views/medical_procedure.xml',
                'views/medical_puerperium_monitor.xml',
                'views/medical_rcri.xml',
                'views/medical_surgey.xml',
                'views/medical_rounding_procedure.xml',
                'views/medical_test_critearea.xml',
                'views/medical_test_type.xml',
                'views/medical_vaccination.xml',
                'views/medicament_category.xml',
                'views/pet_breed.xml',
                'views/pet_type.xml',
                'views/res_partner.xml',
                'report/appointment_recipts_report_template.xml',
                'report/medical_view_report_document_lab.xml',
                'report/medical_view_report_lab_result_demo_report.xml',
                'report/patient_card_report.xml',
                'report/patient_diseases_document_report.xml',
                'report/patient_medications_document_report.xml',
                'report/patient_vaccinations_document_report.xml',
                'report/prescription_demo_report.xml',
                'report/report_view.xml',
                'security/ir.model.access.csv',

        ],
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'price': 239,
    'currency': "EUR",
    'depends' : ['sale_management','account_payment','stock', 'account'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/U8FNbTT9pFQ',
    "images":['static/description/Banner.png'],
    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
