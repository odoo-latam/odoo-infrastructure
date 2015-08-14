# -*- coding: utf-8 -*-
from openerp import fields, api, models


class infrastructure_restore_database_wizard(models.TransientModel):
    _name = "infrastructure.restore_database.wizard"
    _description = "Infrastructure Restore Database Wizard"

    def _get_database_backup(self):
        dump_id = self.env.context.get('active_id', False)
        return self.env['infrastructure.database.backup'].browse(dump_id)

    def _get_create_date(self):
        d = self._get_database_backup()
        return d.create_date

    def _get_server_id(self):
        d = self._get_database_backup()
        return d.database_id.server_id

    def _get_environment_id(self):
        d = self._get_database_backup()
        return d.database_id.instance_id.environment_id

    def _get_instance_id(self):
        d = self._get_database_backup()
        return d.database_id.instance_id

    def _get_database_id(self):
        d = self._get_database_backup()
        return d.database_id

    database_backup_id = fields.Many2one(
        'infrastructure.database.backup',
        string='Dump File',
        default=_get_database_backup,
        readonly=True
    )
    create_date = fields.Datetime(
        string='Created On',
        default=_get_create_date,
        readonly=True,
    )
    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        default=_get_server_id,
        required=True,
        readonly=False
    )
    environment_id = fields.Many2one(
        'infrastructure.environment',
        string='Environment',
        default=_get_environment_id,
        required=True,
        readonly=False
    )
    instance_id = fields.Many2one(
        'infrastructure.instance',
        string='Instance',
        default=_get_instance_id,
        required=True,
        readonly=False
    )
    database_type_id = fields.Many2one(
        'infrastructure.database_type',
        string='Database Type',
        required=True,
    )
    new_db_name = fields.Char(
        string='New db Name',
        required=True
        )
    # TODO ver si incorporamos la posibilidad de que se sobreescriba a la misma bd en la que estamos parados
    # el tema es que actualmente usamos dicha bd para restaurar a traves de database_tools por lo cual no andaria
    # overwrite_active = fields.Boolean(
    #     string='Overwrite Active Database?',
    #     default=False
    # )
    backups_enable = fields.Boolean(
        'Backups Enable on new DB?'
    )

    @api.one
    @api.onchange('environment_id')
    def change_environment(self):
        self.instance_id = False

    @api.onchange('database_type_id')
    def onchange_database_type_id(self):
        if self.database_type_id:
            self.new_db_name = self.database_type_id.prefix + '_'
            # TODO send suggested backup data

    @api.one
    def restore_database(self):
        self.database_backup_id.restore(
            self.new_db_name, self.backups_enable, self.database_type_id)
        return True
