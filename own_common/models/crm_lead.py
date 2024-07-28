from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    x_solution_revenue = fields.Monetary('Solution Revenue', 'company_currency')
    x_final_solution_revenue = fields.Monetary(
        'Final Solution Revenue',
        'company_currency',
        compute='_compute_final_solution_revenue',
        readonly=True,
        store=True,
    )
    x_solution_revenue_tax = fields.Selection(
        [('gst', 'GST 18%'), ('sst', 'SST 15%'), ('srb', 'SRB 15%'), ('pra', 'PRA 5%'), ('kpra', 'KPRA 5%')],
        'Solution Revenue Tax',
        default='gst',
    )
    x_solution_revenue_tax_percentage = fields.Integer(
        'Solution Revenue Tax Percentage', compute='_compute_tax_percentage', store=True
    )
    x_solution_revenue_tax_amount = fields.Monetary(
        'Solution Tax', 'company_currency', compute='_x_compute_solution_revenue_tax_amount', store=True
    )
    x_wht_solution = fields.Monetary('WHT Solution', compute='_x_compute_wht_solution', readonly=True, store=True)

    x_solution_cost = fields.Monetary('Solution Cost', 'company_currency')
    x_nrt_applicable = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Is NRT Applicable?', default='no')
    x_nrt = fields.Monetary('NRT', 'company_currency', compute='_x_compute_x_nrt', store=True)
    x_gp_on_license = fields.Monetary(
        'GP On License', 'company_currency', compute='_x_compute_gp_on_license', store=True
    )

    x_service_revenue = fields.Monetary('Service Revenue', 'company_currency')
    x_service_revenue_tax = fields.Selection(
        [('gst', 'GST 18%'), ('sst', 'SST 15%'), ('srb', 'SRB 15%'), ('pra', 'PRA 5%'), ('kpra', 'KPRA 5%')],
        'Service Revenue Tax',
        default='gst',
    )
    x_service_revenue_tax_percentage = fields.Integer(
        'Service Revenue Tax Percentage', compute='_compute_tax_percentage', store=True
    )
    x_service_revenue_tax_amount = fields.Monetary(
        'Service Tax', 'company_currency', compute='_x_compute_service_revenue_tax_amount', store=True
    )
    x_final_service_revenue = fields.Monetary(
        'Final Service Revenue',
        'company_currency',
        compute='_x_compute_final_service_revenue',
        readonly=True,
        store=True,
    )
    x_wht_service = fields.Monetary(
        'WHT Service', 'company_currency', compute='_x_compute_wht_service', readonly=True, store=True
    )
    x_gp_on_services = fields.Monetary(
        'GP On Services', 'company_currency', compute='_x_compute_gp_on_services', store=True
    )

    x_total_project_gp = fields.Monetary(
        'Total Project GP', 'company_currency', compute='_x_compute_x_total_project_gp', store=True
    )
    x_total_deal_value = fields.Monetary(
        'Total Deal Value', 'company_currency', compute='_x_compute_x_total_deal_value', store=True
    )
    x_gp = fields.Text('GP', compute='_x_compute_x_gp', store=True)
    x_commission = fields.Text('Commission', compute='_x_compute_commission', store=True)

    @api.depends('x_solution_revenue', 'x_solution_revenue_tax_percentage')
    def _compute_final_solution_revenue(self):
        for lead_id in self:
            lead_id.x_final_solution_revenue = (
                lead_id.x_solution_revenue
                + (lead_id.x_solution_revenue * lead_id.x_solution_revenue_tax_percentage / 100)
                if lead_id.x_solution_revenue and lead_id.x_solution_revenue_tax_percentage
                else 0
            )

    @api.depends('x_solution_revenue_tax', 'x_service_revenue_tax')
    def _compute_tax_percentage(self):
        tax_rates = {'gst': 18, 'sst': 15, 'srb': 15, 'pra': 5, 'kpra': 5}
        for lead_id in self:
            lead_id.x_solution_revenue_tax_percentage = tax_rates.get(lead_id.x_solution_revenue_tax, 0)
            lead_id.x_service_revenue_tax_percentage = tax_rates.get(lead_id.x_service_revenue_tax, 0)

    @api.depends('x_solution_revenue_tax', 'x_final_solution_revenue')
    def _x_compute_wht_solution(self):
        for lead_id in self:
            rate = 4 if lead_id.x_solution_revenue_tax in ('sst', 'srb', 'pra', 'kpra') else 5
            lead_id.x_wht_solution = lead_id.x_final_solution_revenue * rate / 100

    @api.depends('x_solution_cost', 'x_nrt_applicable')
    def _x_compute_x_nrt(self):
        for lead_id in self:
            lead_id.x_nrt = lead_id.x_solution_cost * (0.22 if lead_id.x_nrt_applicable == 'yes' else 1)

    @api.depends(
        'x_solution_cost',
        'x_nrt_applicable',
        'x_final_solution_revenue',
        'x_wht_solution',
        'x_solution_revenue',
        'x_solution_revenue_tax_percentage',
        'x_nrt',
    )
    def _x_compute_gp_on_license(self):
        for lead_id in self:
            lead_id.x_gp_on_license = (
                lead_id.x_final_solution_revenue
                - lead_id.x_wht_solution
                - (lead_id.x_solution_revenue * (lead_id.x_solution_revenue_tax_percentage / 100))
                - lead_id.x_solution_cost
                - lead_id.x_nrt
            )

    @api.depends('x_final_service_revenue', 'x_service_revenue', 'x_service_revenue_tax_percentage')
    def _x_compute_final_service_revenue(self):
        for lead_id in self:
            lead_id.x_final_service_revenue = (
                lead_id.x_service_revenue + (lead_id.x_service_revenue * lead_id.x_service_revenue_tax_percentage / 100)
                if lead_id.x_service_revenue and lead_id.x_service_revenue_tax_percentage
                else 0
            )

    @api.depends('x_wht_service', 'x_service_revenue_tax', 'x_final_service_revenue')
    def _x_compute_wht_service(self):
        for lead_id in self:
            rate = 4 if lead_id.x_service_revenue_tax in ('sst', 'srb', 'pra', 'kpra') else 5
            lead_id.x_wht_service = lead_id.x_final_service_revenue * rate / 100

    @api.depends(
        'x_gp_on_services',
        'x_final_service_revenue',
        'x_service_revenue',
        'x_service_revenue_tax_percentage',
        'x_wht_service',
    )
    def _x_compute_gp_on_services(self):
        for lead_id in self:
            lead_id.x_gp_on_services = (
                lead_id.x_final_service_revenue
                - (lead_id.x_service_revenue * lead_id.x_service_revenue_tax_percentage / 100)
                - lead_id.x_wht_service
            ) / 2

    @api.depends('x_solution_revenue_tax_amount', 'x_solution_revenue_tax_percentage', 'x_solution_revenue')
    def _x_compute_solution_revenue_tax_amount(self):
        for lead_id in self:
            lead_id.x_solution_revenue_tax_amount = (
                lead_id.x_solution_revenue * lead_id.x_solution_revenue_tax_percentage / 100
            )

    @api.depends('x_service_revenue_tax_amount', 'x_service_revenue', 'x_service_revenue_tax_percentage')
    def _x_compute_service_revenue_tax_amount(self):
        for lead_id in self:
            lead_id.x_service_revenue_tax_amount = (
                lead_id.x_service_revenue * lead_id.x_service_revenue_tax_percentage / 100
            )

    @api.depends('x_total_project_gp', 'x_gp_on_license', 'x_gp_on_services')
    def _x_compute_x_total_project_gp(self):
        for lead_id in self:
            lead_id.x_total_project_gp = lead_id.x_gp_on_license + lead_id.x_gp_on_services

    @api.depends('x_total_deal_value', 'x_solution_revenue', 'x_service_revenue')
    def _x_compute_x_total_deal_value(self):
        for lead_id in self:
            lead_id.x_total_deal_value = lead_id.x_solution_revenue + lead_id.x_service_revenue

    @api.depends('x_gp', 'x_total_project_gp', 'x_total_deal_value')
    def _x_compute_x_gp(self):
        for lead_id in self:
            if lead_id.x_total_deal_value != 0:
                lead_id.x_gp = f'{round(100 * (lead_id.x_total_project_gp / lead_id.x_total_deal_value))} %'

    @api.depends('x_commission', 'x_total_deal_value')
    def _x_compute_commission(self):
        for lead_id in self:
            lead_id.x_commission = lead_id.x_total_project_gp * 0.1
