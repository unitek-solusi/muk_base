###################################################################################
#
#    Copyright (C) 2017 MuK IT GmbH
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import os
import base64
import logging
from odoo import exceptions
from odoo.tests import common
_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)
class SuspendSecurityTestCase(common.TransactionCase):
    at_install = False
    post_install = True
    def setUp(self):
        super(SuspendSecurityTestCase, self).setUp()
    def tearDown(self):
        super(SuspendSecurityTestCase, self).tearDown()
    def test_suspend_security(self):
        user_id = self.env.ref('base.user_demo').id
        other_company = self.env['res.company'].create({
            'name': 'other company',
            # without this, a partner is created and mail's constraint on
            # notify_email kicks in
            'partner_id': self.env.ref('base.partner_demo').id,
        })
        with self.assertRaises(exceptions.AccessError):
            self.env.ref('base.user_root').sudo(user_id).name = 'test'
        with self.assertRaises(exceptions.AccessError):
            other_company.sudo(user_id).name = 'test'
        self.env.ref('base.user_root').sudo(user_id).suspend_security().name = 'test'
        self.assertEqual(self.env.ref('base.user_root').name, 'test')
        self.assertEqual(self.env.ref('base.user_root').write_uid.id, user_id)
        # this tests ir.rule
        other_company.sudo(user_id).suspend_security().write({'name': 'test'})
        self.assertEqual(other_company.name, 'test')
        self.assertEqual(other_company.write_uid.id, user_id)
        # this tests if _normalize_args conversion works
        self.env['res.users'].browse(
            self.env['res.users'].suspend_security().env.uid)
        # Test normal search on One2many
        partner = self.env['res.partner'].search(
            [('user_ids.id', '=', self.env.user.suspend_security().env.uid)],
            limit=1)
        self.assertEqual(partner, self.env.user.partner_id)
        # Test search on One2many without specifing ID (standard Odoo)
        partner = self.env['res.partner'].search(
            [('user_ids', '=', self.env.uid)],
            limit=1)
        self.assertEqual(partner, self.env.user.partner_id)
        # Test search on One2many without specifing ID (suspend_security)
        partner = self.env['res.partner'].search(
            [('user_ids', '=', self.env.user.suspend_security().env.uid)],
            limit=1)
        self.assertEqual(partner, self.env.user.partner_id)
        # Test search on One2many without ID with IN (standard Odoo)
        partner = self.env['res.partner'].search(
            [('user_ids', 'in', self.env.uid)],
            limit=1)
        self.assertEqual(partner, self.env.user.partner_id)
        # Test search on One2many without ID with IN (suspend_security)
        partner = self.env['res.partner'].search(
            [('user_ids', 'in', self.env.user.suspend_security().env.uid)],
            limit=1)
        self.assertEqual(partner, self.env.user.partner_id)
    def test_normalize(self):
        self.env['res.users'].browse(self.env['res.users'].suspend_security().env.uid)
