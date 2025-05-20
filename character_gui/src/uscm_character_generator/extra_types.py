from typing import NotRequired, TypedDict


class ValueType(TypedDict):
    value: int
    tooltip: NotRequired[str]
    extended: NotRequired[str]


class MinMaxType(ValueType):
    max: int
    min: int


class BonusType(TypedDict):
    Target: str
    Type: str
    Value: int


class CostType(ValueType):
    cost: int
    bonus: NotRequired[list[BonusType]]


class RequirementType(TypedDict):
    type: str
    value: int


class AttributeType(TypedDict):
    value: int
    max: int
    min: int


type AttributeCategory = dict[str, AttributeType]


class AttributeSubtab(TypedDict):
    Attribute: AttributeCategory


class AttributesTab(TypedDict):
    All: AttributeSubtab


class SkillType(MinMaxType):
    cost_table: NotRequired[list[int]]


type SkillsCategory = dict[str, SkillType]
type SkillsSubtab = dict[str, SkillsCategory]


class SkillsTab(TypedDict):
    All: SkillsSubtab


class TraitType(CostType):
    requirements: NotRequired[dict[str, RequirementType]]


type TraitsCategory = dict[str, TraitType]
type TraitsSubtab = dict[str, TraitsCategory]
type TraitsTab = dict[str, TraitsSubtab]


class ExpertiseType(CostType):
    pass


type ExpertiseCategory = dict[str, ExpertiseType]
type ExpertiseSubtab = dict[str, ExpertiseCategory]
type ExpertisesTab = dict[str, ExpertiseSubtab]


PlayerInfoType = TypedDict(
    "PlayerInfoType",
    {
        "Player": str,
        "E-mail": str,
        "Name": str,
        "Platoon": str,
        "Rank": int,
        "Speciality": str,
        "Gender": str,
        "Age": int,
    },
)


CharacterConfigType = TypedDict(
    "CharacterConfigType",
    {
        "Starting XP": int,
        "Starting AP": int,
        "Starting Traits": int,
        "specialities": list[str],
        "platoons": list[str],
        "genders": list[str],
        "skill_cost_table": list[int],
        "age": dict[str, int],
        "Rank Labels": list[str],
        "Rank Bonus": list[int],
        "Carry Capacity Table": list[int],
        "Combat Load Table": list[int],
    },
)


class CharacterProperties(TypedDict):
    Attributes: AttributesTab
    Skills: SkillsTab
    Traits: TraitsTab
    Expertise: ExpertisesTab


CharacterData = TypedDict(
    "CharacterData",
    {
        "Player Info": PlayerInfoType,
        "Config": CharacterConfigType,
        "Character": CharacterProperties,
    },
)
