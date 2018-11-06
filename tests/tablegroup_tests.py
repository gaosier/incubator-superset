# -*- coding:utf-8 -*-
# __author__ = majing

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

from superset import db
from superset.connectors.sqla.models_ext import SqlTableGroup
from tests.base_tests import SupersetTestCase


class TableGroupTests(SupersetTestCase):

    requires_examples = True

    def __init__(self, *args, **kwargs):
        super(TableGroupTests, self).__init__(*args, **kwargs)

    def setUp(self):
        self.instances = []
        group_1 = SqlTableGroup(name='用户数据中心', sort_id=1, parent_id=0)
        group_2 = SqlTableGroup(name='学科数据中心', sort_id=2, parent_id=0)
        group_3 = SqlTableGroup(name='学科机构数据中心', sort_id=1, parent_id=2)
        group_4 = SqlTableGroup(name='学科城市数据中心', sort_id=2, parent_id=2)
        group_5 = SqlTableGroup(name='基础数据中心', sort_id=3, parent_id=0)
        self.instances = [group_1, group_2, group_3, group_4, group_5]
        db.session.add_all(self.instances)
        db.session.commit()

    def tearDown(self):
        for item in self.instances:
            db.session.delete(item)
            db.session.commit()

    def test_menus(self):
        self.login(username='alpha')

        resp = self.get_resp('tablegroupview/menu/0')
        print("resp.data: ", resp)


if __name__ == '__main__':
    unittest.main()
