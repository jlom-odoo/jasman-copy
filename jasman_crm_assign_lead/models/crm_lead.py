import geopy.distance

from odoo import api, fields, models

DEFAULT_COUNTRY = "Mexico"


class CrmLead(models.Model):
    _inherit = "crm.lead"

    imported_lead_jasman = fields.Boolean()

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)
        leads.filtered(lambda l: l.imported_lead_jasman and l.zip)._assign_closest_team_by_location()
        return leads

    def _assign_closest_team_by_location(self):
        teams_with_location = self.env["crm.team"].search([("latitude", "!=", False), ("longitude", "!=", False)])
        for lead in self:
            closest_distance = float("inf")
            closest_team = False
            country_name = lead.country_id.name or DEFAULT_COUNTRY

            lead_coordinates = self.env["res.partner"]._geo_localize(
                lead.street, lead.zip, lead.city,
                lead.state_id.name, country_name
            )
            for team in teams_with_location:
                team_coordinates = (team.latitude, team.longitude)
                distance = geopy.distance.distance(team_coordinates, lead_coordinates).km
                if distance < closest_distance:
                    closest_distance = distance
                    closest_team = team

            lead.team_id = closest_team
