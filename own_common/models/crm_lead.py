from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    x_base_currency_id = fields.Many2one(
        'res.currency', 'Base Currency', compute='_x_compute_base_currency', compute_sudo=True
    )
    x_solution_revenue = fields.Monetary('Solution Revenue', 'x_base_currency_id')
    x_final_solution_revenue = fields.Monetary(
        'Final Solution Revenue',
        'x_base_currency_id',
        compute='_compute_final_solution_revenue',
        readonly=True,
        store=True,
    )
    x_solution_revenue_tax = fields.Many2one(
        'account.tax', string='Solution Revenue Tax', domain=[('type_tax_use', '=', 'sale')]
    )
    x_solution_revenue_tax_amount = fields.Monetary(
        'Solution Tax', 'x_base_currency_id', compute='_x_compute_solution_revenue_tax_amount', store=True
    )
    x_wht_solution = fields.Many2one('account.tax', string='WHT Tax', domain=[('type_tax_use', '=', 'sale')])
    x_wht_solution_amount = fields.Monetary('WHT Solution', 'x_base_currency_id', compute='_x_compute_wht', store=True)

    x_solution_cost = fields.Monetary('Solution Cost', 'x_base_currency_id')
    x_nrt_applicable = fields.Many2one(
        'account.tax', string='NRT Type', domain=[('type_tax_use', '=', 'purchase')], default=None
    )
    # x_nrt = fields.Monetary('NRT', 'x_base_currency_id', compute='_x_compute_x_nrt', store=True)
    x_nrt = fields.Monetary('NRT', 'x_base_currency_id', compute='_x_compute_nrt', store=True)
    x_gp_on_license = fields.Monetary(
        'GP On License', 'x_base_currency_id', compute='_x_compute_gp_on_license', store=True
    )

    x_service_revenue = fields.Monetary('Service Revenue', 'x_base_currency_id')
    x_service_revenue_tax = fields.Many2one(
        'account.tax', string='Service Revenue Tax', domain=[('type_tax_use', '=', 'sale')]
    )
    x_service_revenue_tax_amount = fields.Monetary(
        'Service Tax', 'x_base_currency_id', compute='_x_compute_service_revenue_tax_amount', store=True
    )
    x_final_service_revenue = fields.Monetary(
        'Final Service Revenue',
        'x_base_currency_id',
        compute='_x_compute_final_service_revenue',
        readonly=True,
        store=True,
    )
    x_wht_service = fields.Many2one('account.tax', string='WHT Service', domain=[('type_tax_use', '=', 'sale')])
    x_wht_service_amount = fields.Monetary(
        'WHT Service Amount', 'x_base_currency_id', compute='_x_compute_wht', readonly=True, store=True
    )
    x_gp_on_services = fields.Monetary(
        'GP On Services', 'x_base_currency_id', compute='_x_compute_gp_on_services', store=True
    )

    x_total_project_gp = fields.Monetary(
        'Total Project GP', 'x_base_currency_id', compute='_x_compute_total_project_gp', store=True
    )
    x_total_deal_value = fields.Monetary(
        'Total Deal Value', 'x_base_currency_id', compute='_x_compute_total_deal_value', store=True
    )
    x_gp = fields.Text('GP', compute='_x_compute_gp', store=True)
    x_commission = fields.Monetary('Commission', 'x_base_currency_id', compute='_x_compute_commission', store=True)
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
        'x_wht_solution_amount',
        'x_wht_solution',
        'x_final_solution_revenue',
        'x_wht_service_amount',
        'x_wht_service',
        'x_final_service_revenue',
    )
    def _x_compute_wht(self):
        for lead_id in self:
            solution_rate = abs(lead_id.x_wht_solution.amount if lead_id.x_wht_solution else 0)
            service_rate = abs(lead_id.x_wht_service.amount if lead_id.x_wht_service else 0)
            lead_id.x_wht_solution_amount = (
                lead_id.x_final_solution_revenue * (solution_rate / 100) if solution_rate else 0
            )
            lead_id.x_wht_service_amount = lead_id.x_final_service_revenue * (service_rate / 100) if service_rate else 0

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
        'x_wht_solution_amount',
        'x_solution_revenue',
        'x_nrt',
        'x_solution_revenue_tax',
    )
    def _x_compute_gp_on_license(self):
        for lead_id in self:
            lead_id.x_gp_on_license = (
                (
                    lead_id.x_final_solution_revenue
                    - lead_id.x_wht_solution_amount
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

    @api.depends('x_gp_on_services', 'x_final_service_revenue', 'x_service_revenue', 'x_wht_service_amount')
    def _x_compute_gp_on_services(self):
        for lead_id in self:
            lead_id.x_gp_on_services = (
                (
                    lead_id.x_final_service_revenue
                    - (lead_id.x_service_revenue * lead_id.x_service_revenue_tax.amount / 100)
                    - lead_id.x_wht_service_amount
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
            lead_id.expected_revenue = lead_id.x_solution_revenue + lead_id.x_service_revenue

    @api.depends(
        'x_gp', 'x_total_project_gp', 'x_total_deal_value', 'x_solution_revenue', 'x_service_revenue', 'x_solution_cost'
    )
    def _x_compute_gp(self):
        for lead_id in self:
            lead_id.x_gp = (
                f'{round(100 * (lead_id.x_total_project_gp / lead_id.x_total_deal_value), 2)} %'
                if lead_id.x_total_deal_value != 0
                else 0
            )

    @api.depends('x_commission', 'x_total_deal_value', 'x_commission_percentage')
    def _x_compute_commission(self):
        for lead_id in self:
            lead_id.x_commission = lead_id.x_total_project_gp * (lead_id.x_commission_percentage / 100)

    @api.depends('partner_id', 'email_from', 'phone', 'company_id')
    def _x_compute_base_currency(self):
        for record in self:
            record.x_base_currency_id = self.env.ref('base.USD')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for lead_id in self:
            lead_id.x_base_currency_id = self.env.ref('base.USD')
        return res
