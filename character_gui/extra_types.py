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

class PlayerInfoType(TypedDict):
    Player: str
    Email: str
    Name: str
    Platoon: str
    Rank: int
    Speciality: str
    Gender: str
    Age: str

class CharacterConfigType(TypedDict):
    StartingXP: int
    StartingAP: int
    StartingTraits: int
    Specialities: list[str]
    Platoons: list[str]
    Genders: list[str]
    SkillCostTable: list[int]
    Age: dict[str, int]
    RankLabels: list[str]
    RankBonus: list[int]
    CarryCapacityTable: list[int]
    CombatLoadTable: list[int]
    
class CharacterPropertiesType(TypedDict):
    Attributes: AttributesType
    Skills: SkillsType
    Traits: TraitsType
    Expertise: ExpertisesType

class CharacterDataType(TypedDict):
    PlayerInfo: PlayerInfoType
    Config: CharacterConfigType
    Character: CharacterPropertiesType
       
