#!/usr/bin/env python3

import json
import os
import subprocess
import sys
import textwrap
from copy import deepcopy
from pathlib import Path

import dearpygui.dearpygui as dpg
from reportlab.pdfgen import canvas

from .extra_types import (
    AttributesTab,
    AttributeSubtab,
    CharacterData,
    ExpertisesTab,
    ExpertiseSubtab,
    SkillsSubtab,
    SkillsTab,
    TraitsSubtab,
    TraitsTab,
    ValueType,
)
from .utils import (
    get_character_save_location,
    get_character_template,
    get_pdf_save_location,
)


class CharacterGenerator:
    def __init__(
        self,
        character: CharacterData,
        create_mode: bool,
        extend_character: dict[str, bool],
    ) -> None:
        self._imported_character = character
        self._extend_character = extend_character
        self._current_character = deepcopy(self._imported_character)

        self._serial_properties = self._serialize_properties(
            self._current_character["Character"]
        )
        self._serial_properties.update(
            self._serialize_properties(self._current_character["Character"])
        )
        self._version = 0.1
        self._text_input_width = 200

        self._config = self._current_character["Config"]
        self._player_info = self._current_character["Player Info"]

        self._platoon_alternatives = self._config["platoons"]
        self._speciality_alternatives = self._config["specialities"]
        self._gender_alternatives = self._config["genders"]
        self._rank_alternatives = self._config["Rank Labels"]

        self._create_mode = create_mode
        self._extend_character["background"] = create_mode

        self._section_title_color = [150, 250, 150]

        self._stats: dict[str, ValueType] = {
            "Carry Capacity": {
                "value": 55,
                "tooltip": "Affected by Strength and various Traits.",
            },
            "Combat Load": {
                "value": 25,
                "tooltip": "Affected by Strength and various Traits.",
            },
            "Psycho Limit": {
                "value": 4,
                "tooltip": "Affected by Psyche and various Traits.",
            },
            "Stress Limit": {
                "value": 4,
                "tooltip": "Affected by Psyche and various Traits.",
            },
            "Stunt Cap": {"value": 2, "tooltip": "Affected by Charisma"},
            "Leadership Points": {
                "value": 1,
                "tooltip": "Affected by Charisma and various Traits",
            },
            "Health": {
                "value": 2,
                "tooltip": "Affected by Endurance and various Traits.",
            },
            "Psycho Points": {
                "value": (
                    self._get_base_psycho_points() - self._get_psycho_point_cost()
                ),
                "tooltip": (
                    "Earned when playing and can be reduced by buying "
                    "psychotic disadvantages."
                ),
            },
            "Attribute Points": {"value": self._get_attribute_points()},
            "Extra Attribute Points": {
                "value": self._get_extra_attribute_points(),
                "tooltip": "Additional Attribute Points costing 8 XP per extra point.",
            },
            "Experience Points": {
                "value": (
                    self._get_base_experience_points() - self._get_total_xp_usage()
                )
            },
            "Available Traits": {
                "value": (self._get_base_available_traits() - self._get_count_traits())
            },
        }

        self._serial_properties.update(self._serialize_properties(self._stats))
        self._serial_properties.update(
            self._serialize_properties({"Rank": {"value": self._player_info["Rank"]}})
        )

    def _serialize_properties(self, character: dict):
        properties = dict()
        for key, value in character.items():
            if "value" in character[key]:
                properties.update({key: value})
            else:
                properties.update(self._serialize_properties(character[key]))
        return properties

    def _get_base_attribute_points(self) -> int:
        return self._imported_character["Config"]["Starting AP"]

    def _get_base_experience_points(self) -> int:
        return self._imported_character["Config"]["Starting XP"]

    def _get_base_available_traits(self) -> int:
        return self._imported_character["Config"]["Starting Traits"]

    def _get_base_psycho_points(self) -> int:
        if "Psycho Points" in self._imported_character["Config"].keys():
            imported_pp = self._imported_character["Config"]["Psycho Points"]
        else:
            imported_pp = 0
        return imported_pp

    @staticmethod
    def _get_total_knowledge_cost(skills: SkillsSubtab, default_cost: list[int]) -> int:
        """
        Calulate the xp cost for all skills.
        """
        sum_cost = 0
        for category in skills.values():
            for knowledge in category.values():
                if "cost_table" in knowledge:
                    cost_table = knowledge["cost_table"]
                else:
                    cost_table = default_cost
                sum_cost = sum_cost + cost_table[knowledge["value"]]
        return sum_cost

    def _character_attributes(self):
        return self._current_character["Character"]["Attributes"]["All"]["Attribute"]

    def _get_attribute_value(self, attribute: str) -> int:
        attributes = self._character_attributes()
        return attributes[attribute]["value"]

    def _get_total_attribute_cost(self) -> int:
        sum_points = 0
        for attribute in self._character_attributes().values():
            sum_points = sum_points + attribute["value"]
        return sum_points

    def _get_attribute_points(self) -> int:
        AP = self._get_base_attribute_points() - self._get_total_attribute_cost()
        return max(AP, 0)

    def _get_extra_attribute_points(self) -> int:
        extra_AP = self._get_total_attribute_cost() - self._get_base_attribute_points()
        return max(extra_AP, 0)

    def _get_extra_attribute_point_cost(self) -> int:
        xp_per_ap = 8
        cost = xp_per_ap * self._get_extra_attribute_points()
        return cost

    def _get_total_xp_usage(self) -> int:
        return (
            self._get_total_knowledge_cost(
                skills=self._current_character["Character"]["Skills"]["All"],
                default_cost=self._imported_character["Config"]["skill_cost_table"],
            )
            + self._get_total_property_cost(
                self._current_character["Character"]["Expertise"]
            )
            + self._get_total_property_cost(
                self._current_character["Character"]["Traits"]
            )
            + self._get_extra_attribute_point_cost()
        )

    def _get_count_traits(self) -> int:
        sum_traits = 0
        traits = self._current_character["Character"]["Traits"]
        for main_group in traits:
            for sub_group in traits[main_group]:
                for property in traits[main_group][sub_group].values():
                    if property["value"]:
                        sum_traits = sum_traits + 1
        return sum_traits

    @staticmethod
    def _get_total_property_cost(properties: TraitsTab | ExpertisesTab) -> int:
        """
        Calculate the total cost from boolean poperties .
        For example 'Advantages'.
        """
        sum_cost = 0

        for main_group in properties:
            if main_group != "Psychotic Disadvantages":
                for sub_group in properties[main_group]:
                    for property in properties[main_group][sub_group].values():
                        if property["value"]:
                            sum_cost = sum_cost + property["cost"]
        return sum_cost

    def _get_psycho_point_cost(self) -> int:
        """
        Calculate the total cost of Psychotic Disadvantages.
        """
        properties = self._current_character["Character"]["Traits"]
        trait_tab = properties["Psychotic Disadvantages"]
        sum_cost = 0
        for sub_group in trait_tab:
            for property in trait_tab[sub_group].values():
                if property["value"]:
                    sum_cost = sum_cost + property["cost"]
        return sum_cost

    @staticmethod
    def _wrap_tooltip(tooltip: str) -> str:
        tooltip_width: int = 70

        # Remove multiple whitespaces
        tooltip_str = " ".join(tooltip.split())

        if "Req:" in tooltip_str and not tooltip_str.startswith("Req:"):
            # Put Req on a new line, wrapped separately
            desc_str, req, req_str = tooltip_str.partition("Req:")
            desc_str = textwrap.fill(desc_str, width=tooltip_width)
            req_str = " ".join([req, req_str])
            req_str = textwrap.fill(req_str, width=tooltip_width)
            wrapped_text = "\n".join([desc_str, req_str])
        else:
            wrapped_text = textwrap.fill(tooltip_str, width=tooltip_width)
        return wrapped_text

    def _add_tooltip(self, tooltip_label: str, tooltip_dict: ValueType) -> None:
        if "tooltip" in tooltip_dict:
            tooltip_text = self._wrap_tooltip(tooltip_dict["tooltip"])
            with dpg.tooltip("tooltip_" + tooltip_label):
                dpg.add_text(tooltip_text)

    def _allow_change(self, item: ValueType) -> bool:
        """
        When editing an existing character, boxes are not allowed to be
        unchecked.
        """
        allowed = False
        if self._create_mode or not item["value"]:
            allowed = True
        return allowed

    def _attribute_callback(self, sender, app_data, user_data: dict):
        """
        Triggered when any slider for attribute points have changed.
        """
        self._set_value_and_display_difference(
            property_data=user_data,
            sender=sender,
            new_value=app_data,
        )
        self._update_ap_status()
        self._update_xp_status()
        self._update_psycho_limit()
        self._update_stress_limit()
        self._update_stunt_cap()
        self._update_health_limit()
        self._update_leadership_points()
        self._update_carry_capacity()
        self._update_combat_load()
        self._check_property_disable()

    def _get_value_from_character_state(self, property_data: dict[str, str]) -> int:
        """
        Helper function to get a specific value.
        """
        section = property_data["section"]
        tab = property_data["tab_label"]
        sub_tab = property_data["sub_tab_label"]
        category = property_data["category"]
        label = property_data["label"]
        return self._current_character[section][tab][sub_tab][category][label]["value"]

    def _set_value_in_character_state(self, property_data: dict, new_value: int):
        """
        Helper function to set a specific value.
        """
        section = property_data["section"]
        tab = property_data["tab_label"]
        sub_tab = property_data["sub_tab_label"]
        cat = property_data["category"]
        label = property_data["label"]

        self._current_character[section][tab][sub_tab][cat][label]["value"] = new_value

    def _set_value_and_display_difference(
        self,
        property_data: dict,
        sender: int,
        new_value: int,
    ):
        """
        Helper function that will set the associated value from the slider
        and display the difference compared to the previous saved state.
        """
        self._set_value_in_character_state(
            property_data=property_data,
            new_value=new_value,
        )
        difference = new_value - self._get_value_from_character_state(
            property_data=property_data,
        )

        if difference != 0:
            difference_string = str(difference)
            if difference > 0:
                difference_string = "+" + difference_string

            dpg.set_item_label(item=sender, label=difference_string)
        else:
            dpg.set_item_label(item=sender, label="")

    def _skills_callback(self, sender, app_data, user_data: dict):
        """
        Triggered when any slider for skill points have changed.
        """

        self._set_value_and_display_difference(
            property_data=user_data,
            sender=sender,
            new_value=app_data,
        )
        self._update_xp_status()

    def _property_callback(self, sender, app_data, user_data: dict):
        """
        Triggered when any checkbox for advantages points have changed.
        """
        self._set_value_in_character_state(
            property_data=user_data,
            new_value=app_data,
        )

        self._update_xp_status()
        self._update_pp_status()
        self._check_property_disable()
        self._update_trait_status()
        self._update_stress_limit()
        self._update_overview()

    def _has_requirements(self, property: str) -> bool:
        return "requirements" in self._serial_properties[property]

    @staticmethod
    def _property_is_extended(property: ValueType) -> bool:
        return "extended" in property

    @staticmethod
    def _property_has_value(property: ValueType) -> bool:
        return bool(property["value"])

    def _extension_active(self, property: ValueType) -> bool:
        if self._property_is_extended(property):
            return self._extend_character[property["extended"]]
        else:
            return True

    def _extensions_not_hidden(self, property: str) -> bool:
        if self._property_is_extended(self._serial_properties[property]):
            return self._extension_active(self._serial_properties[property])
        return True

    def _requirements_fulfilled(self, property: str) -> bool:
        reqs: dict = self._serial_properties[property]["requirements"]
        fulfilled = True
        for req_name, req in reqs.items():
            # TODO: An OR option would be useful but not trivial to include
            actual_value: int = self._serial_properties[req_name]["value"]
            if (req["type"] == "==") and (not actual_value == req["value"]):
                fulfilled = False
            if (req["type"] == ">=") and (not actual_value >= req["value"]):
                fulfilled = False
            if (req["type"] == "<=") and (not actual_value <= req["value"]):
                fulfilled = False
        return fulfilled

    def _check_property_disable(self):
        for property in self._serial_properties:
            if self._has_requirements(property) and self._extensions_not_hidden(
                property
            ):
                fulfilled = self._requirements_fulfilled(property)
                dpg.configure_item(property, enabled=fulfilled)

    def _check_active_bonuses(self, target: str) -> list:
        final_bonus = []
        for property in self._serial_properties:
            if "bonus" in self._serial_properties[property]:
                if self._serial_properties[property]["value"] > 0:
                    for bonus in self._serial_properties[property]["bonus"]:
                        if bonus["target"] == target:
                            this_bonus = bonus["value"]
                            if bonus["type"] == "permanent":
                                final_bonus.append(f"{this_bonus:+g}")
                            else:
                                final_bonus.append(f"({this_bonus:+g})")
        return final_bonus

    def _player_info_callback(self, sender, app_data, user_data: dict[str, str]):
        """
        Triggered when changing player info such as name, platoon etc.
        """
        idx = user_data["label"]
        state = self._current_character["Player Info"][idx] = app_data  # noqa: F841
        self._player_info = self._current_character["Player Info"]

    def _update_psycho_limit(self):
        """
        Update the printout of current Psycho limit.
        Must be called whenever a related value have been change.
        """
        psycho_limit = self._get_attribute_value("Psyche")
        self._stats["Psycho Limit"]["value"] = psycho_limit
        dpg.set_value(
            item="Psycho Limit",
            value=psycho_limit,
        )

    def _update_stress_limit(self):
        """
        Update the printout of current Stress limit.
        Must be called whenever a related value have been change.
        """

        stress_limit = self._get_attribute_value("Psyche") * 2
        bonus_string = "".join(self._check_active_bonuses("Stress Limit"))
        self._stats["Stress Limit"]["value"] = stress_limit
        dpg.set_value(
            item="Stress Limit",
            value=f"{stress_limit} {bonus_string}",
        )

    def _update_stunt_cap(self):
        """
        Update the printout of current stunt cap.
        Must be called whenever a related value have been change.
        """

        stunt_cap = self._get_attribute_value("Charisma")
        self._stats["Stunt Cap"]["value"] = stunt_cap
        dpg.set_value(
            item="Stunt Cap",
            value=stunt_cap,
        )

    def _update_health_limit(self):
        """
        Update the printout of current health.
        Must be called whenever a related value have been change.
        """

        health = self._get_attribute_value("Endurance") + 3
        self._stats["Health"]["value"] = health
        dpg.set_value(
            item="Health",
            value=health,
        )

    def _update_carry_capacity(self):
        """
        Update the printout of current carry capacity.
        Must be called whenever a related value have been change.
        """
        idx = self._get_attribute_value("Strength") - 1
        carry_capacity = self._config["Carry Capacity Table"][idx]
        self._stats["Carry Capacity"]["value"] = carry_capacity
        dpg.set_value(
            item="Carry Capacity",
            value=carry_capacity,
        )

    def _update_combat_load(self):
        """
        Update the printout of current combat load.
        Must be called whenever a related value have been change.
        """
        idx = self._get_attribute_value("Strength") - 1
        combat_load = self._current_character["Config"]["Combat Load Table"][idx]
        self._stats["Combat Load"]["value"] = combat_load
        dpg.set_value(
            item="Combat Load",
            value=combat_load,
        )

    def _update_leadership_points(self):
        """
        Update the printout of current health.
        Must be called whenever a related value have been change.
        """
        rank_index = self._player_info["Rank"]
        rank_bonus = self._current_character["Config"]["Rank Bonus"][rank_index]
        leadership_points = self._get_attribute_value("Charisma") + rank_bonus
        bonus_string = "".join(self._check_active_bonuses("Leadership Points"))
        self._stats["Leadership Points"]["value"] = leadership_points
        dpg.set_value(
            item="Leadership Points",
            value=f"{leadership_points} {bonus_string}",
        )

    def _update_ap_status(self):
        """
        Update the printout of available attribute points.
        Must be called whenever a related value have been change.
        """
        extra = self._get_extra_attribute_points()
        remaining = self._get_attribute_points()
        self._stats["Attribute Points"]["value"] = remaining
        dpg.set_value(item="Attribute Points", value=remaining)
        self._stats["Extra Attribute Points"]["value"] = extra
        dpg.set_value(item="Extra Attribute Points", value=extra)

    def _update_xp_status(self):
        """
        Update the printout of available experience points.
        Must be called whenever a related value have been change.
        """
        remaining = self._get_base_experience_points() - self._get_total_xp_usage()
        self._stats["Experience Points"]["value"] = remaining
        dpg.set_value(item="Experience Points", value=remaining)

    def _update_pp_status(self):
        """
        Update the printout of available psycho points.
        Must be called whenever a related value have been change.
        """
        remaining = self._get_base_psycho_points() - self._get_psycho_point_cost()
        self._stats["Psycho Points"]["value"] = remaining
        dpg.set_value(item="Psycho Points", value=remaining)

    def _update_trait_status(self):
        """
        Update the printout of remaining traits.
        Must be called whenever a related value have been change.
        """
        remaining = self._get_base_available_traits() - self._get_count_traits()
        self._stats["Available Traits"]["value"] = remaining
        dpg.set_value(item="Available Traits", value=remaining)

    def _update_overview(self):
        overview_list: str = ""
        for property_key, property_value in self._serial_properties.items():
            if "cost" in property_value and property_value["value"]:
                cost: int = property_value["cost"]
                overview_list = overview_list + f"{property_key} ({cost})\n"
        dpg.set_value("overview_list", overview_list)

    def _get_current_character_name(self):
        current_character_name = self._player_info["Name"]
        return current_character_name.replace(" ", "_").lower()

    def _save_character_callback(self):
        file_path = (
            get_character_save_location()
            .joinpath(self._get_current_character_name())
            .with_suffix(".json")
        )
        CharacterExport.to_json(file_path, self._current_character)

    def _export_to_pdf_callback(self):
        file_path = (
            get_pdf_save_location()
            .joinpath(self._get_current_character_name())
            .with_suffix(".pdf")
        )
        ctp = CharacterToPdf(self._current_character, self._stats, file_path)
        ctp.write_pdf()
        print(f"Created: {file_path}")

        if sys.platform == "win32":
            os.startfile(file_path, "open")
        elif sys.platform == "darwin":
            subprocess.call(["open", file_path])
        else:
            subprocess.call(["xdg-open", file_path])

    @staticmethod
    def _split_dict(source: dict, num_per_part: int, max_row_count=24):
        """
        Helper function to dived a set of components into groups
        in order to control the number of items shown horisontally.
        For example.
        * Limit the amount traits/advantages/disadvantages for each column.
        " Limit the amount of skill sub categories for each column.
        """
        split_items: list[dict] = []
        part = dict()
        row_count: int = 0
        category_count: int = 0
        for item_key, item_value in source.items():
            part[item_key] = item_value
            category_count = category_count + 1
            row_count = row_count + len(item_value)
            if (category_count >= num_per_part) or (row_count >= max_row_count):
                split_items.append(part)
                part = dict()
                category_count = 0
                row_count = 0
        if category_count > 0:
            split_items.append(part)
        return split_items

    def _add_character_setup(self):
        dpg.add_text("Character Setup", color=self._section_title_color)
        with dpg.table(
            header_row=False, policy=dpg.mvTable_SizingStretchProp, row_background=False
        ):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                dpg.add_text("Player:")
                if self._create_mode:
                    dpg.add_input_text(
                        tag="player_input_text",
                        default_value=self._player_info["Player"],
                        width=self._text_input_width,
                        enabled=self._create_mode,
                        user_data={"label": "Player"},
                        callback=self._player_info_callback,
                    )
                else:
                    dpg.add_text(self._player_info["Player"])

            with dpg.table_row():
                dpg.add_text("E-mail:")
                if self._create_mode:
                    dpg.add_input_text(
                        tag="email_input_text",
                        default_value=self._player_info["E-mail"],
                        width=self._text_input_width,
                        enabled=self._create_mode,
                        user_data={"label": "E-mail"},
                        callback=self._player_info_callback,
                    )
                else:
                    dpg.add_text(self._player_info["E-mail"])

            with dpg.table_row():
                dpg.add_text("Name:")
                if self._create_mode:
                    dpg.add_input_text(
                        default_value=self._player_info["Name"],
                        width=self._text_input_width,
                        enabled=self._create_mode,
                        user_data={"label": "Name"},
                        callback=self._player_info_callback,
                    )
                else:
                    dpg.add_text(self._player_info["Name"])

            with dpg.table_row():
                dpg.add_text("Platoon:")
                current_platoon = self._player_info["Platoon"]

                if self._create_mode:
                    dpg.add_combo(
                        items=self._platoon_alternatives,
                        width=self._text_input_width,
                        default_value=self._platoon_alternatives[0],
                        user_data={"label": "Platoon"},
                        callback=self._player_info_callback,
                    )
                else:
                    dpg.add_text(current_platoon)

            with dpg.table_row():
                dpg.add_text("Rank:")
                rank_index = self._player_info["Rank"]
                rank_label = self._rank_alternatives[rank_index]
                dpg.add_text(rank_label)

            with dpg.table_row():
                dpg.add_text("Speciality:")
                current_speciality = self._player_info["Speciality"]
                if self._create_mode:
                    dpg.add_combo(
                        items=self._speciality_alternatives,
                        width=self._text_input_width,
                        default_value=current_speciality,
                        enabled=self._create_mode,
                        user_data={"label": "Speciality"},
                        callback=self._player_info_callback,
                    )
                else:
                    dpg.add_text(current_speciality)

            with dpg.table_row():
                dpg.add_text("Gender:")
                current_gender = self._player_info["Gender"]

                if self._create_mode:
                    dpg.add_combo(
                        tag="gender_input_combo",
                        items=self._gender_alternatives,
                        width=self._text_input_width,
                        default_value=current_gender,
                        enabled=self._create_mode,
                        user_data={"label": "Gender"},
                        callback=self._player_info_callback,
                    )
                else:
                    dpg.add_text(current_gender)

            with dpg.table_row():
                dpg.add_text("Age:")
                current_age = self._player_info["Age"]

                if self._create_mode:
                    dpg.add_slider_int(
                        tag="age_input_combo",
                        min_value=(self._imported_character["Config"]["age"]["min"]),
                        max_value=(self._imported_character["Config"]["age"]["max"]),
                        default_value=current_age,
                        enabled=self._create_mode,
                        user_data={"label": "Age"},
                        callback=self._player_info_callback,
                    )
                else:
                    dpg.add_text(str(current_age))

    def _add_property_check_boxes(
        self,
        section,
        tab_label,
        sub_tab_label,
        num_per_row=4,
        label_width=130,
        cost_width=25,
        show_cost=True,
        callback=None,
    ):
        """
        Add components for traits, advantages or disadvantages.
        """
        item_refs = dict()
        tab: TraitsTab | ExpertisesTab = self._current_character[section][tab_label]
        properties = tab[sub_tab_label]
        split_items: list[TraitsSubtab | ExpertiseSubtab]
        split_items = self._split_dict(properties, num_per_row)

        with dpg.group(horizontal=True):
            for part in split_items:
                with dpg.group():
                    for category_key, category_value in part.items():
                        with dpg.group(width=300):
                            dpg.add_text(category_key, color=self._section_title_color)
                            for property_key, property_value in category_value.items():
                                active = self._extension_active(property_value)
                                has_value = self._property_has_value(property_value)
                                allow_change = self._allow_change(property_value)
                                if active or has_value:
                                    with dpg.group(horizontal=True):
                                        with dpg.table(
                                            header_row=False,
                                            row_background=False,
                                            no_host_extendX=True,
                                        ):
                                            dpg.add_table_column(
                                                width_fixed=True,
                                                init_width_or_weight=20,
                                            )
                                            dpg.add_table_column(
                                                width_fixed=True,
                                                init_width_or_weight=label_width,
                                            )
                                            if show_cost and "cost" in property_value:
                                                dpg.add_table_column(
                                                    width_fixed=True,
                                                    init_width_or_weight=cost_width,
                                                )
                                            with dpg.table_row():
                                                item_id = dpg.add_checkbox(
                                                    tag=property_key,
                                                    user_data={
                                                        "section": section,
                                                        "tab_label": tab_label,
                                                        "sub_tab_label": sub_tab_label,
                                                        "category": category_key,
                                                        "label": property_key,
                                                    },
                                                    indent=5,
                                                    callback=callback,
                                                    default_value=has_value,
                                                    enabled=allow_change,
                                                )
                                                item_refs[property_key] = item_id
                                                dpg.add_text(
                                                    property_key,
                                                    tag="tooltip_" + property_key,
                                                )
                                                if show_cost:
                                                    dpg.add_text(
                                                        f"({property_value['cost']})"
                                                    )
                                                self._add_tooltip(
                                                    property_key, property_value
                                                )
        return item_refs

    def _add_slider_input(
        self,
        section,
        tab_label,
        sub_tab_label,
        num_per_row=3,
        label_width=170,
        callback=None,
    ):
        """
        Add sliders for skills.
        """
        item_refs = dict()
        tab: AttributesTab | SkillsTab = self._current_character[section][tab_label]
        categories = tab[sub_tab_label]
        split_items: list[AttributeSubtab | SkillsSubtab]
        split_items = self._split_dict(categories, num_per_row)

        with dpg.group(horizontal=True):
            for part in split_items:
                with dpg.group():
                    for category_key, category_value in part.items():
                        with dpg.group(width=300):
                            dpg.add_text(category_key, color=self._section_title_color)
                            for property_key, property_value in category_value.items():
                                if self._create_mode:
                                    min_value = property_value["min"]
                                else:
                                    min_value = property_value["value"]

                                active = self._extension_active(property_value)
                                has_value = self._property_has_value(property_value)
                                if active or has_value:
                                    with dpg.table(
                                        header_row=False,
                                        row_background=False,
                                        no_host_extendX=True,
                                    ):
                                        dpg.add_table_column(
                                            width_fixed=True,
                                            init_width_or_weight=label_width,
                                        )
                                        dpg.add_table_column(
                                            width_fixed=True, init_width_or_weight=100
                                        )
                                        with dpg.table_row():
                                            dpg.add_text(
                                                property_key,
                                                tag="tooltip_" + property_key,
                                                indent=5,
                                            )
                                            item_id = dpg.add_slider_int(
                                                tag=property_key,
                                                default_value=property_value["value"],
                                                min_value=min_value,
                                                max_value=property_value["max"],
                                                width=50,
                                                user_data={
                                                    "section": section,
                                                    "tab_label": tab_label,
                                                    "sub_tab_label": sub_tab_label,
                                                    "category": category_key,
                                                    "label": property_key,
                                                },
                                                callback=callback,
                                            )
                                            item_refs[property_key] = item_id

                                            self._add_tooltip(
                                                property_key, property_value
                                            )
        return item_refs

    def main(self):
        with dpg.window(
            width=300,
            height=1000,
            pos=[0, 0],
            no_move=True,
            no_close=True,
            no_collapse=True,
            no_resize=True,
            no_title_bar=True,
        ):
            with dpg.group(width=300):
                self._add_character_setup()

                # Display Stats
                dpg.add_text("Stats", color=self._section_title_color)
                with dpg.table(
                    header_row=False,
                    policy=dpg.mvTable_SizingFixedFit,
                    row_background=False,
                ):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    for stat_label, stat_value in self._stats.items():
                        with dpg.table_row():
                            dpg.add_text(stat_label, tag="tooltip_" + stat_label)
                            dpg.add_text(
                                tag=stat_label,
                                default_value=str(stat_value["value"]),
                            )
                            self._add_tooltip(stat_label, stat_value)

            with dpg.group(width=300):
                dpg.add_spacer(height=50)
                dpg.add_button(
                    label="Save Character", callback=self._save_character_callback
                )
                dpg.add_button(
                    label="Export to PDF", callback=self._export_to_pdf_callback
                )

            """ Hide button for character upload until implemented
            with dpg.group(width=300):
                dpg.add_spacer(height=50)
                if self._create_mode:
                    dpg.add_button(label="Submit new character to Skynet")
                else:
                    dpg.add_button(label="Submit update to Skynet")
            """

        with dpg.window(
            width=1000,
            height=1000,
            pos=[301, 0],
            no_move=True,
            no_close=True,
            no_collapse=True,
            no_resize=True,
            no_title_bar=True,
        ):
            with dpg.group(width=300):
                with dpg.tab_bar(tag="Tabs"):
                    with dpg.tab(label="Attributes"):
                        self._add_slider_input(
                            section="Character",
                            tab_label="Attributes",
                            sub_tab_label="All",
                            callback=self._attribute_callback,
                        )

                    with dpg.tab(label="Skills"):
                        self._add_slider_input(
                            section="Character",
                            tab_label="Skills",
                            sub_tab_label="All",
                            callback=self._skills_callback,
                        )

                    for tab_label in ["Traits", "Expertise"]:
                        with dpg.tab(label=tab_label):
                            with dpg.tab_bar():
                                for sub_tab_label in self._current_character[
                                    "Character"
                                ][tab_label].keys():
                                    with dpg.tab(label=sub_tab_label):
                                        self._add_property_check_boxes(
                                            section="Character",
                                            tab_label=tab_label,
                                            sub_tab_label=sub_tab_label,
                                            num_per_row=3,
                                            label_width=180,
                                            callback=self._property_callback,
                                        )
        with dpg.window(
            width=300,
            height=1000,
            pos=[1302, 0],
            no_move=True,
            no_close=True,
            no_collapse=True,
            no_resize=True,
            no_title_bar=True,
        ):
            with dpg.group(width=300):
                dpg.add_text(
                    "Traits and Experise Overview", color=self._section_title_color
                )
                dpg.add_text("", tag="overview_list", indent=5)
                self._update_overview()

        self._update_xp_status()
        self._update_pp_status()
        self._update_psycho_limit()
        self._update_stress_limit()
        self._update_stunt_cap()
        self._update_health_limit()
        self._update_leadership_points()
        self._update_carry_capacity()
        self._update_combat_load()
        self._check_property_disable()


class CharacterSelector:
    """
    Allow the user to either create a new character or load an existing one.
    """

    def __init__(self):
        self._section_title_color = [150, 250, 150]

        self._available_characters: list[str] = []
        self._characters_files: list[Path] = []

        """
        When true, the character i fully editable in the same way as creating a
        new character.
        When False, XP can only be spend, not removed.
        This feature will be remove/hidden in the final version.
        """
        self._create_mode: bool = False

        self._extend_character = {
            "military": True,
            "navy": True,
            "colonist": True,
            "background": self._create_mode,
        }

        for file in get_character_save_location().glob("*.json"):
            self._available_characters.append(file.stem.replace("_", " ").title())
            self._characters_files.append(file)

        if self._available_characters:
            self._selected_character = self._available_characters[0]
            self._selected_character_file = self._characters_files[0]
        else:
            self._selected_character = None
            self._selected_character_file = None

        # ci = CharacterImport.from_json(self._selected_character_file)
        # cg = CharacterGenerator(character=ci.get_character(),
        #                        create_mode=True,
        #                        extend_character=self._extend_character)
        # cg.main()

    def _character_list_callback(self, sender, app_data):
        """
        Called when selecting a character in the list.
        """
        self._selected_character = app_data

    def _edit_button_callback(self, sender, app_data):
        """
        Continue with the selected character and setup next stage for edit mode.
        """
        idx = self._available_characters.index(self._selected_character)
        self._selected_character_file = self._characters_files[idx]

        ci = CharacterImport.from_json(self._selected_character_file)
        cg = CharacterGenerator(
            character=ci.get_character(),
            create_mode=self._create_mode,
            extend_character=self._extend_character,
        )
        cg.main()

    def _admin_button_callback(self, sender, app_data):
        """
        Update creation mode.
        """
        self._create_mode = app_data

    def _create_button_callback(self, sender, app_data):
        """
        Continue with template character and setup next stage for creation mode.
        """
        self._selected_character_file = get_character_template()

        ci = CharacterImport.from_json(self._selected_character_file)

        cg = CharacterGenerator(
            character=ci.get_character(),
            create_mode=True,
            extend_character=self._extend_character,
        )
        cg.main()

    def _extend_with_military_callback(self, sender, app_data):
        self._extend_character["military"] = app_data

    def _extend_with_navy_callback(self, sender, app_data):
        self._extend_character["navy"] = app_data

    def _extend_with_colonist_callback(self, sender, app_data):
        self._extend_character["colonist"] = app_data

    def _connect_button_callback(self, sender, app_data):
        self._add_character_selection()

    def _add_login(self):
        with dpg.group(width=200):
            dpg.add_text("Credentials:", color=self._section_title_color)
            with dpg.group(horizontal=True):
                dpg.add_text("Username:", color=self._section_title_color, indent=10)
                dpg.add_input_text(default_value="skynet_user", enabled=False, width=50)
            with dpg.group(horizontal=True):
                dpg.add_text("Password:", color=self._section_title_color, indent=10)
                dpg.add_input_text(default_value="skynet_password", enabled=False)
            dpg.add_button(label="Connect", callback=self._connect_button_callback)
            dpg.add_spacer(height=20)

    def _add_character_selection(self):
        with dpg.group(width=300, parent="character_selector"):
            dpg.add_button(
                label="Create New Character", callback=self._create_button_callback
            )
            dpg.add_spacer(height=20)

            dpg.add_listbox(
                self._available_characters,
                callback=self._character_list_callback,
                num_items=10,
            )
            dpg.add_checkbox(label="Admin Mode", callback=self._admin_button_callback)
            dpg.add_button(label="Edit Character", callback=self._edit_button_callback)

            dpg.add_text("Extend character:")
            dpg.add_checkbox(
                label="Other Military",
                default_value=self._extend_character["military"],
                callback=self._extend_with_military_callback,
            )
            dpg.add_checkbox(
                label="Space Navy",
                default_value=self._extend_character["navy"],
                callback=self._extend_with_navy_callback,
            )
            dpg.add_checkbox(
                label="Colonist",
                default_value=self._extend_character["colonist"],
                callback=self._extend_with_colonist_callback,
            )

    def main(self):
        """
        Set Login options.
        Select existing character or create new
        """

        # Uncomment this and comment below to skip selector page and
        # go directly to character creation.
        """
        self._selected_character_file = get_character_template()

        ci = CharacterImport.from_json(self._selected_character_file)
        cg = CharacterGenerator(character=ci.get_character(), create_mode=True)
        cg.main()
        """

        with dpg.window(
            width=380,
            height=400,
            pos=[0, 0],
            tag="character_selector",
            no_move=True,
            no_close=True,
            no_collapse=True,
            no_resize=True,
            no_title_bar=True,
        ):
            # Skip login for now and go directly to the character selector
            # self._add_login()
            self._add_character_selection()


class CharacterImport:
    """
    Handle import of character. Currenty only from json-file.
    """

    def __init__(self, character: CharacterData):
        self._character = character

    @classmethod
    def from_json(cls, character_path: Path):
        with character_path.open() as setup_file:
            imported_character = json.load(setup_file)

        return cls(imported_character)

    def get_character(self):
        return self._character


class CharacterExport:
    """
    Handle export of character. Currenty only to json-file.
    """

    def __init__(self, character_path: Path, character: CharacterData):
        self._character = deepcopy(character)
        self._character_path = character_path

    @classmethod
    def to_json(cls, character_path: Path, character: CharacterData):
        character_out = deepcopy(character)

        # Convert from true/false to 1/0
        char_prop = character_out["Character"]
        for tab in char_prop:
            for sub_tab in char_prop[tab].keys():
                for category in char_prop[tab][sub_tab].keys():
                    for label in char_prop[tab][sub_tab][category].keys():
                        val = char_prop[tab][sub_tab][category][label]["value"]
                        char_prop[tab][sub_tab][category][label]["value"] = int(val)
        character_out["Character"] = char_prop

        as_json = json.dumps(character_out, indent=4)
        with character_path.open(mode="w") as out_file:
            out_file.write(as_json)
        return cls(character_path, character)


class CharacterToPdf:
    def __init__(self, character: CharacterData, stats: dict[str, ValueType], out_file):
        self._line_height = 15
        self._current_y = 820
        self._current_x = 20
        self._font_size = 12
        self._character = character
        self._stats = stats
        self.out_file = str(out_file)
        self._canvas = canvas.Canvas(self.out_file, pagesize=(595, 842))

    def _write_line(self, line: str, title=False):
        if title:
            self._canvas.setFont("Helvetica-Bold", self._font_size)
        else:
            self._canvas.setFont("Helvetica", self._font_size)
        self._canvas.drawString(self._current_x, self._current_y, line)
        self._current_y = self._current_y - self._line_height
        if self._current_y < 0:
            self._current_y = 820
            self._current_x = 200

    def write_pdf(self):
        self._write_line("Character Info", title=True)
        for key, value in self._character["Player Info"].items():
            if key == "Rank":
                rank_index = self._character["Player Info"]["Rank"]
                rank_label = self._character["Config"]["Rank Labels"][rank_index]
                self._write_line(f"{key}: {rank_label}")
            else:
                self._write_line(f"{key}: {value}")

        total_xp = self._character["Config"]["Starting XP"]
        remaining_xp = self._stats["Experience Points"]["value"]
        total_ap = self._character["Config"]["Starting AP"]
        remaining_ap = self._stats["Attribute Points"]["value"]
        total_traits = self._character["Config"]["Starting Traits"]
        remaining_traits = self._stats["Available Traits"]["value"]
        if "Psycho Points" in self._character["Config"].keys():
            total_pp = self._character["Config"]["Psycho Points"]
        else:
            total_pp = 0
        remaining_pp = self._stats["Psycho Points"]["value"]

        self._write_line(" ")
        self._write_line(f"Total XP: {total_xp}")
        self._write_line(f"Remaining XP: {remaining_xp}")
        self._write_line(f"Total AP: {total_ap}")
        self._write_line(f"Remaining AP: {remaining_ap}")
        self._write_line(f"Total PP: {total_pp}")
        self._write_line(f"Remaining PP: {remaining_pp}")
        self._write_line(f"Total traits: {total_traits}")
        self._write_line(f"Remaining traits: {remaining_traits}")
        self._write_line(" ")

        self._write_line("Attributes", title=True)
        attributes = self._character["Character"]["Attributes"]["All"]["Attribute"]
        for attribute, content in attributes.items():
            value = content["value"]
            self._write_line(f"{attribute}: {value}")

        self._write_line("Skills", title=True)
        for content in self._character["Character"]["Skills"]["All"].values():
            for skill, skill_content in content.items():
                value = skill_content["value"]
                if value > 0:
                    self._write_line(f"{skill}: {value}")

        for tab_label in ["Traits", "Expertise"]:
            self._write_line(tab_label, title=True)
            tab: TraitsTab | ExpertisesTab = self._character["Character"][tab_label]
            for sub_tab_label, sub_tab_content in tab.items():
                self._write_line(sub_tab_label, title=True)
                for category_content in sub_tab_content.values():
                    for label, label_content in category_content.items():
                        value = label_content["value"]
                        cost = label_content["cost"]
                        if value > 0:
                            self._write_line(f"{label} ({cost})")

        self._canvas.showPage()
        self._canvas.save()


def set_theme():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(
                dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core
            )

        with dpg.theme_component(dpg.mvCheckbox):
            dpg.add_theme_color(
                dpg.mvThemeCol_CheckMark, [150, 250, 150], category=dpg.mvThemeCat_Core
            )

        with dpg.theme_component(dpg.mvCheckbox, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, [0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, [0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, [0, 0, 0])

    dpg.bind_theme(global_theme)


def main() -> None:
    dpg.create_context()

    set_theme()

    cs = CharacterSelector()
    cs.main()

    dpg.create_viewport(title="USCM Character Editor", width=1730, height=1050)
    dpg.setup_dearpygui()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
