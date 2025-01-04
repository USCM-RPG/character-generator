from typing import NotRequired, TypedDict

class ValueType(TypedDict):
    value: int
    tooltip: NotRequired[str]
    extended: NotRequired[str]

class MinMaxType(TypedDict):
    max: int
    min: int

class CostType(TypedDict):
    cost: int

class RequirementType(TypedDict):
    type: str
    value: int

class RequirementsType(TypedDict, total=False):
    requirements: dict[str, RequirementType]

class AttributeType(ValueType, MinMaxType):
    pass
type AttributesType = dict[str, AttributeType]

class SkillType(ValueType, MinMaxType):
    pass
type SkillGroupType = dict[str, SkillType]
type SkillsType = dict[str, SkillGroupType]

class TraitType(ValueType, CostType, RequirementsType):
    pass
type TraitSubtabType = dict[str, TraitType]
type TraitGroupType = dict[str, TraitSubtabType]
type TraitsType = dict[str, TraitGroupType]

class ExpertiseType(ValueType, CostType):
    pass
type ExpertiseSubcategoryType = dict[str, ExpertiseType]
type ExpertiseCategoryType = dict[str, ExpertiseSubcategoryType]
type ExpertisesType = dict[str, ExpertiseCategoryType]

PlayerInfoType = TypedDict("PlayerInfoType",
    {
        "Player": str,
        "E-mail": str,
        "Name": str,
        "Platoon": str,
        "Rank": int,
        "Speciality": str,
        "Gender": str,
        "Age": int
    }
)

CharacterConfigType = TypedDict("CharacterConfigType",
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
        "Combat Load Table": list[int]
    }
)
    
class CharacterPropertiesType(TypedDict):
    Attributes: AttributesType
    Skills: SkillsType
    Traits: TraitsType
    Expertise: ExpertisesType

CharacterDataType = TypedDict("CharacterDataType",
    {
        "Player Info": PlayerInfoType,
        "Config": CharacterConfigType,
        "Character": CharacterPropertiesType,
    }
)
