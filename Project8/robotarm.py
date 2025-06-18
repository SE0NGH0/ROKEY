import rclpy
import DR_init

# for single robot
ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"
VELOCITY, ACC = 170, 170

DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL

OFF, ON = 0, 1

def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("force_control", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        from DSR_ROBOT2 import (
            release_compliance_ctrl,
            check_force_condition,
            task_compliance_ctrl,
            set_desired_force,
            set_tool,
            set_tcp,
            movej,
            movel,
            get_current_posx,
            set_digital_output,
            get_digital_input,
            wait,
            DR_FC_MOD_REL,
            DR_AXIS_Z,
            DR_BASE,
            DR_MV_MOD_REL,
        )
        from DR_common2 import posx

    except ImportError as e:
        print(f"Error importing DSR_ROBOT2 : {e}")
        return

    # -----------------------------------
    # (1) Place 위치(3층) 계산
    BASE_HEIGHT = 250
    delta = [78, 0, 0, 0, 0, 0]
    delta2 = [38, 68, 0, 0, 0, 0]

    init_cuppos = [353.2068, -50.4698, 102.1384, 0, -180, 0]  
    init_cupposN = []
    init_cupposCopy = init_cuppos.copy() 
    path = []
    i = 3  # 첫 층에 3개

    for r in range(i):
        init_cupposN.append(init_cupposCopy.copy())
        Nfloor = [init_cupposN[r].copy()]
        for _ in range(i-1):
            init_cupposN[r][0] += delta[0]
            Nfloor.append(init_cupposN[r].copy())
        k = i - 1
        for j in range(i-1):
            init_cupposN[r][1] += delta2[1]
            if j % 2 == 0:
                init_cupposN[r][0] -= delta2[0]
            else:
                init_cupposN[r][0] += delta2[0]
            Nfloor.append(init_cupposN[r].copy())

            for _ in range(k-1):
                if j % 2 == 0:
                    init_cupposN[r][0] -= delta[0]
                else:
                    init_cupposN[r][0] += delta[0]
                Nfloor.append(init_cupposN[r].copy())
            k -= 1
        i -= 1
        init_cupposCopy[0] += 38
        init_cupposCopy[1] += 22
        init_cupposCopy[2] += 95
        path.append(Nfloor)

    print("Path (3층):", path)
    placeList = path[0] + path[1] + path[2]  # 3층 전체 좌표 합침

    # -----------------------------------
    # (2) Pick 위치(11개) 계산
    def calculate_pick_positions(base_height, num_cups):
        pick_positions = []
        for i in range(num_cups):
            if i == 0:
                z = base_height
            else:
                z = base_height - i * 11
            pick_positions.append([427.7594, -184.2381, z, 0, -180, 0])
        return pick_positions

    # -----------------------------------
    # (3) 그리퍼 열고 닫기
    def release():
        set_digital_output(2, ON)
        set_digital_output(1, OFF)
        print("Release object")
        wait(1)

    def grip():
        set_digital_output(1, ON)
        set_digital_output(2, OFF)
        print("Grip object")
        wait(1)

    # -----------------------------------
    # (4) Force Control Pick & Place
    def force_control_pick_and_place(pick_pos, place_pos):
        """
        pick_pos: 스택(위)에서 한 컵을 분리해 잡을 위치
        place_pos: 새로 놓을 위치(역시 스택이라 가정)
        """
        grip()
        pre_pick_pos = pick_pos.copy()
        pre_pick_pos[2] += 8
        pre_pick_pos1 = pre_pick_pos[2]

        if place_pos[2] > 180:
            pre_pick_pos1 = pre_pick_pos[2]
            pre_pick_pos[2] = 360

        # 1) Pick 지점 접근
        movel(pre_pick_pos, vel=VELOCITY, acc=ACC)
        movel([pre_pick_pos[0], pre_pick_pos[1], pre_pick_pos1, 
               pre_pick_pos[3], pre_pick_pos[4], pre_pick_pos[5]],
              vel=VELOCITY, acc=ACC)

        # 2) Force Control로 컵 상단 감지(-15N)
        task_compliance_ctrl(stx=[500, 500, 500, 100, 100, 100])
        set_desired_force(fd=[0, 0, -15, 0, 0, 0],
                          dir=[0, 0, 1, 0, 0, 0],
                          mod=DR_FC_MOD_REL)

        while not check_force_condition(DR_AXIS_Z, max=8):
            pass
        height_pos = get_current_posx()[0][2]
        release_compliance_ctrl()

        # 3) 컵 분리 동작
        pre_pick_pos[2] = height_pos
        movel([pre_pick_pos[0], pre_pick_pos[1], height_pos+5,
               pre_pick_pos[3], pre_pick_pos[4], pre_pick_pos[5]],
              vel=VELOCITY, acc=ACC)
        release()
        movel([pick_pos[0], pick_pos[1], height_pos-12,
               pick_pos[3], pick_pos[4], pick_pos[5]],
              vel=VELOCITY, acc=ACC, ref=DR_BASE)
        grip()

        # 4) 위로 들어올리기
        pre_pick_pos[2] += 100
        if place_pos[2] > 180:
            pre_pick_pos[2] = 360
        movel(pre_pick_pos, vel=VELOCITY, acc=ACC)

        # 5) Place 지점 이동
        movel([place_pos[0], place_pos[1], pre_pick_pos[2],
               place_pos[3], place_pos[4], place_pos[5]],
              vel=VELOCITY, acc=ACC, ref=DR_BASE)
        movel([place_pos[0], place_pos[1], place_pos[2]+10,
               place_pos[3], place_pos[4], place_pos[5]],
              vel=VELOCITY, acc=ACC, ref=DR_BASE)

        # 6) Place 시에도 Force Control
        task_compliance_ctrl(stx=[500, 500, 500, 100, 100, 100])
        set_desired_force(fd=[0, 0, -15, 0, 0, 0],
                          dir=[0, 0, 1, 0, 0, 0],
                          mod=DR_FC_MOD_REL)
        while not check_force_condition(DR_AXIS_Z, max=8):
            pass
        release_compliance_ctrl()
        release()

        # 7) 빠져나오기(안전 높이)
        pre_pick_pos[2] -= 150
        if place_pos[2] > 193:
            place_pos[2] = 336
        else:
            place_pos[2] = 217
        movel([place_pos[0], place_pos[1], place_pos[2],
               place_pos[3], place_pos[4], place_pos[5]],
              vel=VELOCITY, acc=ACC)

    # -----------------------------------
    # (5) 메인 동작: 쌓고 → 역순으로 회수
    pickList = calculate_pick_positions(BASE_HEIGHT, 11)
    JReady = [367.471, 8.104, 194.494, 90.013, 179.963, 89.766]

    set_tool("Tool Weight_GR")
    set_tcp("GripperDA_v1")
    movel(JReady, vel=VELOCITY, acc=ACC)

    # -----------------------------
    # (A) 정방향: pickList → placeList (3층 쌓기)
    num_cups_to_place = min(len(placeList), len(pickList))
    print("=== Building the 3층 Tower ===")
    for i in range(num_cups_to_place):
        pick_pos = pickList[i % len(pickList)]
        place_pos = placeList[i]
        force_control_pick_and_place(pick_pos, place_pos)
        
    movel([427,-220,80,90,90,90],vel=60, acc=60)
    movel([427,-177,80,90,90,90],vel=60, acc=60)
    grip()
    movel([427,-177,250,90,90,90],vel=60, acc=60)
    movej([0,0,0,0,0,180],vel=VELOCITY, acc=ACC,mod=DR_MV_MOD_REL)
    movel([427, -100, 290,60,90,-90],vel=60, acc=60)
    movel([427.80596923828125, -3.8458755016326904, 350,60,90,-90],vel=60, acc=60)
    task_compliance_ctrl(stx=[500, 500, 500, 100, 100, 100])
    set_desired_force(fd=[0, 0, -15, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_REL)
    while not check_force_condition(DR_AXIS_Z, max=8):  # Force 감지 대기
        pass
    release_compliance_ctrl()
    release()
    movel([391.7555236816406, -63.046051025390625, 327.4129943847656, 53.128883361816406, 89.54312896728516, -89.16883087158203],vel=60, acc=60)
    movel([391.7555236816406, -63.046051025390625, 530, 53.128883361816406, 89.54312896728516, -89.16883087158203],vel=60, acc=60)
    movej([0,0,0,0,0,-180],vel=60, acc=60,mod=DR_MV_MOD_REL)
    movel([191.67477416992188, 0.5356343388557434, 270.2490234375, 123.4961166381836, 180.0, 126.570068359375], vel=60, acc=60)
    grip()
        
    release()
    movel([134.6050262451172, -278.9804382324219, 238.78634643554688, 151.59938049316406, -179.45892333984375, -156.964111328125], vel=60, acc=60)
    movel([403.05029296875, -39.80586624145508, 321.19781494140625, 59.940921783447266, 89.6454086303711, 89.844970703125], vel=60, acc=60)
    movel([428.347900390625, 3.976081132888794, 321.19781494140625, 59.940921783447266, 89.6454086303711, 89.844970703125], vel=60, acc=60)
    grip()
    movel([428.347900390625, 3.976081132888794, 350, 59.940921783447266, 89.6454086303711, 89.844970703125], vel=60, acc=60)
    movel([403.05029296875, -39.80586624145508, 400, 59.940921783447266, 89.6454086303711, 89.844970703125], vel=60, acc=60)
    movej([0,0,0,0,0,180], vel=VELOCITY, acc=ACC, mod=DR_MV_MOD_REL)
    movel([426.54840087890625,-183.73422241210938,174.16091918945312,56.638145446777344,90.14506530761719,-88.28025817871094], vel=60, acc=60)
    task_compliance_ctrl(stx=[500, 500, 500, 100, 100, 100])
    set_desired_force(fd=[0, 0, -15, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_REL)
    while not check_force_condition(DR_AXIS_Z, max=8):
        pass
    release_compliance_ctrl()
    release()
    movej([0,0,0,0,0,-180], vel=VELOCITY, acc=ACC, mod=DR_MV_MOD_REL)

    # -----------------------------
    # (B) 역순: placeList → pickList (탑 해제/정리)
    print("=== Removing the Tower in Reverse ===")
    # placeList를 마지막(가장 위)부터 다시 꺼내서 pickList로 되돌림
    for i in reversed(range(num_cups_to_place)):
        reverse_pick_pos = placeList[i]             # 지금은 'pick' 대상(실제로는 탑 위의 컵)
        reverse_place_pos = pickList[i % len(pickList)]  # 되돌릴 위치(원래 스택)
        force_control_pick_and_place(reverse_pick_pos, reverse_place_pos)
        
    movel([191.67477416992188, 0.5356343388557434, 270.2490234375, 123.4961166381836, 180.0, 126.570068359375], vel=60, acc=60)
    grip()

    rclpy.shutdown()

if __name__ == "__main__":
    main()
