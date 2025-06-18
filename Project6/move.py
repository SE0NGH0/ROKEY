def grip() :
    set_digital_output(1,1)
    set_digital_output(2,0)
    #wait_digital_input(1,1)
 #여는 함수 설정
def ungrip():
    set_digital_output(1,0)
    set_digital_output(2,1)
    #wait_digital_input(2,1)
def grip_ungrip(g_pick,g_place):
    delta = [0, 0, 50, 0, 0, 0]
    delta2 = [0, 0, 200, 0, 0, 0]
    pick_app = trans(g_pick, delta, DR_BASE, DR_BASE)
    pick_ret = trans(g_pick, delta2, DR_BASE, DR_BASE)
    place_app = trans(g_place, delta, DR_BASE, DR_BASE)
    place_app = trans(g_place, delta, DR_BASE, DR_BASE)
    place_ret = trans(g_place, delta2, DR_BASE, DR_BASE)
    movel(pick_app, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
    movel(g_pick, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
    grip()
    movel(pick_ret, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
    movel(place_app, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
    movel(g_place, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
    ungrip()
    movel(place_ret, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
def grip_spin_ungrip(g_pick,g_place):
    delta = [0, 0, 50, 0, 0, 0]
    delta2 = [0, 0, 100, 0, 0, 0]
    pick_app = trans(g_pick, delta2, DR_BASE, DR_BASE)
    pick_ret = trans(g_pick, delta2, DR_BASE, DR_BASE)
    place_app = trans(g_place, delta, DR_BASE, DR_BASE)
    place_ret = trans(g_place, delta2, DR_BASE, DR_BASE)
    movel(pick_app, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
    movel(g_pick, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
    grip()
    movel(pick_ret, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
    movel(place_app, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
    set_ref_coord(DR_TOOL)
    task_compliance_ctrl(stx=[500, 500, 500, 100, 100, 100])
    fd = [0, 0, 20, 0, 0, 0]
    fctrl_dir= [0, 0, 1, 0, 0, 0]
    set_desired_force(fd, dir=fctrl_dir, mod=DR_FC_MOD_REL)
    while True:
        fck=check_force_condition(DR_AXIS_Z,min=20,ref=DR_BASE)
        if fck==True:
            release_force(time=0)
            release_compliance_ctrl()
            break
    ungrip()
    movel(place_ret, v=100, a=80, ref= DR_BASE, mod=DR_MV_MOD_ABS)
pick_list = [posx(500.6, 149.19, 38.96, 38.24, 179.83, 38.14),
				posx(500.6, 45.56, 38.96, 2.46, -179.93, 2.48),
				posx(397.01, 149.19, 38.96, 121.49, -179.88, 121.65),
				posx(397.01, 45.56, 38.96, 70.93, -179.59, 71.37)]

place_list = [posx(500.6, -3.05, 38.96, 38.24, -179.83, 38.14),
				posx(500.6, -103.53, 38.96, 2.46, -179.93, 2.48),
				posx(397.01, -3.05, 38.96, 121.49, -179.88, 121.65),
				posx(397.01, -103.53, 38.96, 70.93, -179.59, 71.37)]

posx(451.81, -49.97, 30.25, 10.11, -178.5, 10.81)
direction = 1
row = 3
column = 3
stack = 1
thickness = 0
point_offset = [0, 0, 0]
total_count = row * column * stack
Pallet_Pick_Pose =[]
for pallet_index in range(0, total_count):
    Pallet_Pick_Pose.append (get_pattern_point(pick_list[0],pick_list[1],
    							pick_list[2],pick_list[3], pallet_index, 
    							direction, row, column, stack, 
    							thickness, point_offset))

Pallet_Place_Pose =[]
for pallet_index in range(0, total_count):
    Pallet_Place_Pose.append(get_pattern_point(place_list[0],place_list[1],
    							place_list[2],place_list[3], pallet_index, 
    							direction, row, column, stack, 
    							thickness, point_offset))

pallet_cnt=0
def move_to_place():
    ungrip()
    global pallet_cnt
    if pallet_cnt>= 9:
        pallet_cnt= 0
    while pallet_cnt < 9 :
        grip_spin_ungrip(Pallet_Pick_Pose[pallet_cnt],Pallet_Place_Pose[pallet_cnt])
        pallet_cnt += 1
def return_to_place():
    ungrip()
    global pallet_cnt
    if pallet_cnt>= 9:
        pallet_cnt= 0
    while pallet_cnt < 9 :
        grip_spin_ungrip(Pallet_Place_Pose[pallet_cnt], Pallet_Pick_Pose[pallet_cnt])
        pallet_cnt += 1
def main():
    move_to_place()
    return_to_place()
main()
