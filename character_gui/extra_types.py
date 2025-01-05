from typing import NotRequired, TypedDict

class ValueType(TypedDict):
    value: int
    tooltip: NotRequired[str]
    extended: NotRequired[str]
    cost_table: NotRequired[list[int]]

class MinMaxType(ValueType):
    max: int
    min: int

class CostType(ValueType):
    cost: int

class RequirementType(TypedDict):
    type: str
    value: int

class RequirementsType(TypedDict, total=False):
    requirements: dict[str, RequirementType]

class AttributeType(MinMaxType):
    pass
type AttributeSubgroupType = dict[str, AttributeType]
type AttributeGroupType = dict[str, AttributeSubgroupType]
type AttributesType = dict[str, AttributeGroupType]

class SkillType(MinMaxType):
    pass
type SkillSubGroupType = dict[str, SkillType]
type SkillGroupType = dict[str, SkillSubGroupType]
type SkillsType = dict[str, SkillGroupType]

class TraitType(CostType, RequirementsType):
    pass
type TraitSubgroupType = dict[str, TraitType]
type TraitGroupType = dict[str, TraitSubgroupType]
type TraitsType = dict[str, TraitGroupType]

class ExpertiseType(CostType):
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
