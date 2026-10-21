import contra.stages.base_plan as bp
R = G["R4"]
ents = R.ents
e9 = ents[9]
print(e9, e9.track[197], e9.track[193])
for px in (48, 60, 73, 88):
    for pose, ys in ((0, 104), (1, 116)):
        c = bp.centre_x(px, pose)
        print(px, pose, c, [(j, c + bp.PELLET_DX[j], bp.in_box(c + bp.PELLET_DX[j], ys, e9.track[197][0], e9.track[197][1], e9.code)) for j in range(5)])
