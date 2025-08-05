from langchain_core.tools import tool
from db.dnd_db import DnDDatabase

db = DnDDatabase()

@tool
def get_race_info(race_name: str)-> str:
    """
    특정 종족의 정보를 조회합니다.
    
    Args:
        race_name: 조회할 종족 이름 (예: Human, Elf, Dwarf, Halfling)
    
    Returns:
        종족의 상세 정보
    """
    race_data = db.get_race_by_name(race_name)
    if not race_data:
        return f"'{race_name}' 종족을 찾을 수 없습니다."
    
    return f"""
    종족: {race_data['name']}
    설명: {race_data['description']}
    능력치:
    - 힘: {race_data['strength']}
    - 민첩: {race_data['agility']}  
    - 정신력: {race_data['mentality']}
    - 운: {race_data['luck']}
    - 지능: {race_data['intelligence']}
    - 기본 HP: {race_data['base_hp']}
    """

@tool
def get_class_info(class_name: str) -> str:
    """
    특정 직업의 정보를 조회합니다.
    
    Args:
        class_name: 조회할 직업 이름 (예: Warrior, Mage, Rogue, Cleric)
    
    Returns:
        직업의 상세 정보
    """
    class_data = db.get_class_by_name(class_name)
    if not class_data:
        return f"'{class_name}' 직업을 찾을 수 없습니다."
    
    return f"""
    직업: {class_data['name']}
    설명: {class_data['description']}
    능력치:
    - 힘: {class_data['strength']}
    - 민첩: {class_data['agility']}
    - 정신력: {class_data['mentality']}
    - 운: {class_data['luck']}
    - 지능: {class_data['intelligence']}
    - 기본 HP: {class_data['base_hp']}
    """

@tool
def calculate_character_stats(race_name: str, class_name: str) -> str:
    """
    종족과 직업을 조합한 캐릭터의 총 능력치를 계산합니다.
    
    Args:
        race_name: 선택한 종족 이름
        class_name: 선택한 직업 이름
    
    Returns:
        계산된 총 능력치 정보
    """
    stats = db.calculate_total_stats(race_name, class_name)
    if not stats:
        return f"'{race_name}' 종족 또는 '{class_name}' 직업을 찾을 수 없습니다."
    
    return f"""
    캐릭터 정보: {stats['race']} {stats['class']}
    
    총 능력치:
    - 총 힘: {stats['total_strength']} (종족: +{stats['race_bonuses']['strength']}, 직업: +{stats['class_bonuses']['strength']})
    - 총 민첩: {stats['total_agility']} (종족: +{stats['race_bonuses']['agility']}, 직업: +{stats['class_bonuses']['agility']})
    - 총 정신력: {stats['total_mentality']} (종족: +{stats['race_bonuses']['mentality']}, 직업: +{stats['class_bonuses']['mentality']})
    - 총 운: {stats['total_luck']} (종족: +{stats['race_bonuses']['luck']}, 직업: +{stats['class_bonuses']['luck']})
    - 총 지능: {stats['total_intelligence']} (종족: +{stats['race_bonuses']['intelligence']}, 직업: +{stats['class_bonuses']['intelligence']})
    - 총 HP: {stats['total_hp']} (종족: +{stats['race_bonuses']['base_hp']}, 직업: +{stats['class_bonuses']['base_hp']})
    """

@tool 
def list_available_options() -> str:
    """
    선택 가능한 모든 종족과 직업 목록을 반환합니다.
    
    Returns:
        사용 가능한 종족과 직업 목록
    """
    races = db.get_all_races()
    classes = db.get_all_classes()
    
    race_list = "\n".join([f"- {race['name']}: {race['description']}" for race in races])
    class_list = "\n".join([f"- {cls['name']}: {cls['description']}" for cls in classes])
    
    return f"""
    선택 가능한 종족:
    {race_list}
    
    선택 가능한 직업:
    {class_list}
    """