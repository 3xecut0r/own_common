from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    x_base_currency_id = fields.Many2one(
        'res.currency', 'Base Currency', compute='_x_compute_base_currency', store=True
    )
    x_solution_revenue = fields.Monetary('Solution Revenue', 'company_currency')
    x_final_solution_revenue = fields.Monetary(
        'Final Solution Revenue',
        'company_currency',
        compute='_compute_final_solution_revenue',
        readonly=True,
        store=True,
    )
    x_solution_revenue_tax = fields.Many2one(
        'account.tax', string='Solution Revenue Tax', domain=[('type_tax_use', '=', 'sale')]
    )
    x_solution_revenue_tax_amount = fields.Monetary(
        'Solution Tax', 'company_currency', compute='_x_compute_solution_revenue_tax_amount', store=True
    )
    x_wht_solution = fields.Monetary(
        'WHT Solution', 'company_currency', compute='_x_compute_wht', readonly=True, store=True
    )

    x_solution_cost = fields.Monetary('Solution Cost', 'company_currency')
    x_nrt_applicable = fields.Many2one(
        'account.tax', string='NRT Type', domain=[('type_tax_use', '=', 'purchase')], default=None
    )
    # x_nrt = fields.Monetary('NRT', 'company_currency', compute='_x_compute_x_nrt', store=True)
    x_nrt = fields.Monetary('NRT', 'company_currency', compute='_x_compute_nrt', store=True)
    x_gp_on_license = fields.Monetary(
        'GP On License', 'company_currency', compute='_x_compute_gp_on_license', store=True
    )

    x_service_revenue = fields.Monetary('Service Revenue', 'company_currency')
    x_service_revenue_tax = fields.Many2one(
        'account.tax', string='Service Revenue Tax', domain=[('type_tax_use', '=', 'sale')]
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
        'WHT Service', 'company_currency', compute='_x_compute_wht', readonly=True, store=True
    )
    x_gp_on_services = fields.Monetary(
        'GP On Services', 'company_currency', compute='_x_compute_gp_on_services', store=True
    )

    x_total_project_gp = fields.Monetary(
        'Total Project GP', 'company_currency', compute='_x_compute_total_project_gp', store=True
    )
    x_total_deal_value = fields.Monetary(
        'Total Deal Value', 'company_currency', compute='_x_compute_total_deal_value', store=True
    )
    x_gp = fields.Text('GP', compute='_x_compute_gp', store=True)
    x_commission = fields.Monetary('Commission', 'company_currency', compute='_x_compute_commission', store=True)
    x_commission_percentage = fields.Float('Commission %')

    @api.depends('x_solution_revenue', 'x_solution_revenue_tax', 'x_final_solution_revenue')
    def _compute_final_solution_revenue(self):
        for lead_id in self:
            lead_id.x_final_solution_revenue = (
                lead_id.x_solution_revenue + (lead_id.x_solution_revenue * lead_id.x_solution_revenue_tax.amount / 100)
                if lead_id.x_solution_revenue and lead_id.x_solution_revenue_tax.amount
                else 0
            )

    @api.depends(
        'x_solution_revenue_tax',
        'x_wht_solution',
        'x_final_solution_revenue',
        'x_service_revenue_tax',
        'x_wht_service',
        'x_final_service_revenue',
    )
    def _x_compute_wht(self):
        tax_mapping = {'gst': 5, 'sst': 4, 'srb': 4, 'pra': 4, 'kpra': 4}

        def get_rate(tax):
            for key, value in tax_mapping.items():
                if tax.name and key in tax.name.lower():
                    return value
            return 0

        for lead_id in self:
            lead_id.x_wht_solution = lead_id.x_final_solution_revenue * get_rate(lead_id.x_solution_revenue_tax) / 100
            lead_id.x_wht_service = lead_id.x_final_service_revenue * get_rate(lead_id.x_service_revenue_tax) / 100

    @api.depends('x_solution_cost', 'x_nrt_applicable')
    def _x_compute_nrt(self):
        for lead_id in self:
            lead_id.x_nrt = (
                (lead_id.x_solution_cost * ((lead_id.x_nrt_applicable.amount / 100) if lead_id.x_nrt_applicable else 1))
                if lead_id.x_nrt_applicable.amount
                else 0
            )

    @api.depends(
        'x_solution_cost',
        'x_final_solution_revenue',
        'x_wht_solution',
        'x_solution_revenue',
        'x_nrt',
        'x_solution_revenue_tax',
    )
    def _x_compute_gp_on_license(self):
        for lead_id in self:
            lead_id.x_gp_on_license = (
                (
                    lead_id.x_final_solution_revenue
                    - lead_id.x_wht_solution
                    - (lead_id.x_solution_revenue * (lead_id.x_solution_revenue_tax.amount / 100))
                    - lead_id.x_solution_cost
                    - lead_id.x_nrt
                )
                if lead_id.x_solution_revenue_tax.amount
                else 0
            )

    @api.depends('x_final_service_revenue', 'x_service_revenue', 'x_service_revenue_tax')
    def _x_compute_final_service_revenue(self):
        for lead_id in self:
            lead_id.x_final_service_revenue = (
                lead_id.x_service_revenue + (lead_id.x_service_revenue * lead_id.x_service_revenue_tax.amount / 100)
                if lead_id.x_service_revenue and lead_id.x_service_revenue_tax.amount
                else 0
            )

    @api.depends('x_gp_on_services', 'x_final_service_revenue', 'x_service_revenue', 'x_wht_service')
    def _x_compute_gp_on_services(self):
        for lead_id in self:
            lead_id.x_gp_on_services = (
                (
                    lead_id.x_final_service_revenue
                    - (lead_id.x_service_revenue * lead_id.x_service_revenue_tax.amount / 100)
                    - lead_id.x_wht_service
                )
                / 2
                if lead_id.x_service_revenue_tax.amount
                else 0
            )

    @api.depends('x_solution_revenue_tax_amount', 'x_solution_revenue', 'x_solution_revenue_tax')
    def _x_compute_solution_revenue_tax_amount(self):
        for lead_id in self:
            lead_id.x_solution_revenue_tax_amount = (
                lead_id.x_solution_revenue * lead_id.x_solution_revenue_tax.amount / 100
                if lead_id.x_solution_revenue_tax.amount
                else 0
            )

    @api.depends('x_service_revenue_tax_amount', 'x_service_revenue', 'x_service_revenue_tax')
    def _x_compute_service_revenue_tax_amount(self):
        for lead_id in self:
            lead_id.x_service_revenue_tax_amount = (
                (lead_id.x_service_revenue * lead_id.x_service_revenue_tax.amount / 100)
                if lead_id.x_service_revenue_tax.amount
                else 0
            )

    @api.depends('x_total_project_gp', 'x_gp_on_license', 'x_gp_on_services')
    def _x_compute_total_project_gp(self):
        for lead_id in self:
            lead_id.x_total_project_gp = lead_id.x_gp_on_license + lead_id.x_gp_on_services

    @api.depends('x_total_deal_value', 'x_solution_revenue', 'x_service_revenue')
    def _x_compute_total_deal_value(self):
        for lead_id in self:
            lead_id.x_total_deal_value = lead_id.x_solution_revenue + lead_id.x_service_revenue

    @api.depends(
        'x_gp',
        'x_total_project_gp',
        'x_total_deal_value',
        'expected_revenue',
        'x_solution_revenue',
        'x_service_revenue',
        'x_solution_cost',
    )
    def _x_compute_gp(self):
        for lead_id in self:
            lead_id.x_gp = (
                f'{round(100 * (lead_id.x_total_project_gp / lead_id.x_total_deal_value), 2)} %'
                if lead_id.x_total_deal_value != 0
                else 0
            )
            lead_id.expected_revenue = lead_id.x_solution_revenue + lead_id.x_service_revenue - lead_id.x_solution_cost

    @api.depends('x_commission', 'x_total_deal_value', 'x_commission_percentage')
    def _x_compute_commission(self):
        for lead_id in self:
            lead_id.x_commission = lead_id.x_total_project_gp * (lead_id.x_commission_percentage / 100)

    @api.depends('partner_id', 'email_from', 'phone')
    def _x_compute_base_currency(self):
        for record in self:
            record.x_base_currency_id = self.env.ref('base.USD')
