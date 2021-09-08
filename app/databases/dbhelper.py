# coding: utf-8
# SUTD WTH SQL Helper
# Created by James Raphael Tiovalen (2020)

# Import libraries
import sqlalchemy
from sqlalchemy import Column, DateTime, String, Text, DDL, event, and_
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import sum, coalesce
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func

# Set up a thread-safe scoped session
from sqlalchemy.orm import scoped_session, sessionmaker

import settings
import decimal
import datetime
import json
import ast
import statistics
from itertools import groupby
from operator import itemgetter

# Define percentages of the four criterias
CRIT_1 = settings.PERCENTAGES[0]
CRIT_2 = settings.PERCENTAGES[1]
CRIT_3 = settings.PERCENTAGES[2]
CRIT_4 = settings.PERCENTAGES[3]


# JSON encoder function for SQLAlchemy special classes
def alchemyencoder(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)


# Main database class (SQLAlchemy ORM implementation is resistant to SQL injection)
class DBHelper:
    engine = sqlalchemy.create_engine(settings.DB_URL)
    Base = declarative_base()
    metadata = Base.metadata

    # Define General SQLAlchemy Model

    class Credentials(Base):
        __tablename__ = "credentials"

        username = Column(VARCHAR(256), primary_key=True, nullable=False)
        password = Column(VARCHAR(256), nullable=False)

    class Judge(Base):
        __tablename__ = "judge"

        # This ID is the judge's Slack user ID (instead of UUID)
        judge_id = Column(VARCHAR(36), primary_key=True, nullable=False)
        name = Column(Text, nullable=False)

        def __repr__(self):
            return f"<Judge ID: {self.judge_id}>"

    class CategoryGroup(Base):
        __tablename__ = "category_group"

        category_group_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        category_id = Column(VARCHAR(36), nullable=False)
        group_id = Column(VARCHAR(36), nullable=False)

        def __repr__(self):
            return f"<Category Group ID: {self.category_group_id}>"

    class CategoryJudge(Base):
        __tablename__ = "category_judge"

        category_judge_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        category_id = Column(VARCHAR(36), nullable=False)
        judge_id = Column(VARCHAR(36), nullable=False)

        def __repr__(self):
            return f"<Category Judge ID: {self.category_judge_id}>"

    class CategoryParticipant(Base):
        __tablename__ = "category_participant"

        category_participant_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        category_id = Column(VARCHAR(36), nullable=False)
        participant_id = Column(VARCHAR(36), nullable=False)

        def __repr__(self):
            return f"<Category Participant ID: {self.category_participant_id}>"

    class CompetitionCategory(Base):
        __tablename__ = "competition_category"

        category_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        name = Column(Text, nullable=False)

        def __repr__(self):
            return f"<Category ID: {self.category_id}>"

    class Consumable(Base):
        __tablename__ = "consumable"

        consumable_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        name = Column(Text, nullable=False)
        description = Column(Text)
        stock_qty = Column(INTEGER(11), nullable=False)
        total_qty = Column(INTEGER(11), nullable=False)
        quota_per_group = Column(INTEGER(11), nullable=False)

        def __repr__(self):
            return f"<Consumable ID: {self.consumable_id}>"

    class ConsumableGroup(Base):
        __tablename__ = "consumable_group"

        consumable_group_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        group_id = Column(VARCHAR(36), nullable=False)
        consumable_id = Column(VARCHAR(36), nullable=False)
        qty = Column(INTEGER(11), nullable=False)

        def __repr__(self):
            return f"<Consumable Group ID: {self.consumable_group_id}>"

    class Group(Base):
        __tablename__ = "group"

        group_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        name = Column(Text, nullable=False)
        group_leader_id = Column(VARCHAR(36), nullable=False)
        space = Column(Text)
        submission_url = Column(VARCHAR(2083))
        hack_submitted = Column(TINYINT(4), nullable=False, default=0)
        utensils_returned = Column(TINYINT(4), nullable=False, default=0)

        def __repr__(self):
            return f"<Group ID: {self.group_id}>"

    class Loan(Base):
        __tablename__ = "loan"

        loan_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        tool_id = Column(VARCHAR(36), nullable=False)
        loan_to_group_id = Column(VARCHAR(36), nullable=False)
        loan_datetime = Column(DateTime, nullable=False)

        def __repr__(self):
            return f"<Loan ID: {self.loan_id}>"

    class Score(Base):
        __tablename__ = "score"

        score_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        category_id = Column(VARCHAR(36), nullable=False)
        judge_id = Column(VARCHAR(36), nullable=False)
        group_id = Column(VARCHAR(36), nullable=False)
        criteria_1_score = Column(INTEGER(11), nullable=False)
        criteria_2_score = Column(INTEGER(11), nullable=False)
        criteria_3_score = Column(INTEGER(11), nullable=False)
        criteria_4_score = Column(INTEGER(11), nullable=False)
        notes_filepath = Column(Text)

        def __repr__(self):
            return f"<Score ID: {self.score_id}>"

    class Tool(Base):
        __tablename__ = "tool"

        tool_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        loaned = Column(TINYINT(4), nullable=False)
        name = Column(Text, nullable=False)
        description = Column(Text)
        latest_loan = Column(VARCHAR(36))

        def __repr__(self):
            return f"<Tool ID: {self.tool_id}>"

    class Participant(Base):
        __tablename__ = "participant"

        participant_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        name = Column(Text, nullable=False)
        contact_number = Column(Text, nullable=False)
        email = Column(Text, nullable=False)
        group_id = Column(VARCHAR(36))
        registered = Column(TINYINT(4), nullable=False)
        DoB = Column(DateTime, nullable=False)
        gender = Column(Text, nullable=False)
        nationality = Column(Text, nullable=False)
        organisation_id = Column(VARCHAR(36), nullable=False)
        designation = Column(Text, nullable=False)
        dietary_pref = Column(Text, nullable=False)
        NoK_id = Column(VARCHAR(36), nullable=False)
        shirt_size = Column(Text, nullable=False)
        previous_hackathons_attended = Column(Text, nullable=False)
        bringing_utensils = Column(Text, nullable=False)
        team_allocation_preference = Column(Text, nullable=False)
        utensil_color = Column(Text)
        created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
        last_modified = Column(
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            onupdate=func.now(),
        )

        def __repr__(self):
            return f"<Participant ID: {self.participant_id}>"

    class ParticipantOrganisation(Base):
        __tablename__ = "participant_organisation"

        organisation_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        organisation_name = Column(Text, nullable=False)
        participant_id = Column(VARCHAR(36), nullable=False)
        created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
        last_modified = Column(
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            onupdate=func.now(),
        )

        def __repr__(self):
            return f"<Organisation ID: {self.organisation_id}>"

    class ParticipantNextOfKin(Base):
        __tablename__ = "participant_next_of_kin"

        NoK_id = Column(
            VARCHAR(36), primary_key=True, nullable=False, default=func.uuid()
        )
        NoK_name = Column(Text, nullable=False)
        NoK_contact_number = Column(Text, nullable=False)
        NoK_relationship = Column(Text, nullable=False)
        participant_id = Column(VARCHAR(36), nullable=False)
        created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
        last_modified = Column(
            DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            onupdate=func.now(),
        )

        def __repr__(self):
            return f"<Participant Next Of Kin ID: {self.NoK_id}>"

    class ParticipantPreferenceTechnologyofInterest(Base):
        __tablename__ = "_participant_preference_toi"

        technology_of_interest_id = Column(
            VARCHAR(36), primary_key=True, nullable=False
        )
        name = Column(Text, nullable=False)

        def __repr__(self):
            return f"<Participant Preference Technology of Interest ID: {self.technology_of_interest_id}>"

    class ParticipantPreferenceTechnologyofInterestParticipant(Base):
        __tablename__ = "_participant_preference_toi_participant"

        technology_of_interest_participant_id = Column(
            VARCHAR(36), primary_key=True, nullable=False
        )
        technology_of_interest_id = Column(VARCHAR(36), nullable=False)
        participant_id = Column(VARCHAR(36), nullable=False)

        def __repr__(self):
            return f"<Participant Preference Technology of Interest Participant ID: {self.technology_of_interest_participant_id}>"

    class ParticipantPreferenceSkills(Base):
        __tablename__ = "_participant_preference_skills"

        skills_id = Column(VARCHAR(36), primary_key=True, nullable=False)
        name = Column(Text, nullable=False)

        def __repr__(self):
            return f"<Participant Preference Skills ID: {self.skills_id}>"

    class ParticipantPreferenceSkillsParticipant(Base):
        __tablename__ = "_participant_preference_skills_participant"

        skills_participant_id = Column(VARCHAR(36), primary_key=True, nullable=False)
        skills_id = Column(VARCHAR(36))
        other_skills = Column(Text)
        participant_id = Column(VARCHAR(36), nullable=False)

        def __repr__(self):
            return f"<Participant Preference Skills Participant ID: {self.skills_participant_id}>"

    class ParticipantPreferenceUtensilName(Base):
        __tablename__ = "_participant_preference_utensil_name"

        utensil_name_id = Column(VARCHAR(36), primary_key=True, nullable=False)
        name = Column(Text, nullable=False)

        def __repr__(self):
            return f"<Participant Preference Utensil Name ID: {self.utensil_name_id}>"

    class ParticipantPreferenceUtensilNameParticipant(Base):
        __tablename__ = "_participant_preference_utensil_name_participant"

        utensil_name_participant_id = Column(
            VARCHAR(36), primary_key=True, nullable=False
        )
        utensil_name_id = Column(VARCHAR(36), nullable=False)
        participant_id = Column(VARCHAR(36), nullable=False)

        def __repr__(self):
            return f"<Participant Preference Utensil Name Participant ID: {self.utensil_name_participant_id}>"

    class ParticipantPreferenceWorkshops(Base):
        __tablename__ = "_participant_preference_workshops"

        workshops_id = Column(VARCHAR(36), primary_key=True, nullable=False)
        name = Column(Text, nullable=False)

        def __repr__(self):
            return f"<Participant Preference Workshops ID: {self.workshops_id}>"

    class ParticipantPreferenceWorkshopsParticipant(Base):
        __tablename__ = "_participant_preference_workshops_participant"

        workshops_participant_id = Column(VARCHAR(36), primary_key=True, nullable=False)
        workshops_id = Column(VARCHAR(36), nullable=False)
        participant_id = Column(VARCHAR(36), nullable=False)
        level_of_preference = Column(INTEGER(11), nullable=False)

        def __repr__(self):
            return f"<Participant Preference Workshops Participant ID: {self.workshops_participant_id}>"

    # Define triggers
    event.listen(
        CategoryGroup.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.%(table)s_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        CategoryJudge.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.%(table)s_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        CategoryParticipant.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.%(table)s_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        CompetitionCategory.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.category_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        Consumable.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.%(table)s_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        ConsumableGroup.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.%(table)s_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    # This is a special hacky workaround since "group" is a reserved keyword in PyMySQL
    event.listen(
        Group.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER group_trigger BEFORE INSERT ON `group` FOR EACH ROW SET NEW.group_id = UUID(), NEW.hack_submitted = 0, NEW.utensils_returned = 0;"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        Loan.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.%(table)s_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        Score.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.%(table)s_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        Tool.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.%(table)s_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        Participant.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.%(table)s_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    # Different column names compared to table names
    event.listen(
        ParticipantOrganisation.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.organisation_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        ParticipantNextOfKin.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.NoK_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        ParticipantPreferenceTechnologyofInterest.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.technology_of_interest_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        ParticipantPreferenceTechnologyofInterestParticipant.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.technology_of_interest_participant_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        ParticipantPreferenceSkills.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.skills_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        ParticipantPreferenceSkillsParticipant.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.skills_participant_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        ParticipantPreferenceUtensilName.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.utensil_name_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        ParticipantPreferenceUtensilNameParticipant.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.utensil_name_participant_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        ParticipantPreferenceWorkshops.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.workshops_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )
    event.listen(
        ParticipantPreferenceWorkshopsParticipant.__table__,
        "after_create",
        DDL(
            """CREATE TRIGGER %(table)s_trigger BEFORE INSERT ON %(table)s FOR EACH ROW SET NEW.workshops_participant_id = UUID();"""
        ).execute_if(dialect="mysql"),
    )

    # Create the model in the SQL database if the tables do not exist yet (conditional by default)
    metadata.create_all(engine)

    # Initiate session factory
    session_factory = sessionmaker(bind=engine)

    # All calls to Session() will create a thread-local session
    # Remember to call .remove() on Session, not session
    Session = scoped_session(session_factory)

    # Define helper functions

    def get_all_categories(self):
        session = self.Session()

        categories = session.query(self.CompetitionCategory.name).all()

        self.Session.remove()

        return sorted([category for sublist in categories for category in sublist])

    def add_all_categories(self):
        session = self.Session()

        try:
            for category in settings.CATEGORIES:
                session.add(self.CompetitionCategory(name=category))
                session.commit()
        # This is important for modification queries
        except:
            session.rollback()
            raise
        finally:
            session.close()

        self.Session.remove()

    def get_all_judges(self):
        session = self.Session()

        judges = session.query(self.Judge.judge_id).all()

        self.Session.remove()

        return sorted([judge for sublist in judges for judge in sublist])

    def get_category_id(self, category_name):
        session = self.Session()

        category = (
            session.query(self.CompetitionCategory.category_id)
            .filter(self.CompetitionCategory.name == category_name)
            .all()
        )

        self.Session.remove()

        return category[0][0]

    def get_category_name(self, category_id):
        session = self.Session()

        category = (
            session.query(self.CompetitionCategory.name)
            .filter(self.CompetitionCategory.category_id == category_id)
            .all()
        )

        self.Session.remove()

        return category[0][0]

    def get_group_id(self, group_name):
        session = self.Session()

        group = (
            session.query(self.Group.group_id)
            .filter(self.Group.name == group_name)
            .all()
        )

        self.Session.remove()

        return group[0][0]

    def get_group_name(self, group_id):
        session = self.Session()

        group = (
            session.query(self.Group.name).filter(self.Group.group_id == group_id).all()
        )

        self.Session.remove()

        return group[0][0]

    def add_judge(self, user_id, name):
        session = self.Session()

        try:
            session.add(
                self.Judge(
                    judge_id=user_id,
                    name=name,
                )
            )
            session.commit()
        # This is important for modification queries
        except:
            session.rollback()
            raise
        finally:
            session.close()

        self.Session.remove()

    def add_judge_category(self, user_id, category_name):
        session = self.Session()

        # Prepare category_id
        category_id = self.get_category_id(category_name)

        try:
            session.add(
                self.CategoryJudge(
                    judge_id=user_id,
                    category_id=category_id,
                )
            )
            session.commit()
        # This is important for modification queries
        except:
            session.rollback()
            raise
        finally:
            session.close()

        self.Session.remove()

    def build_leaderboard(self, category_name):
        session = self.Session()

        # Prepare category_id
        category_id = self.get_category_id(category_name)

        # Join Group and Score tables using group_id, filter based on category_id, then select these 7 columns (as subquery)
        score_list = (
            session.query(
                self.Group.group_id,
                self.Group.name,
                self.Score.category_id,
                self.Score.criteria_1_score,
                self.Score.criteria_2_score,
                self.Score.criteria_3_score,
                self.Score.criteria_4_score,
            )
            .join(self.Score, self.Group.group_id == self.Score.group_id)
            .filter(self.Score.category_id == category_id)
            .subquery()
        )

        # Select group names and average scores as namedtuples for all criterias
        result = (
            session.query(
                score_list.c.name,
                func.avg(score_list.c.criteria_1_score).label("criteria_1"),
                func.avg(score_list.c.criteria_2_score).label("criteria_2"),
                func.avg(score_list.c.criteria_3_score).label("criteria_3"),
                func.avg(score_list.c.criteria_4_score).label("criteria_4"),
            )
            .group_by(score_list.c.name)
            .all()
        )

        # Insert percentage of each criteria here
        actual_result = (
            (
                group_name,
                (decimal.Decimal(CRIT_1) * first)
                + (decimal.Decimal(CRIT_2) * second)
                + (decimal.Decimal(CRIT_3) * third)
                + (decimal.Decimal(CRIT_4) * fourth),
            )
            for group_name, first, second, third, fourth in result
        )

        # Sort list in descending order of score
        final_result = sorted(actual_result, key=lambda x: x[1], reverse=True)

        self.Session.remove()

        return json.dumps(final_result, default=alchemyencoder)

    # Get all teams judgeable by the specified judge
    def get_all_teams(self, judge_id):
        session = self.Session()
        temp_judge_categories = sorted(
            session.query(self.Judge.name, self.CompetitionCategory.name)
            .join(
                self.CategoryJudge, self.Judge.judge_id == self.CategoryJudge.judge_id
            )
            .join(
                self.CompetitionCategory,
                self.CategoryJudge.category_id == self.CompetitionCategory.category_id,
            )
            .filter(self.Judge.judge_id == judge_id)
            .all(),
            key=lambda x: x[1],
        )
        # Group categories for the specified judge together in a list based on first element of tuple
        categories = [
            (name, [category for _, category in categories])
            for name, categories in groupby(temp_judge_categories, itemgetter(0))
        ]

        # Check if list is empty
        if not categories:
            self.Session.remove()

            return []

        else:
            main_list = []
            allowed_categories = sorted(categories[0][1])
            team_list = sorted(
                session.query(self.Group.name, self.CompetitionCategory.name)
                .join(
                    self.CategoryGroup,
                    self.Group.group_id == self.CategoryGroup.group_id,
                )
                .join(
                    self.CompetitionCategory,
                    self.CategoryGroup.category_id
                    == self.CompetitionCategory.category_id,
                )
                .all(),
                key=lambda x: x[1],
            )
            # Group categories for each team together in a list based on first element of tuple
            actual_team_list = [
                (name, [category for _, category in categories])
                for name, categories in groupby(team_list, itemgetter(0))
            ]

            for i in range(len(actual_team_list)):
                name = actual_team_list[i][0]
                category = actual_team_list[i][1]

                # Check if both lists share any elements
                if not set(allowed_categories).isdisjoint(category):
                    main_list.append(name)

            self.Session.remove()

            return sorted(main_list)

    # Get a list of the categories of a specific team to be judged
    def get_categories(self, judge_id, group_name):
        session = self.Session()

        # Prepare group_id
        group_id = self.get_group_id(group_name)

        temp_judge_categories = sorted(
            session.query(self.Judge.name, self.CompetitionCategory.name)
            .join(
                self.CategoryJudge, self.Judge.judge_id == self.CategoryJudge.judge_id
            )
            .join(
                self.CompetitionCategory,
                self.CategoryJudge.category_id == self.CompetitionCategory.category_id,
            )
            .filter(self.Judge.judge_id == judge_id)
            .all(),
            key=lambda x: x[1],
        )

        # Group categories for the specified judge together in a list based on first element of tuple
        judge_categories = [
            (name, [category for _, category in categories])
            for name, categories in groupby(temp_judge_categories, itemgetter(0))
        ][0][1]
        temp_group_categories = (
            session.query(self.Group.group_id, self.CompetitionCategory.name)
            .join(
                self.CategoryGroup, self.Group.group_id == self.CategoryGroup.group_id
            )
            .join(
                self.CompetitionCategory,
                self.CategoryGroup.category_id == self.CompetitionCategory.category_id,
            )
            .filter(self.Group.group_id == group_id)
            .all()
        )
        # Group categories for the specified group together in a list based on first element of tuple
        actual_group_categories = [
            (name, [x for _, x in categories])
            for name, categories in groupby(temp_group_categories, itemgetter(0))
        ]
        group_categories = sorted(actual_group_categories[0][1])

        # Get common elements of both lists
        categories = sorted(list(set(group_categories).intersection(judge_categories)))

        self.Session.remove()

        return categories

    # Commit a score to the database
    def add_score(
        self,
        judge_id,
        group_name,
        category_name,
        criteria_1_score,
        criteria_2_score,
        criteria_3_score,
        criteria_4_score,
    ):
        session = self.Session()

        # Prepare group_id and category_id
        group_id = self.get_group_id(group_name)
        category_id = self.get_category_id(category_name)

        try:
            session.add(
                self.Score(
                    judge_id=judge_id,
                    group_id=group_id,
                    category_id=category_id,
                    criteria_1_score=criteria_1_score,
                    criteria_2_score=criteria_2_score,
                    criteria_3_score=criteria_3_score,
                    criteria_4_score=criteria_4_score,
                )
            )
            session.commit()
        # This is important for modification queries
        except:
            session.rollback()
            raise
        finally:
            session.close()

        self.Session.remove()

    # Append the remarks image URL to the score commit
    def add_remarks(self, judge_id, group_id, path):
        session = self.Session()

        try:
            session.query(self.Score).filter(
                and_(self.Score.judge_id == judge_id, self.Score.group_id == group_id)
            ).update({self.Score.notes_filepath: path}, synchronize_session=False)
            session.commit()
        # This is important for modification queries
        except:
            session.rollback()
            raise
        finally:
            session.close()

        self.Session.remove()

    # Get all scores of a specific category committed by the specified judge for editing purposes
    def get_all_scores(self, judge_id, category_name):
        session = self.Session()

        # Prepare category_id
        category_id = self.get_category_id(category_name)

        scoreboard = (
            session.query(
                self.Score.group_id,
                self.Score.criteria_1_score,
                self.Score.criteria_2_score,
                self.Score.criteria_3_score,
                self.Score.criteria_4_score,
                self.Score.notes_filepath,
            )
            .filter(
                and_(
                    self.Score.judge_id == judge_id,
                    self.Score.category_id == category_id,
                )
            )
            .all()
        )

        self.Session.remove()

        return sorted(scoreboard, key=lambda x: x[0])

    # Check for existence of submitted scores in Score table
    def check_score_existence(self, judge_id):
        session = self.Session()

        scores = (
            session.query(self.Score.score_id)
            .filter(self.Score.judge_id == judge_id)
            .all()
        )

        self.Session.remove()

        return bool(scores)

    # Return a list of the teams that have been judged by a specific judge
    def get_judged_teams(self, judge_id):
        session = self.Session()

        judged_groups = (
            session.query(self.Score.group_id)
            .filter(self.Score.judge_id == judge_id)
            .all()
        )

        name_list = []
        for group in judged_groups:
            name = self.get_group_name(group[0])
            name_list.append(name)

        self.Session.remove()

        return sorted(list(set(name_list)))

    # Return a list of the categories that have been judged by a specific judge
    def get_judged_categories(self, judge_id):
        session = self.Session()

        judged_categories = (
            session.query(self.Score.category_id)
            .filter(self.Score.judge_id == judge_id)
            .all()
        )

        main_categories = list(set(judged_categories))

        self.Session.remove()

        return sorted([category for sublist in main_categories for category in sublist])

    # Obtain specific score row
    def get_specific_score(self, judge_id, group_name, category_name):
        session = self.Session()

        # Prepare group_id and category_id
        group_id = self.get_group_id(group_name)
        category_id = self.get_category_id(category_name)

        category_score = (
            session.query(
                self.Score.criteria_1_score,
                self.Score.criteria_2_score,
                self.Score.criteria_3_score,
                self.Score.criteria_4_score,
            )
            .filter(
                and_(
                    self.Score.judge_id == judge_id,
                    self.Score.group_id == group_id,
                    self.Score.category_id == category_id,
                )
            )
            .all()
        )

        self.Session.remove()

        return category_score[0]

    # Obtain specific remark
    def get_specific_remark(self, judge_id, group_name):
        session = self.Session()

        # Prepare group_id
        group_id = self.get_group_id(group_name)

        category_score = (
            session.query(self.Score.notes_filepath)
            .filter(
                and_(
                    self.Score.judge_id == judge_id,
                    self.Score.group_id == group_id,
                )
            )
            .all()
        )

        self.Session.remove()

        return category_score[0][0]
