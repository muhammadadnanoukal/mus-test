from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError


class BomInherit(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'

    parent_id = fields.Many2one('mrp.bom', string='Template BOM', index=True)
    child_ids = fields.One2many('mrp.bom', 'parent_id', string='Variants BOM', domain=[('active', '=', True)])

    @api.model
    def create(self, vals):

        res = super().create(vals)
        if res.parent_id:
            return res

        template = res.product_tmpl_id
        for prod in template.product_variant_ids:
            values = {'product_id': prod.id, 'parent_id': res.id}
            copy = res.copy(default=values)
            print("variant ", prod.name, copy.product_id)

        return res

    def unlink(self):
        for ch in self.child_ids:
            ch.unlink()
        super(BomInherit, self).unlink()

    def write(self, vals):

        write_result = super(BomInherit, self).write(vals)

        for ch in self.child_ids:
            ch.write(vals)

        return write_result

    def action_show_boms(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("altanmia_eva_production.action_variant_bom")
        action['domain'] = [('parent_id','=', self.id)]
        return action