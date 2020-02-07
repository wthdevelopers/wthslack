# coding: utf-8
# This file holds important Firebase functions for tracking conversations
# Created by James Raphael Tiovalen (2020)


# Import libraries
from google.cloud import firestore
import os
import settings
import config


class FireConn:
    # Establish Firestore Client connection
    def __init__(self):
        self.db = firestore.Client()

    # Define atomic functions
    # Note that Firestore does not have any default rate-limiting by design (limiting billing is not an option)

    def get_state(self, channel_id, user_id):
        try:
            state = (
                self.db.collection("conversations")
                .document(f"{str(channel_id)}")
                .get()
                .to_dict()[f"{str(user_id)}"]["state"]
            )
            return state

        except (TypeError, KeyError) as e:
            status = config.db.check_score_existence(user_id)
            if status:
                self.db.collection("conversations").document(f"{str(channel_id)}").set(
                    {f"{str(user_id)}": {"state": config.CONVERSATION_END}}, merge=True
                )
                return config.INITIAL_STATE

            else:
                self.db.collection("conversations").document(f"{str(channel_id)}").set(
                    {f"{str(user_id)}": {"state": config.INITIAL_STATE}}, merge=True
                )
                return config.INITIAL_STATE

    def change_state(self, channel_id, user_id, state):
        self.db.collection("conversations").document(f"{str(channel_id)}").set(
            {f"{str(user_id)}": {"state": state}}, merge=True
        )

    def get_ts(self, channel_id, user_id):
        try:
            ts = (
                self.db.collection("conversations")
                .document(f"{str(channel_id)}")
                .get()
                .to_dict()[f"{str(user_id)}"]["timestamp"]
            )
            return ts

        except (TypeError, KeyError) as e:
            return None

    def change_ts(self, channel_id, user_id, ts):
        self.db.collection("conversations").document(f"{str(channel_id)}").set(
            {f"{str(user_id)}": {"timestamp": ts}}, merge=True
        )

    def change_state_ts(self, channel_id, user_id, state, ts):
        self.db.collection("conversations").document(f"{str(channel_id)}").set(
            {f"{str(user_id)}": {"state": state, "timestamp": ts}}, merge=True
        )
