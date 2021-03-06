"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from datetime import datetime

from cloudcafe.compute.common.constants import Constants
from cloudroast.stacktach.fixtures import StackTachComputeIntegration,\
    StackTachTestAssertionsFixture


class StackTachDBServerResizeUpRevertTests(StackTachComputeIntegration,
                                           StackTachTestAssertionsFixture):
    """
    @summary: With Server Resize Up (e.g. from flavor 2 -> 3) then
      Revert (i.e., cancelling the resize so flavor 3 -> 2),
      tests the entries created in StackTach DB.
    """

    @classmethod
    def setUpClass(cls):
        cls.create_server()
        cls.resize_server()
        cls.revert_resize_server()
        cls.audit_period_beginning = \
            datetime.utcnow().strftime(Constants.DATETIME_0AM_FORMAT)

        cls.stacktach_events_for_server(server=cls.reverted_resized_server)
        cls.event_launch_resize_server = cls.event_launches[1]
        cls.event_launch_revert_resize = cls.event_launches[2]
        cls.event_exist_resize_server = cls.event_exists[0]
        cls.event_exist_revert_resize_server = cls.event_exists[1]

    def test_launch_entry_on_revert_resize_up_server_response(self):
        """
        Verify the Launch parameters are being returned in the
        Server Revert Resize Up response
        """
        # There should be 3 launch entries for a revert resize.
        self.validate_attributes_in_launch_response(num_of_launch_entry=3)

    def test_launch_entry_fields_on_create_server(self):
        """
        Verify that the first Launch entry will have all expected fields
        before a Server Resize Up
        """
        self.validate_launch_entry_field_values(
            server=self.created_server)

    def test_launch_entry_fields_on_resize_up(self):
        """
        Verify that the second Launch entry will have all expected fields
        after a Server Resize and before a Server Revert Resize Up
        """
        self.validate_launch_entry_field_values(
            server=self.verify_resized_server,
            event_launch_server=self.event_launch_resize_server,
            expected_flavor_ref=self.flavor_ref_alt,
            launched_at=self.launched_at_resized_server)

    def test_launch_entry_fields_on_revert_resize_up(self):
        """
        Verify that the third Launch entry will have all expected fields
        after a Server Revert Resize Up
        """

        self.validate_launch_entry_field_values(
            server=self.reverted_resized_server,
            event_launch_server=self.event_launch_revert_resize,
            launched_at=self.launched_at_revert_resize_server)

    def test_exist_entry_on_revert_resize_up_server_response(self):
        """
        Verify the Exist parameters are correct after a Server Revert Resize Up
        """
        # There should be 2 immediate exists entries for a revert resize.
        self.validate_attributes_in_exist_response(num_of_exist_entry=2)

    def test_exists_entry_fields_on_resize_up(self):
        """
        Verify that the First exists entry will have all expected fields
        on the first Server Resize; before Server Revert Resize Up
        """
        self.validate_exist_entry_field_values(
            server=self.created_server)
        self.validate_exist_entry_audit_period_values(
            expected_audit_period_ending=self.resize_start_time,
            expected_audit_period_beginning=self.audit_period_beginning)

    def test_exist_launched_at_field_match_on_resize_up(self):
        """
        Verify that the first Exists entry launched_at matches the
        Launch entry launched_at for a Server Resize Up
        """
        self.assertEqual(
            self.event_launch.launched_at,
            self.event_exist_resize_server.launched_at,
            self.msg.format("launched_at",
                            self.event_launch.launched_at,
                            self.event_exist_resize_server.launched_at,
                            self.exist_response.reason,
                            self.exist_response.content))

    def test_exists_entry_fields_on_revert_resize_up(self):
        """
        Verify that the Second Exist entry will have all expected fields
        after Server Revert Resize Up
        """
        self.validate_exist_entry_field_values(
            server=self.verify_resized_server,
            event_exist_server=self.event_exist_revert_resize_server,
            expected_flavor_ref=self.flavor_ref_alt,
            launched_at=self.launched_at_resized_server)
        self.validate_exist_entry_audit_period_values(
            expected_audit_period_ending=self.revert_resize_start_time,
            expected_audit_period_beginning=self.audit_period_beginning,
            event_exist_server=self.event_exist_revert_resize_server)

    def test_exist_launched_at_field_match_on_revert_resize_up(self):
        """
        Verify that the second Exists entry launched_at matches the
        Launch entry launched_at for a Server Revert Resize Up
        """
        self.assertEqual(
            self.event_launch_resize_server.launched_at,
            self.event_exist_revert_resize_server.launched_at,
            self.msg.format("launched_at",
                            self.event_launch_resize_server.launched_at,
                            self.event_exist_revert_resize_server.launched_at,
                            self.exist_response.reason,
                            self.exist_response.content))

    def test_no_delete_entry_on_revert_resize_up_server_response(self):
        """
        Verify that there is no delete entry after a Server Revert Resize
        """
        self.validate_no_deletes_entry_returned()
