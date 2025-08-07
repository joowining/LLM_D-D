# 수정된 테스트 함수들

def test_intro():
    # 초기 state 준비
    initial_state = {
        "messages": [],
        "system_messages": [],
        "character_state": {
            "name": "",
            "race": "",
            "profession": "",
            "status": {},
            "location_type": "",
            "location": "",
            "attack_item": "",
            "defense_item": ""
        },
        "game_phase": GamePhase.introduction,
        "game_context": [],
        "story_summary": "",
        "question_time": 0,
        "cache_box": {}
    }
    
    try:
        result = result_graph.invoke(initial_state)
        print("Graph execution completed successfully!")
        print("Final state:", result)
        return result
    except Exception as e:
        print(f"Error during graph execution: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_graph_structure():
    """그래프 구조만 테스트 (실행하지 않음)"""
    try:
        # 그래프 구조 확인
        nodes = result_graph.get_graph().nodes
        edges = result_graph.get_graph().edges
        
        print("=== Graph Structure Test ===")
        print(f"Nodes: {list(nodes.keys())}")
        print(f"Edges: {len(edges)} connections")
        
        # ASCII 다이어그램 출력
        print("\n=== Graph Visualization ===")
        print(result_graph.get_graph().draw_ascii())
        
        return True
    except Exception as e:
        print(f"Graph structure error: {e}")
        return False

def test_individual_nodes():
    """개별 노드들을 간단히 테스트"""
    test_state = {
        "messages": ["안녕하세요"],
        "system_messages": [],
        "character_state": {
            "name": "테스트",
            "race": "Human",
            "profession": "Fighter",
            "status": {"current_hp": 100, "base_hp": 100},
            "location_type": "village",
            "location": "스톤브릿지",
            "attack_item": "long_sword",
            "defense_item": "leather_jacket"
        },
        "game_phase": GamePhase.introduction,
        "game_context": [],
        "story_summary": "",
        "question_time": 0,
        "cache_box": {}
    }
    
    print("=== Individual Node Tests ===")
    
    # 개별 노드 테스트
    try:
        print("Testing introduction node...")
        intro_result = introduce_background_node(test_state)
        print("✅ Introduction node works")
        
        print("Testing race explanation node...")
        race_result = explain_race(test_state)
        print("✅ Race explanation node works")
        
        return True
    except Exception as e:
        print(f"❌ Node test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== DnD Game Intro Test ===\n")
    
    # 1. 그래프 구조 테스트
    print("1. Testing graph structure...")
    if test_graph_structure():
        print("✅ Graph structure is valid\n")
    else:
        print("❌ Graph structure has issues\n")
        exit(1)
    
    # 2. 개별 노드 테스트
    print("2. Testing individual nodes...")
    if test_individual_nodes():
        print("✅ Individual nodes work\n")
    else:
        print("❌ Some nodes have issues\n")
    
    # 3. 전체 그래프 실행 테스트 (선택사항)
    user_choice = input("Do you want to run the full graph? (y/N): ").lower()
    if user_choice == 'y':
        print("3. Running full graph...")
        test_intro()
    else:
        print("Skipping full graph execution.")
    
    # 4. PNG 저장 시도
    try:
        png_data = result_graph.get_graph().draw_mermaid_png()
        with open("intro_graph.png", "wb") as f:
            f.write(png_data)
        print("📊 Graph visualization saved as intro_graph.png")
    except Exception as e:
        print(f"PNG save failed: {e}")
        print("Using ASCII visualization instead:")
        print(result_graph.get_graph().draw_ascii())