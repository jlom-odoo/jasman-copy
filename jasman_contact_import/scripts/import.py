from xmlrpc import client
import pandas as pd
import numpy as np
import locale

# Configuration
db_url = "http://localhost:8069"
db = '17.0-jasman'
username = 'admin'
password = 'admin'

# XMLRPC - Common
common = client.ServerProxy('{}/xmlrpc/2/common'.format(db_url))
uid = common.authenticate(db, username, password, {})

# XMLRPC - Models
models = client.ServerProxy('{}/xmlrpc/2/object'.format(db_url), )

# Locale config
locale.setlocale(locale.LC_ALL, '')

def import_contact(raw_data, warnings: list):
    data = {
        'jasman_id': raw_data['Cuenta'],
        'name': raw_data['Nombre (Razón Social sin S.A. de C.V.)'],
        'company_type': raw_data['Tipo de registro'],
        'ref': raw_data['Nombre de búsqueda'],
        'street': raw_data['Calle + Número de calle + Número Interior'],
        'street2': raw_data['Colonia'],
        'zip': raw_data['Código Postal'],
        'city': raw_data['Municipio'],
        'comment': raw_data['Complemento'],
        'phone': raw_data['Teléfono'],
        'email': raw_data['Correo electrónico'],
        'use_partner_credit_limit': raw_data['Tipo de pago'],
        'credit_limit': locale.atof(raw_data['Límite de crédito']),
        'pay_day': raw_data['Días de pago'],
        'payment_reference': raw_data['Referencia'],
        'sale_warn': raw_data['Facturación y entrega (Venta)'],
        'invoice_warn': raw_data['Facturación y entrega (Factura)'],
        'vat': raw_data['RFC'], 
        'l10n_mx_edi_fiscal_regime': str(raw_data['Régimen Fiscal']),
        'l10n_mx_edi_usage': raw_data['Propósito de uso del CFDI'],
        'state_id': import_state_id(raw_data['Estado'], warnings),
        'country_id': import_country_id(raw_data['País'], warnings),
        'property_account_position_id': import_property_account_position_id(raw_data['Tipo de empresa'], warnings),
        'property_product_pricelist': import_product_pricelist_id(raw_data['Grupo de precios'], warnings),
        'property_payment_term_id': import_payment_term_id(raw_data['Condiciones de pago'], warnings),
        'user_id': import_user_id(raw_data['Vendedor'], []), # Do not add warnings,
        'invoice_user_id': import_user_id(raw_data['Ejecutivo de cobranza'], []), # Do not add warnings
        'channel_analytic_account_id': import_channel_analytic_account_id(raw_data['Clasificación del cliente (D-Canal)'], warnings),
        # DELETED
        # 'property_delivery_carrier_id': import_delivery_carrier_id(raw_data['Tipo de entrega'], warnings),
        # 'confirm_delivery': raw_data['Cita para entrega'],
        # 'guarantee_expiry': raw_data['Límite de garantía'],
        # 'contract_expiry': raw_data['Vigencia de contrato'],
    }
    # Checks
    if data['name'] is False or data['name'] is None or data['name'] == '':
        raise BaseException(f"Invalid contact name {data['name']}")
    if data['l10n_mx_edi_fiscal_regime'] not in ('601', '603', '605', '606', '607', '608', '609', '610', '611', '612', '614', '615', '616', '620', '621', '622', '623', '624', '625', '626', '628', '629', '630'):
        raise BaseException(f"Invalid edi regime {data['l10n_mx_edi_fiscal_regime']}")
    if data['l10n_mx_edi_usage'] not in (False, 'G01', 'GO2', 'G03', 'IO1', 'I02', 'I04', 'I05', 'I06', 'I07', 'I08', 'D01', 'DO2', 'D03', 'D04', 'D05', 'D06', 'D07', 'D08', 'D09', 'D10', 'S01'):
        raise BaseException(f"Invalid edi usage {data['l10n_mx_edi_usage']}")

    return data


cached_state_ids = {}
def import_state_id(state_name, warnings: list):
    # Get state full names
    if state_name == "Coahuila de Zaragosa":
        state_name = "Coahuila"
    if state_name == "Michoacán de Ocampo":
        state_name = "Michoacán"
    if state_name == "Veracruz de Ignacio de la Llave":
        state_name = "Veracruz"
    # Get from db if not in cache
    if cached_state_ids.get(state_name) is None:
        state_id = models.execute_kw(db, uid, password, 'res.country.state', 'search', [[('name', '=', state_name)]])
        cached_state_ids[state_name] = state_id[0] if state_id else False
    # If not exists
    if cached_state_ids.get(state_name) is False:
        warnings.append(f"State ({state_name}) does not exist")
    return cached_state_ids[state_name]

cached_country_ids = {}
def import_country_id(country_name, warnings: list):
    # Get from db if not in cache 
    if cached_country_ids.get(country_name) is None:
        country_id = models.execute_kw(db, uid, password, 'res.country', 'search', [[('display_name', '=', country_name)]])
        cached_country_ids[country_name] = country_id[0] if country_id else False
    # If not exists
    if cached_country_ids.get(country_name) is False:
        warnings.append(f"Country ({country_name}) does not exist")
    return cached_country_ids[country_name]

cached_channel_analytic_account_ids = {}
def import_channel_analytic_account_id(analytic_account_name, warnings: list):
    # Get from db if not in cache
    if cached_channel_analytic_account_ids.get(analytic_account_name) is None:
        # TODO: Check if name or code
        analytic_account_id = models.execute_kw(db, uid, password, 'account.analytic.account', 'search', [[('name', '=', analytic_account_name)]])
        cached_channel_analytic_account_ids[analytic_account_name] = analytic_account_id[0] if analytic_account_id else False
    # If not exists
    if cached_channel_analytic_account_ids.get(analytic_account_name) is False:
        warnings.append(f"Channel analytic account ({analytic_account_name}) does not exist")
    return cached_channel_analytic_account_ids[analytic_account_name]

cached_account_position_ids = {}
def import_property_account_position_id(position_name, warnings: list):
    # Get from db if not in cache
    if cached_account_position_ids.get(position_name) is None:
        position_id = models.execute_kw(db, uid, password, 'account.fiscal.position', 'search', [[('name', '=', position_name)]])
        cached_account_position_ids[position_name] = position_id[0] if position_id else False
    # If not exists
    if cached_account_position_ids.get(position_name) is False:
        warnings.append(f"Property account position ({position_name}) does not exist")
    return cached_account_position_ids[position_name]

cached_product_pricelist_ids = {}
def import_product_pricelist_id(pricelist_name, warnings: list):
    # Get from db if not in cache
    if cached_product_pricelist_ids.get(pricelist_name) is None:
        pricelist_id = models.execute_kw(db, uid, password, 'product.pricelist', 'search', [[('name', 'ilike', pricelist_name)]],
        {'context': {'lang': 'es_MX'}})
        cached_product_pricelist_ids[pricelist_name] = pricelist_id[0] if pricelist_id else False
    # If not exists
    if cached_product_pricelist_ids.get(pricelist_name) is False:
        warnings.append(f"Pricelist ({pricelist_name}) does not exist")
    return cached_product_pricelist_ids[pricelist_name]

cached_payment_term_ids = {}
def import_payment_term_id(payment_term_name, warnings: list):
    # Get from db if not in cache
    if cached_payment_term_ids.get(payment_term_name) is None:
        payment_term_id = models.execute_kw(db, uid, password, 'account.payment.term', 'search', [[('name', 'ilike', payment_term_name)]], 
        {'context': {'lang': 'es_MX'}})
        cached_payment_term_ids[payment_term_name] = payment_term_id[0] if payment_term_id else False
    # If not exists
    if cached_payment_term_ids.get(payment_term_name) is False:
        warnings.append(f"Account payment term ({payment_term_name}) does not exist")
    return cached_payment_term_ids[payment_term_name]

cached_user_ids = {}
def import_user_id(user_name, warnings: list):
    # Get from db if not in cache
    if cached_user_ids.get(user_name) is None:
        user_id = models.execute_kw(db, uid, password, 'res.users', 'search', [[('name', '=', user_name)]])
        cached_user_ids[user_name] = user_id[0] if user_id else False
    # If not exists
    if cached_user_ids.get(user_name) is False:
        warnings.append(f"User ({user_name}) does not exist")
    return cached_user_ids[user_name]

cached_delivery_carrier_ids = {}
def import_delivery_carrier_id(carrier_name, warnings: list):
    # Get from db if not in cache
    if cached_delivery_carrier_ids.get(carrier_name) is None:
        carrier_id = models.execute_kw(db, uid, password, 'delivery.carrier', 'search', [[('name', '=', carrier_name)]])
        cached_delivery_carrier_ids[carrier_name] = carrier_id[0] if carrier_id else False
    # If not exists
    if cached_delivery_carrier_ids.get(carrier_name) is False:
        warnings.append(f"Delivery carrier ({carrier_name}) does not exist")
    return cached_delivery_carrier_ids[carrier_name]

def import_from_csv(csv_path, out_csv_path):
    failed_rows = []
    rows_to_commit = []
    df = pd.read_csv(csv_path).replace(np.nan, False)
    for i, row in df.iterrows():
        id = row['Cuenta']
        warnings = []
        try:
            contact = import_contact(row, warnings)
            # models.execute_kw(db, uid, password, 'res.partner', 'create', [contact])
            rows_to_commit.append(contact)
            if len(warnings) > 0:
                failed_rows.append({
                    'id': id, 
                    'warnings': ";".join(warnings), 
                    'errors': ''
                })
            print(f"Row {i} (warnings {len(warnings)})")
        except BaseException as e:
            failed_rows.append(({
                'id': id, 
                'errors': e,
                'warnings': ";".join(warnings)
            }))
            print(f"Row {i} ERROR {e}")
        
        if i%500 == 0:
            try:
                models.execute_kw(db, uid, password, 'res.partner', 'create', [rows_to_commit])
            except BaseException as e:
                print(f"Range {i-500} - {i} ERROR {e}")
                return
            rows_to_commit = []
    failed_rows_df = pd.DataFrame(failed_rows)
    failed_rows_df.to_csv(out_csv_path)

import_from_csv("jasman_contact_import/data3.csv", "jasman_contact_import/out.csv")
